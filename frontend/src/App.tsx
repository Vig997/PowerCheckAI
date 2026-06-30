import { Activity, AlertCircle, Cpu, Gauge, Home, Loader2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { api } from "./api/client";
import { DarkModeToggle } from "./components/DarkModeToggle";
import { starterProjects } from "./data/starterProjects";
import { DashboardPage } from "./pages/DashboardPage";
import { LandingPage } from "./pages/LandingPage";
import { ProjectBuilderPage } from "./pages/ProjectBuilderPage";
import type { ComponentItem, ExampleProject, Page, PowerSource, ProjectConfig } from "./types";
import {
  loadCatalogCache,
  loadCurrentProject,
  loadTheme,
  requestDurableStorage,
  saveCatalogCache,
  saveCurrentProject,
  saveTheme,
} from "./utils/storage";

function App() {
  const [catalogCache] = useState(() => loadCatalogCache());
  const [page, setPage] = useState<Page>("landing");
  const [theme, setTheme] = useState<"dark" | "light">(() => loadTheme());
  const [project, setProject] = useState<ProjectConfig>(() => loadCurrentProject());
  const [components, setComponents] = useState<ComponentItem[]>(() => catalogCache.components ?? []);
  const [powerSources, setPowerSources] = useState<PowerSource[]>(() => catalogCache.powerSources ?? []);
  const [templates] = useState<ExampleProject[]>(starterProjects);
  const [dashboardSection, setDashboardSection] = useState<"my-projects" | "example-projects" | null>(null);
  const [dashboardFocusKey, setDashboardFocusKey] = useState(0);
  const [landingKey, setLandingKey] = useState(0);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    saveTheme(theme);
  }, [theme]);

  useEffect(() => {
    void requestDurableStorage();
  }, []);

  useEffect(() => {
    saveCurrentProject(project);
  }, [project]);

  useEffect(() => {
    let alive = true;
    async function loadData() {
      setCatalogLoading(true);
      const [componentResult, sourceResult] = await Promise.allSettled([
        api.components(),
        api.powerSources(),
      ]);
      if (!alive) return;

      if (componentResult.status === "fulfilled") {
        setComponents(componentResult.value);
      }
      if (sourceResult.status === "fulfilled") {
        setPowerSources(sourceResult.value);
      }
      if (componentResult.status === "fulfilled" && sourceResult.status === "fulfilled") {
        saveCatalogCache(componentResult.value, sourceResult.value);
        setError(null);
      } else {
        const failed = componentResult.status === "rejected" ? componentResult.reason : sourceResult.status === "rejected" ? sourceResult.reason : null;
        setError(failed instanceof Error ? failed.message : "PowerCheck could not refresh the component catalog.");
      }
      setCatalogLoading(false);
    }
    loadData();
    return () => {
      alive = false;
    };
  }, []);

  const navItems = useMemo(
    () => [
      ["landing", "Home", Home],
      ["dashboard", "Dashboard", Gauge],
      ["builder", "Builder", Cpu],
    ] as const,
    [],
  );

  function updateProject(next: ProjectConfig) {
    setProject(next);
  }

  function openDashboard(section: "my-projects" | "example-projects") {
    setDashboardSection(section);
    setDashboardFocusKey((current) => current + 1);
    setPage("dashboard");
  }

  function openHome() {
    setLandingKey((current) => current + 1);
    setPage("landing");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <div className="min-h-screen text-slate-900 dark:text-slate-100">
      <header className="nav-scroll-mask sticky top-0 z-40 px-4 py-4 will-change-transform sm:px-6">
        <div className="relative z-10 mx-auto flex max-w-7xl items-center justify-between gap-5 rounded-xl border border-slate-200 bg-white/95 px-5 py-3 shadow-soft backdrop-blur-sm dark-surface-shadow dark:border-slate-800 dark:bg-slate-950/95 sm:px-6">
          <button
            type="button"
            className="flex min-w-0 shrink-0 items-center gap-3 rounded-md px-2 py-1 text-left transition duration-200 ease-out hover:-translate-y-0.5 hover:text-cyan-600 active:translate-y-0 active:scale-95 dark:hover:text-cyan-300"
            onClick={openHome}
            aria-label="Go to home"
            title="Go to home"
          >
            <div className="rounded-md border border-cyan-200 bg-cyan-100 p-3 text-slate-950 dark:border-cyan-400 dark:bg-cyan-400 dark:text-slate-950">
              <Activity className="h-6 w-6" />
            </div>
            <div>
              <div className="text-2xl font-black leading-tight tracking-normal">PowerCheck AI</div>
            </div>
          </button>
          <div className="ml-auto flex min-w-0 items-center justify-end gap-2">
            <nav className="flex min-w-0 items-center justify-end gap-1 overflow-x-auto">
              {navItems.map(([id, label, Icon]) => (
                <button
                  key={id}
                  type="button"
                  className={`inline-flex shrink-0 items-center gap-2 rounded-md px-3 py-2.5 text-base font-semibold transition duration-200 ease-out hover:-translate-y-0.5 hover:text-cyan-600 active:translate-y-0 active:scale-95 dark:hover:text-cyan-300 lg:px-4 ${page === id ? "text-cyan-600 dark:text-cyan-300" : "text-slate-900 dark:text-slate-300"}`}
                  onClick={() => {
                    if (id === "landing") {
                      openHome();
                      return;
                    }
                    setPage(id);
                  }}
                >
                  <Icon className="h-5 w-5" />
                  <span className="hidden sm:inline">{label}</span>
                </button>
              ))}
            </nav>
            <DarkModeToggle theme={theme} onToggle={() => setTheme(theme === "dark" ? "light" : "dark")} />
          </div>
        </div>
      </header>

      {error ? (
        <div className="mx-auto mt-4 max-w-7xl px-6">
          <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-100">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <div>
              <b>Backend connection issue</b>
              <div className="mt-1">{error}</div>
              <div className="mt-1">Expected API base URL: {api.baseUrl}</div>
            </div>
          </div>
        </div>
      ) : null}

      {catalogLoading && page !== "landing" && !components.length ? (
        <div className="mx-auto mt-4 max-w-7xl px-6">
          <div className="flex items-center gap-3 rounded-lg border border-cyan-200 bg-cyan-50/90 p-3 text-sm font-semibold text-slate-950 shadow-sm dark:border-cyan-400/30 dark:bg-cyan-400/10 dark:text-cyan-100">
            <Loader2 className="h-4 w-4 animate-spin text-cyan-600 dark:text-cyan-300" />
            Loading component catalog in the background...
          </div>
        </div>
      ) : null}

      {page === "landing" ? (
        <LandingPage
          key={landingKey}
          templates={templates}
          onNavigate={(nextPage) => {
            if (nextPage === "builder") {
              openDashboard("my-projects");
              return;
            }
            setPage(nextPage);
          }}
          onTryExample={() => openDashboard("example-projects")}
        />
      ) : null}
      {page === "builder" ? (
        <ProjectBuilderPage
          project={project}
          components={components}
          templates={templates}
          onProjectChange={updateProject}
          onReturnToDashboard={() => openDashboard("my-projects")}
        />
      ) : null}
      {page === "dashboard" ? (
        <DashboardPage
          project={project}
          templates={templates}
          powerSources={powerSources}
          focusSection={dashboardSection}
          focusKey={dashboardFocusKey}
          onProjectChange={updateProject}
        />
      ) : null}
      <footer className="px-6 py-6 text-center text-xs font-semibold text-slate-900 dark:text-slate-400">
        2026 | Vignesh Balaji
      </footer>
    </div>
  );
}

export default App;
