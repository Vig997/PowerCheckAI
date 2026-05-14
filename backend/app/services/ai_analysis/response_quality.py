from __future__ import annotations

from difflib import SequenceMatcher

from .utils import clamp


def _similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, left.lower(), right.lower()).ratio()


def _repetition_flags(modules: list) -> list[str]:
    flags = []
    for index, module in enumerate(modules):
        for other in modules[index + 1:]:
            if _similarity(module.details, other.details) > 0.82:
                flags.append(f"{module.title} and {other.title} are too similar")
    return flags


def _missing_unit_flags(modules: list) -> list[str]:
    flags = []
    unit_terms = ("ma", "v", "w", "mah", "ohm")
    for module in modules:
        text = f"{module.summary} {module.details}"
        if any(char.isdigit() for char in text) and not any(unit in text.lower() for unit in unit_terms):
            flags.append(f"{module.title} contains a number without an obvious unit")
    return flags


def quality_check_modules(modules: list, understanding: dict, unmatched: list[dict], ee_result: dict, final_recommendation: dict) -> dict:
    flags: list[str] = []
    flags.extend(_repetition_flags(modules))
    flags.extend(_missing_unit_flags(modules))

    missing = list(understanding.get("missing_information", []))
    unmatched_names = [part.get("raw_text", "unknown part") for part in unmatched if part.get("reason") == "no_database_match"]
    if unmatched_names:
        flags.append("Some parts were not matched to the component database")
        missing.append("datasheet specs for unmatched parts: " + ", ".join(unmatched_names[:5]))

    current = ee_result["analysis"]["current"]
    source = ee_result["power_source"]
    if source.get("max_current_mA", 0) < current.get("peak_total_mA", 0) and final_recommendation.get("verdict") == "Safe to build":
        flags.append("Final verdict was too optimistic for the supply current margin")

    confidence_penalty = 0.05 * len(flags) + 0.04 * len(missing)
    hidden_confidence = round(clamp(0.9 - confidence_penalty, 0.25, 0.95), 2)
    return {
        "hidden_confidence": hidden_confidence,
        "flags": list(dict.fromkeys(flags)),
        "missing_information": list(dict.fromkeys(missing)),
        "passed": hidden_confidence >= 0.55 and not flags[:2],
    }


def apply_quality_gate(modules: list, quality: dict) -> list:
    if quality["hidden_confidence"] >= 0.65 and not quality["missing_information"]:
        return modules

    for module in modules:
        module.confidence = min(module.confidence, quality["hidden_confidence"])
        for item in quality["missing_information"]:
            if item not in module.missing_information:
                module.missing_information.append(item)
        module.missing_information = module.missing_information[:6]
    return modules
