from __future__ import annotations

from typing import Any

from .component_extractor import extract_components
from .component_matcher import match_components
from .ee_checker import run_ee_check
from .feature_builder import build_features
from .final_recommendation_engine import build_final_recommendation
from .input_understanding import understand_project_text
from .ml_risk_classifier import classify_project_risk
from .module_result_builder import build_module_results
from .response_quality import apply_quality_gate, quality_check_modules


def analyze_project_description_text(
    project_name: str,
    description_text: str,
    components: list[Any],
    power_sources: list[Any],
    regulators: list[Any],
    existing_project_config: dict[str, Any] | None = None,
) -> dict:
    # Keep the analysis steps simple and readable: read text, match parts,
    # run EE checks, then make the module text a little safer.
    understanding = understand_project_text(description_text)
    cleaned_text = understanding["cleaned_text"]
    extracted = extract_components(cleaned_text)
    matched, unmatched = match_components(extracted, components)
    ee_result = run_ee_check(matched, unmatched, power_sources, regulators)
    features = build_features(matched, ee_result)
    risk = classify_project_risk(features, ee_result["analysis"]["risk"])
    final_recommendation = build_final_recommendation(matched, unmatched, ee_result, risk, features, understanding)
    modules = build_module_results(
        project_name=project_name,
        description_text=cleaned_text,
        matches=matched,
        unmatched=unmatched,
        ee_result=ee_result,
        features=features,
        risk=risk,
        final_recommendation=final_recommendation,
        input_context=understanding,
    )
    quality = quality_check_modules(modules, understanding, unmatched, ee_result, final_recommendation)
    modules = apply_quality_gate(modules, quality)

    return {
        "project_name": project_name,
        "extracted_components": [item.model_dump() for item in extracted],
        "matched_components": matched,
        "unmatched_parts": unmatched,
        "inferred_microcontroller": ee_result["microcontroller"],
        "inferred_power_source": ee_result["power_source"],
        "electrical_analysis": {
            **ee_result["analysis"],
            "selected_components": ee_result["selected_components"],
            "regulator": ee_result.get("regulator"),
            "features": features,
            "input_understanding": understanding,
            "quality_check": quality,
            "existing_project_config": existing_project_config or {},
        },
        "risk_analysis": risk,
        "modules": modules,
        "final_recommendation": final_recommendation,
    }
