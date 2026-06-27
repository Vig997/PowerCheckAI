import type { ProjectConfig } from "../types";

const CURRENT_PROJECT_KEY = "powercheck.currentProject";
const PROJECT_LIBRARY_KEY = "powercheck.projectLibrary";
const RECENT_PROJECTS_KEY = "powercheck.recentProjects";
const THEME_KEY = "powercheck.theme";

function readStorage(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function writeStorage(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch {
    // If storage is blocked or full, keep the app usable for the current session.
  }
}

function normalizeProject(project: Partial<ProjectConfig>): ProjectConfig {
  const fallback = defaultProject();
  return {
    ...fallback,
    ...project,
    project_name: (project.project_name ?? fallback.project_name).trim() || fallback.project_name,
    selected_components: Array.isArray(project.selected_components) ? project.selected_components : [],
    settings: {
      ...fallback.settings,
      ...project.settings,
    },
    updated_at: project.updated_at ?? new Date().toISOString(),
  };
}

function sortProjects(projects: ProjectConfig[]): ProjectConfig[] {
  return [...projects].sort((a, b) => {
    const first = Date.parse(a.updated_at);
    const second = Date.parse(b.updated_at);
    return (Number.isFinite(second) ? second : 0) - (Number.isFinite(first) ? first : 0);
  });
}

function uniqueProjects(projects: ProjectConfig[]): ProjectConfig[] {
  const seen = new Map<string, ProjectConfig>();
  for (const project of sortProjects(projects)) {
    if (!seen.has(project.project_name)) {
      seen.set(project.project_name, project);
    }
  }
  return Array.from(seen.values());
}

export function defaultProject(): ProjectConfig {
  return {
    project_name: "Untitled PowerCheck Project",
    project_summary: "",
    project_description: "",
    project_origin: "custom",
    selected_microcontroller_id: null,
    selected_components: [],
    selected_power_source_id: null,
    regulator_id: null,
    settings: {
      brightness_percent: 60,
      motor_load_level: 0.7,
      servo_activity_level: 0.6,
      wifi_enabled: true,
      camera_enabled: false,
      beginner_mode: true,
      regulated_output_voltage: null,
    },
    updated_at: new Date().toISOString(),
  };
}

export function loadCurrentProject(): ProjectConfig {
  const raw = readStorage(CURRENT_PROJECT_KEY);
  if (!raw) {
    return defaultProject();
  }

  try {
    const parsed = JSON.parse(raw) as Partial<ProjectConfig>;
    return normalizeProject(parsed);
  } catch {
    return defaultProject();
  }
}

export function saveCurrentProject(project: ProjectConfig): void {
  writeStorage(CURRENT_PROJECT_KEY, JSON.stringify({ ...project, updated_at: new Date().toISOString() }));
}

// Kept as "Recent" in the function name so the existing app does not need a
// rewrite. It now stores the full local project library, not a capped list.
export function loadRecentProjects(): ProjectConfig[] {
  const raw = readStorage(PROJECT_LIBRARY_KEY) ?? readStorage(RECENT_PROJECTS_KEY);
  if (!raw) {
    return [];
  }
  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      return [];
    }
    const projects = uniqueProjects(parsed.map((item) => normalizeProject(item as Partial<ProjectConfig>)));
    if (!readStorage(PROJECT_LIBRARY_KEY) && projects.length > 0) {
      writeStorage(PROJECT_LIBRARY_KEY, JSON.stringify(projects));
    }
    return projects;
  } catch {
    return [];
  }
}

export function saveRecentProject(project: ProjectConfig): void {
  const stamped = normalizeProject({ ...project, updated_at: new Date().toISOString() });
  const recent = loadRecentProjects().filter((item) => item.project_name !== stamped.project_name);
  const library = uniqueProjects([stamped, ...recent]);
  writeStorage(PROJECT_LIBRARY_KEY, JSON.stringify(library));
  writeStorage(RECENT_PROJECTS_KEY, JSON.stringify(library));
  saveCurrentProject(stamped);
}

export function deleteRecentProject(projectName: string): void {
  const recent = loadRecentProjects().filter((item) => item.project_name !== projectName);
  writeStorage(PROJECT_LIBRARY_KEY, JSON.stringify(recent));
  writeStorage(RECENT_PROJECTS_KEY, JSON.stringify(recent));
}

export function loadTheme(): "dark" | "light" {
  return readStorage(THEME_KEY) === "light" ? "light" : "dark";
}

export function saveTheme(theme: "dark" | "light"): void {
  writeStorage(THEME_KEY, theme);
}

export async function requestDurableStorage(): Promise<boolean> {
  try {
    if (!navigator.storage?.persist) {
      return false;
    }
    return await navigator.storage.persist();
  } catch {
    return false;
  }
}
