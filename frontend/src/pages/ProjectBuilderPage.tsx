import {
  ArrowLeft,
  BatteryCharging,
  CircuitBoard,
  Gauge,
  GitBranch,
  Save,
  ShieldCheck,
  Sparkles,
  Thermometer,
  Trash2,
  X,
  Zap,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";

import { api } from "../api/client";
import type { AiModuleResult, AiProjectAnalysis, ComponentItem, ExampleProject, ProjectConfig } from "../types";
import { defaultProject, deleteRecentProject, loadRecentProjects, saveRecentProject } from "../utils/storage";

const PROJECT_TITLE_LIMIT = 42;
const PROJECT_DESCRIPTION_LIMIT = 1200;

function upsertProjectInPlace(projects: ProjectConfig[], project: ProjectConfig): ProjectConfig[] {
  const exists = projects.some((saved) => saved.project_name === project.project_name);
  if (!exists) {
    return [...projects, project];
  }
  return projects.map((saved) => (saved.project_name === project.project_name ? project : saved));
}

function mergeProjectsInPlace(current: ProjectConfig[], loaded: ProjectConfig[]): ProjectConfig[] {
  const loadedByName = new Map(loaded.map((project) => [project.project_name, project]));
  const merged = current
    .filter((project) => loadedByName.has(project.project_name))
    .map((project) => loadedByName.get(project.project_name) ?? project);
  const existingNames = new Set(merged.map((project) => project.project_name));
  return [...merged, ...loaded.filter((project) => !existingNames.has(project.project_name))];
}

type FeatureInsight = {
  title: string;
  icon: LucideIcon;
  status: "Updated" | "Needs Details";
  score: number | null;
  detail: string;
  recommendation: string;
  expandedDetail: string;
};

export function ProjectBuilderPage({
  project,
  components,
  templates,
  onProjectChange,
  onReturnToDashboard,
}: {
  project: ProjectConfig;
  components: ComponentItem[];
  templates: ExampleProject[];
  onProjectChange: (project: ProjectConfig) => void;
  onReturnToDashboard: () => void;
}) {
  const [descriptionDraft, setDescriptionDraft] = useState(project.project_description ?? "");
  const [builderProjects, setBuilderProjects] = useState<ProjectConfig[]>(() => loadRecentProjects());
  const [expandedInsight, setExpandedInsight] = useState<FeatureInsight | null>(null);
  const [isExpandedClosing, setIsExpandedClosing] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState<AiProjectAnalysis | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [verdictAnimationKey, setVerdictAnimationKey] = useState(0);
  const [saveFlash, setSaveFlash] = useState(false);
  const [projectSwitchAnimationKey, setProjectSwitchAnimationKey] = useState(0);
  const isStarterProject = project.project_origin === "starter";
  const activeTemplate = useMemo(
    () => templates.find((template) => template.name === project.project_name),
    [project.project_name, templates],
  );
  const savedProjectDescription = project.project_description?.trim() ?? "";
  const builderDescription = isStarterProject
    ? savedProjectDescription || activeTemplate?.full_description || ""
    : project.project_description ?? "";
  const projectHeaderDescription = isStarterProject
    ? activeTemplate?.description ?? project.project_description ?? ""
    : project.project_summary ?? "";
  const hasSelectedProject =
    project.project_name !== "Untitled PowerCheck Project" ||
    Boolean(project.project_description?.trim()) ||
    Boolean(project.selected_microcontroller_id) ||
    project.selected_components.length > 0;
  const descriptionReady = isStarterProject || Boolean(builderDescription.trim());
  const moduleAverageScore = aiAnalysis?.modules?.length
    ? Math.round(aiAnalysis.modules.reduce((total, module) => total + module.score, 0) / aiAnalysis.modules.length)
    : null;
  const safetyScore = moduleAverageScore;

  useEffect(() => {
    setDescriptionDraft(builderDescription);
    setAiAnalysis(project.builder_analysis ?? null);
    setAnalysisError(null);
  }, [builderDescription, project.builder_analysis, project.project_name]);

  useEffect(() => {
    setBuilderProjects((current) => mergeProjectsInPlace(current, loadRecentProjects()));
  }, [project.project_name]);

  useEffect(() => {
    if (!hasSelectedProject && builderProjects.length > 0) {
      onProjectChange(builderProjects[0]);
    }
  }, [builderProjects, hasSelectedProject, onProjectChange]);

  const projectTabs = useMemo(() => {
    if (!hasSelectedProject) return builderProjects;
    return upsertProjectInPlace(builderProjects, project);
  }, [builderProjects, hasSelectedProject, project]);

  const selectedParts = useMemo(() => {
    const componentMap = new Map(components.map((component) => [component.id, component]));
    const board = project.selected_microcontroller_id ? componentMap.get(project.selected_microcontroller_id) : null;
    const parts = project.selected_components
      .map((item) => ({ item, component: componentMap.get(item.component_id) }))
      .filter((entry): entry is { item: typeof entry.item; component: ComponentItem } => Boolean(entry.component));
    return { board, parts };
  }, [components, project.selected_components, project.selected_microcontroller_id]);

  const insights = aiAnalysis?.modules?.length
    ? buildAiFeatureInsights(aiAnalysis.modules)
    : buildFeatureInsights({
        boardName: selectedParts.board?.name,
        componentNames: selectedParts.parts.map(({ component, item }) => `${component.name} x${item.quantity}`),
        description: builderDescription,
        ready: descriptionReady,
      });

  function updateProject(patch: Partial<ProjectConfig>) {
    onProjectChange({ ...project, ...patch, updated_at: new Date().toISOString() });
  }

  function switchBuilderProject(nextProject: ProjectConfig) {
    const currentProject = {
      ...project,
      project_description: descriptionDraft.trim().slice(0, PROJECT_DESCRIPTION_LIMIT),
      builder_analysis: aiAnalysis ?? project.builder_analysis ?? null,
      updated_at: new Date().toISOString(),
    };
    if (hasSelectedProject) saveRecentProject(currentProject);
    onProjectChange(nextProject);
    setBuilderProjects((current) => upsertProjectInPlace(current, currentProject));
    setProjectSwitchAnimationKey((current) => current + 1);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function deleteBuilderProject(projectName: string) {
    deleteRecentProject(projectName);
    const remainingProjects = builderProjects.filter((saved) => saved.project_name !== projectName);
    setBuilderProjects(remainingProjects);
    if (projectName === project.project_name) {
      onProjectChange(remainingProjects[0] ?? defaultProject());
    }
  }

  async function submitDescription() {
    const next = {
      ...project,
      project_description: descriptionDraft.trim().slice(0, PROJECT_DESCRIPTION_LIMIT),
      builder_analysis: aiAnalysis ?? project.builder_analysis ?? null,
      updated_at: new Date().toISOString(),
    };
    onProjectChange(next);
    saveRecentProject(next);
    setBuilderProjects((current) => upsertProjectInPlace(current, next));
    setAnalysisLoading(true);
    setAnalysisError(null);
    try {
      const result = await api.analyzeProjectDescription({
        project_name: next.project_name,
        description_text: next.project_description || "Project details were not provided.",
        existing_project_config: next as unknown as Record<string, unknown>,
      });
      const analyzedProject = {
        ...next,
        builder_analysis: result,
        updated_at: new Date().toISOString(),
      };
      setAiAnalysis(result);
      onProjectChange(analyzedProject);
      saveRecentProject(analyzedProject);
      setBuilderProjects((current) => upsertProjectInPlace(current, analyzedProject));
      setVerdictAnimationKey((current) => current + 1);
    } catch (error) {
      setAnalysisError(error instanceof Error ? error.message : "PowerCheck could not analyze this description.");
    } finally {
      setAnalysisLoading(false);
    }
  }

  function saveProject() {
    const next = {
      ...project,
      project_description: descriptionDraft.trim().slice(0, PROJECT_DESCRIPTION_LIMIT),
      builder_analysis: aiAnalysis ?? project.builder_analysis ?? null,
      updated_at: new Date().toISOString(),
    };
    onProjectChange(next);
    saveRecentProject(next);
    setBuilderProjects((current) => upsertProjectInPlace(current, next));
    setSaveFlash(true);
    window.setTimeout(() => setSaveFlash(false), 1400);
  }

  function openExpandedInsight(insight: FeatureInsight) {
    setIsExpandedClosing(false);
    setExpandedInsight(insight);
  }

  function closeExpandedInsight() {
    setIsExpandedClosing(true);
    window.setTimeout(() => {
      setExpandedInsight(null);
      setIsExpandedClosing(false);
    }, 220);
  }

  if (!hasSelectedProject) {
    return (
      <main className="animate-page mx-auto max-w-7xl px-6 py-8">
        <section className="panel flex min-h-96 flex-col items-center justify-center p-8 text-center">
          <CircuitBoard className="h-12 w-12 text-cyan-600 dark:text-cyan-300" />
          <h1 className="mt-5 text-3xl font-black text-slate-950 dark:text-white">Builder Locked</h1>
          <p className="mt-3 max-w-xl text-sm leading-6 text-slate-900 dark:text-slate-300">
            Create a Project Or Move Starter Projects to My Projects to Access Them in The Builder.
          </p>
          <button type="button" className="button-primary mt-6" onClick={onReturnToDashboard}>
            <ArrowLeft className="h-4 w-4" />
            Return to Dashboard
          </button>
        </section>
      </main>
    );
  }

  return (
    <main className="animate-page mx-auto max-w-7xl space-y-6 px-6 py-8">
      <section className="panel p-3">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex flex-wrap gap-2">
            {projectTabs.map((saved) => {
              const isActive = saved.project_name === project.project_name;
              return (
                <div
                  key={`${saved.project_name}-${saved.updated_at}`}
                  className={`flex shrink-0 items-center gap-3 rounded-md border px-3 py-1.5 text-sm font-bold transition duration-200 ease-out hover:-translate-y-0.5 active:scale-95 ${
                    isActive
                      ? "border-cyan-300 bg-cyan-100 text-cyan-900 shadow-soft dark:border-cyan-300 dark:bg-cyan-400/20 dark:text-cyan-100"
                      : "border-slate-200 bg-white/80 text-slate-900 hover:border-cyan-300 hover:text-cyan-700 dark:border-slate-800 dark:bg-slate-900/80 dark:text-slate-300 dark:hover:border-cyan-400/50 dark:hover:text-cyan-200"
                  }`}
                >
                  <button
                    type="button"
                    className="max-w-52 truncate leading-none"
                    onClick={() => {
                      if (!isActive) switchBuilderProject(saved);
                    }}
                    title={saved.project_name}
                  >
                    {saved.project_name}
                  </button>
                  <button
                    type="button"
                    className="inline-flex h-6 w-6 items-center justify-center rounded-md text-red-600 transition hover:bg-red-100 hover:text-red-700 active:scale-95 dark:text-red-300 dark:hover:bg-red-950"
                    onClick={(event) => {
                      event.stopPropagation();
                      deleteBuilderProject(saved.project_name);
                    }}
                    aria-label={`Delete ${saved.project_name}`}
                    title="Delete project"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              );
            })}
          </div>
          <button type="button" className="button-secondary py-1.5" onClick={onReturnToDashboard}>
            <ArrowLeft className="h-4 w-4" />
            Return to Dashboard
          </button>
        </div>
      </section>

      <div key={`${project.project_name}-${projectSwitchAnimationKey}`} className="animate-page space-y-6">
        <section className="panel p-5">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div className="min-w-0 flex-1">
              <input
                className="w-full break-words bg-transparent text-4xl font-black text-slate-950 outline-none [overflow-wrap:anywhere] dark:text-white"
                value={project.project_name}
                maxLength={PROJECT_TITLE_LIMIT}
                onChange={(event) => updateProject({ project_name: event.target.value.slice(0, PROJECT_TITLE_LIMIT) })}
              />
              <p className="mt-3 max-w-3xl break-words text-sm leading-6 text-slate-900 [overflow-wrap:anywhere] dark:text-slate-300">
                {!hasSelectedProject
                  ? "Click on a project from your Dashboard to populate the Builder framework."
                  : projectHeaderDescription || "Add a project description and submit it to populate the validation framework."}
              </p>
            </div>
            <div className="flex shrink-0 flex-wrap gap-2">
              <div className={`inline-flex items-center justify-center rounded-md border px-4 py-2 text-sm font-black ${scoreTone(safetyScore)}`}>
                Score: {safetyScore === null ? "-/100" : `${safetyScore}/100`}
              </div>
              <button type="button" className="button-secondary" onClick={saveProject}>
                <Save className="h-4 w-4" />
                {saveFlash ? "Saved to My Projects" : "Save Project"}
              </button>
            </div>
          </div>
        </section>

        <section className="panel p-5">
          <h2 className="text-2xl font-black text-slate-950 dark:text-white">Project Description Input</h2>
          <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_320px]">
            <label>
              <span className="label">Project description</span>
              <textarea
                className="input mt-2 min-h-36 resize-none"
                value={descriptionDraft}
                maxLength={PROJECT_DESCRIPTION_LIMIT}
                placeholder="Explain your project and write down a detailed list of the parts you are going to use."
                onChange={(event) => setDescriptionDraft(event.target.value.slice(0, PROJECT_DESCRIPTION_LIMIT))}
              />
            </label>
            <div className="rounded-lg border border-cyan-200 bg-cyan-50/70 p-4 dark:border-cyan-400/30 dark:bg-cyan-400/10">
              <Sparkles className="h-5 w-5 text-cyan-600 dark:text-cyan-300" />
              <h3 className="mt-3 font-bold text-slate-950 dark:text-white">Analysis Output</h3>
              <p className="mt-2 text-sm leading-6 text-slate-900 dark:text-slate-300">
                Submitting a description fills each validation module with project-specific guidance. Starter projects are
                pre-filled from their template hardware.
              </p>
              {aiAnalysis?.final_recommendation ? (
                <p
                  key={verdictAnimationKey}
                  className="verdict-card-pop mt-3 break-words rounded-md border border-cyan-200 bg-white/70 p-3 text-xs font-bold leading-5 text-slate-900 dark:border-cyan-400/30 dark:bg-slate-950/60 dark:text-cyan-100"
                >
                  Verdict: {aiAnalysis.final_recommendation.verdict}
                </p>
              ) : null}
              {analysisError ? (
                <p className="mt-3 break-words rounded-md border border-red-200 bg-red-50 p-3 text-xs font-bold leading-5 text-red-900 dark:border-red-400/30 dark:bg-red-950/40 dark:text-red-100">
                  {analysisError}
                </p>
              ) : null}
              <button type="button" className="button-primary mt-4 w-full" onClick={submitDescription} disabled={analysisLoading}>
                {analysisLoading ? "Analyzing..." : "Submit Description"}
              </button>
            </div>
          </div>
        </section>

        <section className="panel p-5">
          <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
            <div>
              <h2 className="text-3xl font-black text-slate-950 dark:text-white">PowerCheck Modules</h2>
            </div>
          </div>
          <div key={`${project.project_name}-modules-${verdictAnimationKey}`} className="animate-page mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {insights.map((insight) => (
              <FeatureBox key={insight.title} insight={insight} onExpand={() => openExpandedInsight(insight)} />
            ))}
          </div>
        </section>
      </div>

      {expandedInsight ? createPortal(
        <div className={`modal-backdrop fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-4 backdrop-blur-sm ${isExpandedClosing ? "modal-backdrop-out" : ""}`}>
          <section className={`project-card-glow modal-panel relative flex max-h-[88vh] w-full max-w-5xl flex-col overflow-hidden rounded-xl border border-cyan-300 bg-white text-slate-950 shadow-2xl dark:border-cyan-400/50 dark:bg-slate-950 dark:text-white ${isExpandedClosing ? "modal-panel-out" : ""}`}>
            <div className="flex items-start justify-between gap-4 border-b border-slate-200 p-5 dark:border-slate-800">
              <div>
                <p className="label">Expanded Module Analysis</p>
                <h2 className="mt-2 text-3xl font-black">{expandedInsight.title}</h2>
              </div>
              <button
                type="button"
                className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-md border border-slate-300 bg-white text-slate-950 transition hover:-translate-y-0.5 hover:border-cyan-300 hover:text-cyan-700 active:scale-95 dark:border-slate-700 dark:bg-slate-900 dark:text-white dark:hover:border-cyan-400 dark:hover:text-cyan-200"
                onClick={closeExpandedInsight}
                aria-label="Close expanded analysis"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="overflow-y-auto p-5">
              <div className="rounded-lg border border-cyan-200 bg-cyan-50/70 p-4 dark:border-cyan-400/30 dark:bg-cyan-400/10">
                <p className="text-sm font-bold text-cyan-800 dark:text-cyan-100">{expandedInsight.recommendation}</p>
                <p className="mt-2 text-sm leading-6 text-slate-900 dark:text-slate-300">{expandedInsight.detail}</p>
              </div>
              <div className="mt-5 whitespace-pre-line rounded-lg border border-slate-200 bg-white/90 p-5 text-sm leading-7 text-slate-900 dark:border-slate-800 dark:bg-slate-900/90 dark:text-slate-200">
                {expandedInsight.expandedDetail}
              </div>
            </div>
          </section>
        </div>,
        document.body,
      ) : null}
    </main>
  );
}

