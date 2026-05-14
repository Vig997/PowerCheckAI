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
import type { AiModuleResult, AiProjectAnalysis, AnalysisResult, ComponentItem, ExampleProject, ProjectConfig } from "../types";
import { formatCurrent } from "../utils/format";
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
  analysis,
  onProjectChange,
  onReturnToDashboard,
}: {
  project: ProjectConfig;
  components: ComponentItem[];
  templates: ExampleProject[];
  analysis: AnalysisResult | null;
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
  const safetyScore = moduleAverageScore ?? riskToSafetyScore(analysis?.risk.score);

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
        analysis,
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

function riskToSafetyScore(score?: number | null): number | null {
  return typeof score === "number" ? Math.max(0, Math.min(100, 100 - score)) : null;
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
  analysis,
  boardName,
  componentNames,
  description,
  ready,
}: {
  analysis: AnalysisResult | null;
  boardName?: string;
  componentNames: string[];
  description: string;
  ready: boolean;
}): FeatureInsight[] {
  const status: FeatureInsight["status"] = ready ? "Updated" : "Needs Details";
  const componentSummary = componentNames.length ? componentNames.slice(0, 3).join(", ") : "project loads and sensors";
  const projectContext = description || `Board: ${boardName ?? "not selected"}; Parts: ${componentSummary}.`;
  const typical = analysis ? formatCurrent(analysis.current.typical_total_mA) : "estimated after analysis";
  const peak = analysis ? formatCurrent(analysis.current.peak_total_mA) : "estimated from project details";
  const battery = analysis?.battery_life.message ?? (analysis?.battery_life.runtime_hours_typical ? `${analysis.battery_life.runtime_hours_typical.toFixed(1)} hr typical` : "runtime estimate pending");
  const heat = typeof analysis?.regulator_heat.classification === "string" ? analysis.regulator_heat.classification : "thermal estimate pending";
  const brownout = analysis?.warnings.some((warning) => warning.code.includes("brownout")) ? "brownout warning detected" : "brownout risk estimated from startup load";

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

  return [
    {
      title: "Real-Time Current Profiling",
      icon: Gauge,
      status,
      score: riskToSafetyScore(analysis?.risk.score),
      detail: `Typical draw is ${typical}; peak draw is ${peak}. Context: ${projectContext}`,
      recommendation: "Track normal and peak loads",
      expandedDetail: detailedAnalysis("Real-Time Current Profiling", projectContext, [
        `Typical current estimate: ${typical}.`,
        `Peak current estimate: ${peak}.`,
        "This module separates normal operating current from short high-current events. That matters because many beginner electronics projects look safe at average current but fail when motors start, servos stall, LEDs turn full white, or WiFi radios transmit.",
        "Use the typical current number for runtime planning and thermal expectations. Use the peak current number for choosing the supply, regulator, wiring, and connector ratings.",
        "A safe design should keep the power supply comfortably above peak current. PowerCheck normally expects a margin above the peak, because cheap USB supplies, breadboard rails, and jumper wires can sag under sudden load.",
      ]),
    },
    {
      title: "Brownout Prediction Engine",
      icon: Zap,
      status,
      score: riskToSafetyScore(analysis?.risk.score),
      detail: `${brownout}. Watch for resets during motors, WiFi bursts, servos, or LED startup spikes.`,
      recommendation: "Check voltage sag margin",
      expandedDetail: detailedAnalysis("Brownout Prediction Engine", projectContext, [
        `${brownout}.`,
        "Brownout happens when the supply voltage dips below what the microcontroller needs to run reliably. The project may not look like it is losing power completely; instead the board may reset, freeze, disconnect from WiFi, flicker LEDs, or behave randomly.",
        "The most common causes are motor startup current, servo stall current, LED strip current spikes, pump/solenoid activation, weak batteries, long thin wires, and regulators that cannot respond quickly enough.",
        "For Arduino-style 5V systems, voltage sag near the 5V rail can cause resets or unstable sensor readings. For ESP32 and ESP32-CAM systems, WiFi and camera bursts are especially sensitive because the 3.3V rail needs strong transient current.",
        "A safer build uses a supply with more peak current headroom, separate high-current rails for motors/servos/LEDs, common ground between rails, and bulk capacitance near noisy loads.",
      ]),
    },
    {
      title: "GPIO Protection Analysis",
      icon: ShieldCheck,
      status,
      score: riskToSafetyScore(analysis?.risk.score),
      detail: `GPIO should only signal loads. High-current or inductive devices in ${componentSummary} need driver hardware.`,
      recommendation: "Avoid powering loads from pins",
      expandedDetail: detailedAnalysis("GPIO Protection Analysis", projectContext, [
        "GPIO pins are signal pins, not power supplies. They are meant to output logic levels or read inputs, usually at only a few milliamps.",
        `In this project, pay special attention to ${componentSummary}. Motors, servos, relays, pumps, solenoids, buzzers, fans, and LED strips should not be powered directly from GPIO.`,
        "If a load needs more current than a GPIO pin can safely provide, the pin can overheat, latch up, permanently fail, or make the whole board unstable.",
        "Inductive loads are extra risky because motors, relays, pumps, and solenoids can kick voltage backward when switched off. That back EMF can damage pins unless a driver, flyback diode, MOSFET module, or motor driver handles it.",
        "The safer pattern is: GPIO sends a small control signal, a driver handles load current, the load has its own suitable power rail, and all grounds are connected together.",
      ]),
    },
    {
      title: "Battery Discharge Modeling",
      icon: BatteryCharging,
      status,
      score: riskToSafetyScore(analysis?.risk.score),
      detail: `Battery/runtime model: ${battery}. Larger peak current lowers practical runtime.`,
      recommendation: "Size for worst-case current",
      expandedDetail: detailedAnalysis("Battery Discharge Modeling", projectContext, [
        `Runtime estimate: ${battery}.`,
        "Battery life is not just capacity divided by average current. Real batteries sag under load, lose usable capacity at high current, and may shut down early if protection circuits trip.",
        "Small rectangular 9V batteries are especially poor for motors, servos, LED strips, pumps, and wireless boards. AA packs, LiPo packs, or wall adapters are usually better for beginner robotics and lighting projects.",
        "For runtime, use typical current to estimate normal operation. For reliability, use peak current to check whether the battery can actually supply bursts without voltage collapse.",
        "If the project uses a buck or boost converter, remember that converter efficiency changes battery current. A boost converter stepping 3.7V up to 5V can draw much more input current than the 5V output current suggests.",
      ]),
    },
    {
      title: "Thermal Regulator Analysis",
      icon: Thermometer,
      status,
      score: riskToSafetyScore(analysis?.risk.score),
      detail: `Regulator heat status: ${heat}. Linear regulators need extra attention when voltage drop and current are high.`,
      recommendation: "Prefer buck converters for heat",
      expandedDetail: detailedAnalysis("Thermal Regulator Analysis", projectContext, [
        `Thermal status: ${heat}.`,
        "Linear regulators turn extra voltage into heat. A 12V source feeding a 5V rail at high current can create a lot of heat because the regulator must burn off the 7V difference.",
        "The core estimate is heat in watts = (input voltage - output voltage) x output current. Even one watt can make a small regulator very warm without a heatsink or airflow.",
        "Buck converters are usually better when the input voltage is much higher than the output voltage, or when the project includes motors, servos, pumps, displays, or LED strips.",
        "If the regulator gets too hot, symptoms include voltage droop, random resets, flickering LEDs, unreliable sensors, or the regulator shutting down thermally.",
      ]),
    },
    {
      title: "Component Compatibility Engine",
      icon: CircuitBoard,
      status,
      score: riskToSafetyScore(analysis?.risk.score),
      detail: `Checks voltage, logic-level, current, and driver compatibility for ${componentSummary}.`,
      recommendation: "Verify voltage and signal levels",
      expandedDetail: detailedAnalysis("Component Compatibility Engine", projectContext, [
        `Compatibility focus: ${componentSummary}.`,
        "Compatibility means more than whether a connector fits. PowerCheck looks at voltage range, current draw, logic level, whether a driver is needed, whether the load is inductive, and whether GPIO can safely control it.",
        "Common compatibility mistakes include connecting 5V sensor outputs to ESP32 GPIO, powering 5V-only devices from a weak 3.7V LiPo without a boost converter, skipping motor drivers, and assuming an Arduino 5V pin can power servos or motors.",
        "For each module, verify supply voltage first, then signal voltage, then current, then startup/stall behavior. If any one of those is wrong, the project may still power on but behave unreliably or damage hardware.",
        "A safer design uses level shifting where needed, drivers for loads, regulators sized for current, and external supplies for high-current components.",
      ]),
    },
    {
      title: "Power Tree Visualization",
      icon: GitBranch,
      status,
      score: riskToSafetyScore(analysis?.risk.score),
      detail: `Power should flow from source to regulator/rails, then to controller and loads with shared ground.`,
      recommendation: "Build a clear power tree",
      expandedDetail: detailedAnalysis("Power Tree Visualization", projectContext, [
        "A power tree is the map of how power moves through the project. It starts at the battery, USB supply, or wall adapter and branches through switches, regulators, rails, and loads.",
        "For this project, draw the source first, then any buck/boost/linear regulators, then each rail. Put the microcontroller and sensors on the logic rail, and put high-current loads on their own rail when needed.",
        "Mark current direction, voltage level, and ground connections. This quickly reveals if a part is on the wrong voltage, if a regulator is carrying too much current, or if a motor load is being routed through a fragile board pin.",
        "A good power tree also makes troubleshooting easier: if LEDs flicker, motors slow, or the board resets, you can inspect the affected rail instead of guessing across the whole project.",
      ]),
    },
    {
      title: "Startup Surge Analysis",
      icon: Zap,
      status,
      score: riskToSafetyScore(analysis?.risk.score),
      detail: `Startup surge should be sized above the steady current because motors, servos, pumps, and LEDs can spike briefly.`,
      recommendation: "Reserve peak-current headroom",
      expandedDetail: detailedAnalysis("Startup Surge Analysis", projectContext, [
        "Startup surge is the brief high-current demand that happens when a load first turns on or changes state. It can be much larger than normal running current.",
        "DC motors can draw near stall current at startup. Servos can spike when moving or resisting force. Pumps and solenoids can jump quickly when energized. LED strips can surge when many pixels turn on at high brightness.",
        "These spikes can cause brownouts even when the average current looks safe. That is why the power supply should be sized from peak current plus margin, not only typical current.",
        "Mitigation options include a stronger supply, separate high-current rail, bulk capacitors near loads, lower LED brightness, ramping motor speed with PWM, and avoiding simultaneous startup of many loads.",
      ]),
    },
  ];
}

function detailedAnalysis(title: string, projectContext: string, points: string[]): string {
  return expandedModuleAnalysis({
    detected: projectContext,
    meaning: `${title} is using your project details to check one important power-safety question.`,
    risks: points.slice(0, 2),
    fixes: [
      "Check every component datasheet or product listing for voltage range and current draw.",
      "Confirm the power supply can handle peak current, not only average current.",
      "Keep GPIO pins for signal control and use driver hardware for loads.",
      "Use common ground between the controller and any external power rail.",
    ],
    missing: ["exact part specs if not listed"],
  });
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
  ["Real-Time Current Profiling", Gauge],
  ["Brownout Prediction Engine", Zap],
  ["GPIO Protection Analysis", ShieldCheck],
  ["Battery Discharge Modeling", BatteryCharging],
  ["Thermal Regulator Analysis", Thermometer],
  ["Component Compatibility Engine", CircuitBoard],
  ["Power Tree Visualization", GitBranch],
  ["Startup Surge Analysis", Zap],
];
