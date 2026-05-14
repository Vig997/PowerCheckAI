from typing import Any, Literal

from pydantic import BaseModel, Field


class AnalyzeProjectDescriptionRequest(BaseModel):
    project_name: str = "Untitled PowerCheck Project"
    description_text: str = Field(min_length=1)
    existing_project_config: dict[str, Any] = Field(default_factory=dict)


class ExtractedComponent(BaseModel):
    raw_text: str
    normalized_name: str
    category: str
    quantity: int = 1
    voltage: float | None = None
    current_mA: float | None = None
    capacity_mAh: float | None = None
    confidence: float = 0.7


class ModuleResult(BaseModel):
    title: str
    status: Literal["safe", "warning", "danger", "info"]
    score: int
    severity: Literal["low", "medium", "high"]
    summary: str
    details: str
    symptoms: list[str] = Field(default_factory=list)
    fixes: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    formulas: list[str] = Field(default_factory=list)
    confidence: float = 0.75


class AnalyzeProjectDescriptionResponse(BaseModel):
    project_name: str
    extracted_components: list[dict[str, Any]]
    matched_components: list[dict[str, Any]]
    unmatched_parts: list[dict[str, Any]]
    inferred_microcontroller: dict[str, Any] | None
    inferred_power_source: dict[str, Any] | None
    electrical_analysis: dict[str, Any]
    risk_analysis: dict[str, Any]
    modules: list[ModuleResult]
    final_recommendation: dict[str, Any]
