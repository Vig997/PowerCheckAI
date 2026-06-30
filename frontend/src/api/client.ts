import type {
  AiProjectAnalysis,
  ComponentItem,
  PowerSource,
} from "../types";

const API_BASE_URL = "/_/backend";

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
    return text || "The frontend reached /api, but the backend did not return details. Make sure FastAPI is running at http://127.0.0.1:8000.";
  } catch {
    return "The frontend reached /api, but the backend did not return details. Make sure FastAPI is running at http://127.0.0.1:8000.";
  }
}

export const api = {
  baseUrl: API_BASE_URL,
  health: () => request<{ status: string }>("/health"),
  components: (category?: string) =>
    request<ComponentItem[]>(category ? `/components?category=${encodeURIComponent(category)}` : "/components"),
  powerSources: () => request<PowerSource[]>("/power-sources"),
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
};