function scoreTone(score: number | null): string {
  if (score === null) {
    return "border-slate-300 bg-white/95 text-slate-700 dark:border-slate-700 dark:bg-slate-900/95 dark:text-slate-300";
  }
  if (score >= 70) {
    return "border-green-300 bg-green-100 text-green-900 dark:border-green-300/40 dark:bg-green-400/15 dark:text-green-100";
  }
  if (score >= 30) {
    return "border-yellow-300 bg-yellow-100 text-yellow-900 dark:border-yellow-300/40 dark:bg-yellow-400/15 dark:text-yellow-100";
  }
  return "border-red-300 bg-red-100 text-red-900 dark:border-red-300/40 dark:bg-red-400/15 dark:text-red-100";
}

function FeatureBox({ insight, onExpand }: { insight: FeatureInsight; onExpand: () => void }) {
  const Icon = insight.icon;
  return (
    <article className="project-card-glow flex h-full min-h-80 flex-col rounded-lg border border-cyan-200 bg-white/90 p-4 transition duration-200 ease-out hover:-translate-y-0.5 dark:border-cyan-400/30 dark:bg-slate-900/90">
      <div className="flex items-start justify-between gap-3">
        <div className="rounded-md bg-cyan-50 p-2 text-cyan-700 dark:bg-cyan-950 dark:text-cyan-200">
          <Icon className="h-5 w-5" />
        </div>
        <div className="flex flex-col items-end gap-1">
          <span
            className={`rounded-full px-2 py-1 text-xs font-bold ${
              insight.status === "Updated"
                ? "bg-green-100 text-green-900 dark:bg-green-400/15 dark:text-green-100"
                : "bg-amber-100 text-amber-900 dark:bg-amber-400/15 dark:text-amber-100"
            }`}
          >
            {insight.status}
          </span>
          <span className={`rounded-full border px-2 py-1 text-xs font-black ${scoreTone(insight.score)}`}>
            {insight.score === null ? "-/100" : `${insight.score}/100`}
          </span>
        </div>
      </div>
      <h3 className="mt-4 min-h-12 font-bold text-slate-950 dark:text-white">{insight.title}</h3>
      <p className="mt-3 min-h-24 overflow-hidden text-sm leading-6 text-slate-900 [display:-webkit-box] [-webkit-box-orient:vertical] [-webkit-line-clamp:4] dark:text-slate-300">
        {insight.detail}
      </p>
      <div className="mt-auto pt-4">
        <p className="min-h-10 overflow-hidden break-words text-xs font-bold uppercase leading-5 tracking-normal text-cyan-700 [display:-webkit-box] [-webkit-box-orient:vertical] [-webkit-line-clamp:2] dark:text-cyan-300">
          {insight.recommendation}
        </p>
        <button type="button" className="button-secondary mt-3 w-full text-xs" onClick={onExpand}>
          Click to Expand
        </button>
      </div>
    </article>
  );
}

