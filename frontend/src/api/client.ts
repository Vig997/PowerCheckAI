import type {
  AiProjectAnalysis,
  AnalysisResult,
  ComponentItem,
  ExampleProject,
  ParsedProject,
  PowerSource,
  ProjectConfig,
  Regulator,
  ReportResponse,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });
  } catch {
    throw new Error("Could not reach the PowerCheck backend. Make sure the backend server is running.");
  }

  if (!response.ok) {
    const detail = await safeResponseText(response);
    throw new Error(`${response.status} ${response.statusText}: ${detail}`);
  }

  try {
    return response.json() as Promise<T>;
  } catch {
    throw new Error("The backend returned an invalid response.");
  }
}

async function safeResponseText(response: Response): Promise<string> {
  try {
    const text = await response.text();
    return text || "No error details returned.";
  } catch {
    return "No error details returned.";
  }
}

export const api = {
  baseUrl: API_BASE_URL,
  health: () => request<{ status: string }>("/health"),
  components: (category?: string) =>
    request<ComponentItem[]>(category ? `/components?category=${encodeURIComponent(category)}` : "/components"),
  powerSources: () => request<PowerSource[]>("/power-sources"),
  regulators: () => request<Regulator[]>("/regulators"),
  exampleProjects: () => request<ExampleProject[]>("/example-projects"),
  analyzeProjectDescription: (payload: {
    project_name: string;
    description_text: string;
    existing_project_config?: Record<string, unknown>;
  }) =>
    request<AiProjectAnalysis>("/analyze-project-description", {
      method: "POST",
      body: JSON.stringify({
        project_name: payload.project_name,
        description_text: payload.description_text,
        existing_project_config: payload.existing_project_config ?? {},
      }),
    }),
  analyze: (project: ProjectConfig) =>
    request<AnalysisResult>("/analyze", {
      method: "POST",
      body: JSON.stringify({
        selected_microcontroller_id: project.selected_microcontroller_id,
        selected_components: project.selected_components,
        selected_power_source_id: project.selected_power_source_id,
        regulator_id: project.regulator_id,
        settings: project.settings,
      }),
    }),
  parseProjectDescription: (description: string) =>
    request<ParsedProject>("/parse-project-description", {
      method: "POST",
      body: JSON.stringify({ description }),
    }),
  generateReport: (project: ProjectConfig) =>
    request<ReportResponse>("/generate-report", {
      method: "POST",
      body: JSON.stringify({
        project_name: project.project_name,
        selected_microcontroller_id: project.selected_microcontroller_id,
        selected_components: project.selected_components,
        selected_power_source_id: project.selected_power_source_id,
        regulator_id: project.regulator_id,
        settings: project.settings,
      }),
    }),
  estimateNeoPixelCurrent: (led_count: number, brightness_percent: number) =>
    request<{
      led_count: number;
      brightness_percent: number;
      typical_current_mA: number;
      max_current_mA: number;
      recommended_supply_current_mA: number;
    }>("/estimate-neopixel-current", {
      method: "POST",
      body: JSON.stringify({ led_count, brightness_percent }),
    }),
  estimateRegulatorHeat: (payload: {
    regulator_type: "linear" | "buck" | "boost";
    input_voltage: number;
    output_voltage: number;
    output_current_mA: number;
    efficiency?: number;
  }) =>
    request<Record<string, unknown>>("/estimate-regulator-heat", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  estimateBatteryLife: (payload: {
    capacity_mAh: number;
    typical_current_mA: number;
    peak_current_mA?: number;
    efficiency?: number;
  }) =>
    request<Record<string, unknown>>("/estimate-battery-life", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
