from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ComponentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    voltage_min: float | None
    voltage_max: float | None
    typical_current_mA: float
    max_current_mA: float | None
    startup_current_mA: float | None
    stall_current_mA: float | None
    recommended_gpio_current_mA: float | None
    logic_voltage: float | None
    gpio_safe: bool
    requires_driver: bool
    is_high_current: bool
    is_logic_sensitive: bool
    is_inductive: bool
    notes: str | None
    common_warning: str | None
    beginner_tip: str | None


class PowerSourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    voltage: float
    max_current_mA: float
    capacity_mAh: float | None
    internal_resistance_ohm: float
    source_type: str
    notes: str | None
    beginner_tip: str | None


class RegulatorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    regulator_type: str
    input_voltage_min: float | None
    input_voltage_max: float | None
    output_voltage_options: list[float]
    max_current_mA: float
    efficiency: float | None
    notes: str | None
    beginner_tip: str | None


class ExampleProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    components: list[dict]
    power_source: str
    expected_notes: list[str]


class SelectedComponentInput(BaseModel):
    component_id: int
    quantity: int = Field(default=1, ge=1)
    powered_from: Literal["board", "external", "gpio", "same_supply"] = "same_supply"
    rail_voltage: float | None = None


class CustomPowerSourceInput(BaseModel):
    name: str = "Custom Power Source"
    voltage: float = Field(gt=0)
    max_current_mA: float = Field(gt=0)
    capacity_mAh: float | None = Field(default=None, ge=0)
    internal_resistance_ohm: float = Field(default=0.1, ge=0)
    source_type: str = "custom"
    notes: str | None = None
    beginner_tip: str | None = None


class AnalysisSettingsInput(BaseModel):
    brightness_percent: float = Field(default=100, ge=0, le=100)
    motor_load_level: float = Field(default=1.0, ge=0, le=1)
    servo_activity_level: float = Field(default=1.0, ge=0, le=1)
    wifi_enabled: bool = False
    camera_enabled: bool = False
    beginner_mode: bool = True
    regulated_output_voltage: float | None = Field(default=None, gt=0)


class AnalyzeRequest(BaseModel):
    selected_microcontroller_id: int
    selected_components: list[SelectedComponentInput] = Field(default_factory=list)
    selected_power_source_id: int | None = None
    regulator_id: int | None = None
    custom_power_source: CustomPowerSourceInput | None = None
    settings: AnalysisSettingsInput = Field(default_factory=AnalysisSettingsInput)


class ProjectDescriptionRequest(BaseModel):
    description: str = Field(min_length=1)


class GenerateReportRequest(AnalyzeRequest):
    project_name: str = "Untitled PowerCheck Project"


class NeoPixelEstimateRequest(BaseModel):
    led_count: int = Field(ge=1)
    brightness_percent: float = Field(default=100, ge=0, le=100)


class RegulatorHeatEstimateRequest(BaseModel):
    regulator_type: Literal["linear", "buck", "boost"] = "linear"
    input_voltage: float = Field(gt=0)
    output_voltage: float = Field(gt=0)
    output_current_mA: float = Field(ge=0)
    efficiency: float | None = Field(default=None, gt=0, le=1)


class BatteryLifeEstimateRequest(BaseModel):
    capacity_mAh: float = Field(gt=0)
    typical_current_mA: float = Field(gt=0)
    peak_current_mA: float | None = Field(default=None, gt=0)
    efficiency: float = Field(default=1.0, gt=0, le=1)
