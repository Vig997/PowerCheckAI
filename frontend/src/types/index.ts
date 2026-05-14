export type PoweredFrom = "board" | "external" | "gpio" | "same_supply";
export type RiskLabel = "Safe" | "Borderline" | "Unsafe";
export type Page = "landing" | "builder" | "dashboard";

export interface ComponentItem {
  id: number;
  name: string;
  category: string;
  voltage_min: number | null;
  voltage_max: number | null;
  typical_current_mA: number;
  max_current_mA: number | null;
  startup_current_mA: number | null;
  stall_current_mA: number | null;
  recommended_gpio_current_mA: number | null;
  logic_voltage: number | null;
  gpio_safe: boolean;
  requires_driver: boolean;
  is_high_current: boolean;
  is_logic_sensitive: boolean;
  is_inductive: boolean;
  notes: string | null;
  common_warning: string | null;
  beginner_tip: string | null;
}

export interface PowerSource {
  id: number;
  name: string;
  voltage: number;
  max_current_mA: number;
  capacity_mAh: number | null;
  internal_resistance_ohm: number;
  source_type: string;
  notes: string | null;
  beginner_tip: string | null;
}

export interface Regulator {
  id: number;
  name: string;
  regulator_type: "linear" | "buck" | "boost" | string;
  input_voltage_min: number | null;
  input_voltage_max: number | null;
  output_voltage_options: number[];
  max_current_mA: number;
  efficiency: number | null;
  notes: string | null;
  beginner_tip: string | null;
}

export interface ExampleProject {
  id: number;
  name: string;
  description: string;
  full_description?: string;
  components: Array<{ component_id: number; quantity: number }>;
  power_source: string;
  expected_notes: string[];
}

export interface SelectedComponent {
  component_id: number;
  quantity: number;
  powered_from: PoweredFrom;
  rail_voltage?: number | null;
}

export interface ProjectSettings {
  brightness_percent: number;
  motor_load_level: number;
  servo_activity_level: number;
  wifi_enabled: boolean;
  camera_enabled: boolean;
  beginner_mode: boolean;
  regulated_output_voltage?: number | null;
}

export interface ProjectConfig {
  project_name: string;
  project_summary?: string;
  project_description?: string;
  project_origin?: "custom" | "starter";
  builder_analysis?: AiProjectAnalysis | null;
  selected_microcontroller_id: number | null;
  selected_components: SelectedComponent[];
  selected_power_source_id: number | null;
  regulator_id: number | null;
  settings: ProjectSettings;
  updated_at: string;
}

export interface WarningItem {
  code: string;
  severity: "critical" | "warning" | "suggestion" | string;
  component: string | null;
  issue: string;
  why_it_matters: string;
  likely_symptoms: string[];
  recommended_fix: string | null;
}

export interface TopFix {
  code: string;
  fix: string;
  difficulty: "Easy" | "Medium" | "Advanced" | string;
  cost: "$" | "$$" | "$$$" | string;
}

export interface AnalysisResult {
  current: {
    typical_total_mA: number;
    peak_total_mA: number;
    recommended_current_mA: number;
    current_margin_mA: number;
    current_margin_percent: number;
    line_items: Array<{
      name: string;
      quantity: number;
      typical_mA: number;
      peak_mA: number;
      powered_from: string;
    }>;
  };
  battery_life: {
    is_wall_powered: boolean;
    runtime_hours_typical: number | null;
    runtime_hours_worst: number | null;
    message: string | null;
  };
  regulator_heat: Record<string, unknown>;
  warnings: WarningItem[];
  warning_summary: Record<string, number>;
  risk: {
    score: number;
    label: RiskLabel;
  };
  regulated_voltage: number;
  selected_microcontroller: ComponentItem;
  selected_components: Array<{
    component: ComponentItem;
    quantity: number;
    powered_from: PoweredFrom;
    rail_voltage?: number | null;
  }>;
  power_source: PowerSource;
  regulator: Regulator | null;
  explanations: WarningItem[];
  top_fixes: TopFix[];
}

export interface AiModuleResult {
  title: string;
  status: "safe" | "warning" | "danger" | "info";
  score: number;
  severity: "low" | "medium" | "high";
  summary: string;
  details: string;
  symptoms: string[];
  fixes: string[];
  missing_information?: string[];
  formulas: string[];
  confidence: number;
}

export interface AiProjectAnalysis {
  project_name: string;
  extracted_components: Array<Record<string, unknown>>;
  matched_components: Array<Record<string, unknown>>;
  unmatched_parts: Array<Record<string, unknown>>;
  inferred_microcontroller: Record<string, unknown> | null;
  inferred_power_source: Record<string, unknown> | null;
  electrical_analysis: Record<string, unknown>;
  risk_analysis: {
    score: number;
    label: RiskLabel;
    confidence: number;
    model: string;
  };
  modules: AiModuleResult[];
  final_recommendation: {
    verdict: string;
    overall_score: number;
    risk_score?: number;
    summary: string;
    parts_to_keep: string[];
    parts_to_add: string[];
    parts_to_replace: string[];
    parts_to_remove: string[];
    missing_information: string[];
    highest_priority_fix: string;
    beginner_build_advice: string;
    confidence: number;
  };
}

export interface ParsedProject {
  description: string;
  selected_microcontroller: { component_id: number; name: string; quantity: number } | null;
  selected_components: Array<{ component_id: number; name: string; quantity: number }>;
}

export interface ReportResponse {
  project_name: string;
  report: string;
  risk: {
    score: number;
    label: RiskLabel;
  };
}