function buildAiFeatureInsights(modules: AiModuleResult[]): FeatureInsight[] {
  return modules.map((module) => ({
    title: module.title,
    icon: iconForModule(module.title),
    status: "Updated",
    score: module.score,
    detail: module.summary,
    recommendation: module.fixes[0] ?? `${module.severity} severity`,
    expandedDetail: expandedModuleAnalysis({
      detected: module.details,
      meaning: module.summary,
      risks: module.symptoms,
      fixes: module.fixes,
      missing: module.missing_information ?? [],
    }),
  }));
}

function iconForModule(title: string): LucideIcon {
  const match = featureShells.find(([featureTitle]) => featureTitle === title);
  return match?.[1] ?? Sparkles;
}

function buildFeatureInsights({
  boardName,
  componentNames,
  description,
  ready,
}: {
  boardName?: string;
  componentNames: string[];
  description: string;
  ready: boolean;
}): FeatureInsight[] {
  const status: FeatureInsight["status"] = "Needs Details";
  const componentSummary = componentNames.length ? componentNames.slice(0, 3).join(", ") : "project loads and sensors";
  const projectContext = description || `Board: ${boardName ?? "not selected"}; Parts: ${componentSummary}.`;

  if (!ready) {
    return featureShells.map(([title, icon]) => ({
      title,
      icon,
      status,
      score: null,
      detail: "Submit a project description so PowerCheck can generate this module for your design.",
      recommendation: "Awaiting project details",
      expandedDetail: expandedModuleAnalysis({
        detected: "No confirmed project parts have been submitted yet.",
        meaning: "This box needs your project idea and parts list before it can give useful advice.",
        risks: ["Without the parts list, PowerCheck cannot tell which pieces need more power, safer wiring, or a stronger supply."],
        fixes: [
          "Explain what your build does.",
          "List the microcontroller, sensors, motors, servos, LEDs, displays, drivers, regulators, and power source.",
          "Include voltage, current, or battery capacity when you know it.",
        ],
        missing: ["project description", "parts list", "power source"],
      }),
    }));
  }

  return featureShells.map(([title, icon]) => ({
    title,
    icon,
    status,
    score: null,
    detail: `Ready to analyze ${componentSummary}. Press Submit Description to calculate this module from the project text.`,
    recommendation: "Submit description",
    expandedDetail: expandedModuleAnalysis({
      detected: projectContext,
      meaning: `${title} will be filled from the backend analysis after you submit the project description.`,
      risks: [
        "These values are intentionally not guessed before analysis runs.",
        "Submit the description so PowerCheck can extract parts, check current, and generate project-specific advice.",
      ],
      fixes: ["Press Submit Description after listing the project goal, parts, and power source."],
      missing: ["backend analysis result"],
    }),
  }));
}

function expandedModuleAnalysis({
  detected,
  meaning,
  risks,
  fixes,
  missing,
}: {
  detected: string;
  meaning: string;
  risks: string[];
  fixes: string[];
  missing: string[];
}): string {
  return [
    "What Was Detected",
    detected,
    "",
    "What This Means",
    meaning,
    "",
    "Risks or Concerns",
    ...(risks.length ? risks.map((risk) => `- ${risk}`) : ["- No major problem was found from the current project text."]),
    "",
    "Recommended Fixes",
    ...(fixes.length ? fixes.map((fix) => `- ${fix}`) : ["- Check the part specs and leave extra room in your power supply before wiring."]),
    "",
    "Missing Information",
    ...(missing.length ? missing.map((item) => `- ${item}`) : ["- No major missing information was found."]),
  ].join("\n");
}

const featureShells: Array<[string, LucideIcon]> = [
  ["Current Draw Check", Gauge],
  ["Board Reset Risk", Zap],
  ["GPIO Pin Safety", ShieldCheck],
  ["Battery Life Estimate", BatteryCharging],
  ["Regulator Heat Check", Thermometer],
  ["Parts Compatibility Check", CircuitBoard],
  ["Power Path Map", GitBranch],
  ["Startup Spike Check", Zap],
];
