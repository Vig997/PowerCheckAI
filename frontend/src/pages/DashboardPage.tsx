import { FilePlus2, Trash2 } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

import type { ExampleProject, PowerSource, ProjectConfig } from "../types";
import { defaultProject, deleteRecentProject, loadRecentProjects, saveRecentProject } from "../utils/storage";

const PROJECT_TITLE_LIMIT = 42;
const PROJECT_DESCRIPTION_LIMIT = 150;

export function DashboardPage({
  project,
  templates,
  powerSources,
  focusSection,
  focusKey,
  onProjectChange,
}: {
  project: ProjectConfig;
  templates: ExampleProject[];
  powerSources: PowerSource[];
  focusSection: "my-projects" | "example-projects" | null;
  focusKey: number;
  onProjectChange: (project: ProjectConfig) => void;
}) {
  const [savedProjects, setSavedProjects] = useState<ProjectConfig[]>(() => loadRecentProjects());
  const [deletingProjectNames, setDeletingProjectNames] = useState<string[]>([]);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectDescription, setNewProjectDescription] = useState("");
  const [addedProjectName, setAddedProjectName] = useState<string | null>(null);
  const [movingTemplateIds, setMovingTemplateIds] = useState<number[]>([]);
  const [movingProjectNames, setMovingProjectNames] = useState<string[]>([]);
  const myProjectsRef = useRef<HTMLElement>(null);
  const exampleProjectsRef = useRef<HTMLElement>(null);
  const availableTemplates = templates.filter((template) => !savedProjects.some((saved) => saved.project_name === template.name)).slice(0, 10);

  useEffect(() => {
    window.setTimeout(() => {
      if (focusSection === "example-projects") {
        const sectionTop = exampleProjectsRef.current?.getBoundingClientRect().top ?? 0;
        window.scrollTo({ top: window.scrollY + sectionTop - 112, behavior: "smooth" });
        return;
      }
      window.scrollTo({ top: 0, behavior: "smooth" });
    }, 30);
  }, [focusSection, focusKey]);

  function refreshSavedProjects() {
    setSavedProjects(loadRecentProjects());
  }

  function createBlankProject() {
    const trimmedName = newProjectName.trim();
    const next = {
      ...defaultProject(),
      project_name: (trimmedName || `PowerCheck Project ${savedProjects.length + 1}`).slice(0, PROJECT_TITLE_LIMIT),
      project_summary: newProjectDescription.trim().slice(0, PROJECT_DESCRIPTION_LIMIT),
      project_description: "",
      project_origin: "custom" as const,
    };
    saveRecentProject(next);
    onProjectChange(next);
    refreshSavedProjects();
    setAddedProjectName(next.project_name);
    setNewProjectName("");
    setNewProjectDescription("");
    setIsCreateOpen(false);
    window.setTimeout(() => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }, 30);
    window.setTimeout(() => setAddedProjectName(null), 420);
  }

  function saveExampleToMyProjects(template: ExampleProject) {
    if (movingTemplateIds.includes(template.id)) return;
    setMovingTemplateIds((current) => [...current, template.id]);
    window.setTimeout(() => {
      saveExampleToMyProjectsNow(template);
      setMovingTemplateIds((current) => current.filter((id) => id !== template.id));
    }, 340);
  }

  function saveExampleToMyProjectsNow(template: ExampleProject) {
    const powerSource = powerSources.find((source) => source.name === template.power_source);
    const next: ProjectConfig = {
      ...defaultProject(),
      project_name: template.name,
      project_description: template.full_description ?? template.description,
      project_origin: "starter",
      selected_microcontroller_id: template.components[0]?.component_id ?? null,
      selected_components: template.components.slice(1).map((item) => ({
        component_id: item.component_id,
        quantity: item.quantity,
        powered_from: "same_supply",
        rail_voltage: null,
      })),
      selected_power_source_id: powerSource?.id ?? null,
      updated_at: new Date().toISOString(),
    };
    saveRecentProject(next);
    refreshSavedProjects();
    setAddedProjectName(next.project_name);
    window.setTimeout(() => setAddedProjectName(null), 420);
  }

  function moveProjectToStarter(projectName: string) {
    if (movingProjectNames.includes(projectName)) return;
    setMovingProjectNames((current) => [...current, projectName]);
    window.setTimeout(() => {
      deleteRecentProject(projectName);
      if (project.project_name === projectName) {
        onProjectChange(defaultProject());
      }
      refreshSavedProjects();
      setMovingProjectNames((current) => current.filter((name) => name !== projectName));
    }, 340);
  }

  function deleteProject(projectName: string) {
    if (deletingProjectNames.includes(projectName)) return;
    setDeletingProjectNames((current) => [...current, projectName]);
    window.setTimeout(() => {
      deleteRecentProject(projectName);
      if (project.project_name === projectName) {
        onProjectChange(defaultProject());
      }
      refreshSavedProjects();
      setDeletingProjectNames((current) => current.filter((name) => name !== projectName));
    }, 260);
  }

  const projectHub = (
    <>
      <section
        ref={myProjectsRef}
        className="panel p-5"
      >
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 className="mt-2 text-3xl font-black text-slate-950 dark:text-white">My Projects</h1>
            <p className="mt-2 text-sm text-slate-900 dark:text-slate-300">
              Create Projects and Move Projects Here to Access Them in The Builder. Projects stay saved on this browser until you delete them.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="button" className="button-primary" onClick={() => setIsCreateOpen(true)}>
              <FilePlus2 className="h-4 w-4" /> Add Project
            </button>
          </div>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {savedProjects.length ? (
            savedProjects.map((saved) => {
              const matchingTemplate = templates.find((template) => template.name === saved.project_name);
              const isStarterSaved = saved.project_origin === "starter" || Boolean(matchingTemplate);
              const previewDescription = matchingTemplate?.description ?? saved.project_summary ?? saved.project_description ?? "No description added yet.";
              return (
                <article
                  key={`${saved.project_name}-${saved.updated_at}`}
                  className={`project-card-glow rounded-lg border border-cyan-200 bg-white/80 p-4 shadow-sm transition duration-200 ease-out dark:border-cyan-400/30 dark:bg-slate-900/80 ${
                    deletingProjectNames.includes(saved.project_name) ? "project-card-delete" : ""
                  } ${movingProjectNames.includes(saved.project_name) ? "project-card-move-out" : ""
                  } ${addedProjectName === saved.project_name ? "project-card-enter" : ""}`}
                >
                  <div className="block w-full text-left">
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <h3 className="break-words font-bold text-slate-950 dark:text-white [overflow-wrap:anywhere]">{saved.project_name}</h3>
                      {!isStarterSaved ? (
                        <span className="rounded-full border border-cyan-300 bg-cyan-50 px-2 py-1 text-[10px] font-black uppercase tracking-normal text-cyan-800 dark:border-cyan-400/40 dark:bg-cyan-400/10 dark:text-cyan-200">
                          My Project
                        </span>
                      ) : null}
                    </div>
                    <p className="mt-2 break-words text-sm leading-6 text-slate-900 dark:text-slate-300 [overflow-wrap:anywhere]">
                      {previewDescription}
                    </p>
                  </div>
                  <div className="mt-4 flex flex-wrap items-center gap-3">
                    {isStarterSaved ? (
                      <button type="button" className="button-secondary text-xs" onClick={() => moveProjectToStarter(saved.project_name)}>
                        Move to Starter Projects
                      </button>
                    ) : null}
                    <button type="button" className="inline-flex items-center gap-2 text-sm font-semibold text-red-700 transition hover:text-red-500 dark:text-red-300" onClick={() => deleteProject(saved.project_name)}>
                      <Trash2 className="h-4 w-4" /> Delete
                    </button>
                  </div>
                </article>
              );
            })
          ) : (
            <div className="rounded-lg border border-dashed border-cyan-300 bg-cyan-50/80 p-5 text-sm font-semibold text-slate-950 dark:border-cyan-400/50 dark:bg-cyan-400/10 dark:text-cyan-100 md:col-span-2 xl:col-span-3">
              Add a new project or move a starter project here.
            </div>
          )}
        </div>
      </section>

      {isCreateOpen ? createPortal(
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-200/70 p-4 backdrop-blur-sm dark:bg-slate-950/70">
          <section className="create-project-modal w-full max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-soft dark:border-cyan-400/30 dark:bg-slate-950">
            <h2 className="text-2xl font-black text-slate-950 dark:text-white">Create New Project</h2>
            <p className="mt-2 text-sm text-slate-900 dark:text-slate-300">Name your project now. You can open it in Builder after it appears in My Projects.</p>
            <label className="mt-5 block">
              <span className="label">Project name</span>
              <input
                className="input mt-2"
                autoFocus
                value={newProjectName}
                maxLength={PROJECT_TITLE_LIMIT}
                placeholder="ESP32 Robot Car"
                onChange={(event) => setNewProjectName(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") createBlankProject();
                  if (event.key === "Escape") setIsCreateOpen(false);
                }}
              />
            </label>
            <label className="mt-4 block">
              <span className="label">Description</span>
              <textarea
                className="input mt-2 min-h-24 resize-none"
                value={newProjectDescription}
                maxLength={PROJECT_DESCRIPTION_LIMIT}
                placeholder="Shortly describe what this project will build or test."
                onChange={(event) => setNewProjectDescription(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Escape") setIsCreateOpen(false);
                }}
              />
            </label>
            <div className="mt-5 flex justify-end gap-2">
              <button type="button" className="button-secondary" onClick={() => setIsCreateOpen(false)}>
                Cancel
              </button>
              <button type="button" className="button-primary" onClick={createBlankProject}>
                Create Project
              </button>
            </div>
          </section>
        </div>,
        document.body,
      ) : null}

      <section
        ref={exampleProjectsRef}
        className="panel p-5"
      >
        <div className="flex flex-col gap-2 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h2 className="text-3xl font-black text-slate-950 dark:text-white">Starter Projects</h2>
            <p className="mt-2 text-sm text-slate-900 dark:text-slate-300">Move Starter Projects to My Projects to Access Them in The Builder.</p>
          </div>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {availableTemplates.length ? availableTemplates.map((template) => (
            <article
              key={template.id}
              className={`project-card-glow flex flex-col rounded-lg border border-cyan-200 bg-white/80 p-4 text-left shadow-sm transition duration-200 ease-out hover:-translate-y-0.5 hover:border-cyan-400 hover:text-cyan-700 dark:border-cyan-400/30 dark:bg-slate-900/80 dark:hover:text-cyan-300 ${
                movingTemplateIds.includes(template.id) ? "project-card-move-out" : ""
              }`}
            >
              <h3 className="font-bold text-slate-950 dark:text-white">{template.name}</h3>
              <p className="mt-2 flex-1 text-sm leading-6 text-slate-900 dark:text-slate-300">{template.description}</p>
              <button
                type="button"
                className="button-secondary mt-auto text-xs active:scale-100"
                onClick={(event) => {
                  event.stopPropagation();
                  saveExampleToMyProjects(template);
                }}
              >
                Move to My Projects
              </button>
            </article>
          )) : (
            <div className="rounded-lg border border-dashed border-cyan-300 bg-cyan-50/80 p-5 text-sm font-semibold text-slate-950 dark:border-cyan-400/50 dark:bg-cyan-400/10 dark:text-cyan-100 md:col-span-2 xl:col-span-3">
              All starter projects are currently in My Projects. Move one back here to return it.
            </div>
          )}
        </div>
      </section>
    </>
  );

  return (
    <main className="animate-page mx-auto max-w-7xl space-y-6 px-6 py-8">
      {projectHub}
    </main>
  );
}
