from __future__ import annotations

import re

from .regex_patterns import (
    BUDGET_RE,
    CAPACITANCE_RE,
    CAPACITY_RE,
    CURRENT_RE,
    DEADLINE_RE,
    DIMENSION_RE,
    POWER_RE,
    RESISTANCE_RE,
    VOLTAGE_RE,
)


INTENT_KEYWORDS: dict[str, list[str]] = {
    "calculation_request": ["calculate", "estimate", "how much", "runtime", "current draw", "battery life", "heat"],
    "design_recommendation": ["recommend", "should i", "what parts", "choose", "replace", "better"],
    "debugging_request": ["not working", "reset", "flicker", "jitter", "disconnect", "overheat", "brownout", "unstable"],
    "component_selection": ["parts", "component", "module", "sensor", "motor", "battery", "driver"],
    "project_planning": ["build", "project", "plan", "robot", "station", "system", "controller"],
    "safety_risk_review": ["safe", "risk", "damage", "gpio", "voltage", "power directly", "overload"],
    "explanation_request": ["explain", "why", "teach", "understand", "how does"],
}


def preprocess_description(description_text: str) -> str:
    text = description_text.replace("\u2192", " to ").replace("->", " to ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _matches(pattern, text: str, unit_key: str | None = None) -> list[dict]:
    values = []
    for match in pattern.finditer(text):
        item = {"value": float(match.group("value")), "raw": match.group(0)}
        if unit_key and match.groupdict().get(unit_key):
            item["unit"] = match.group(unit_key)
        values.append(item)
    return values


def classify_intents(text: str) -> list[str]:
    lowered = text.lower()
    intents = [
        intent
        for intent, keywords in INTENT_KEYWORDS.items()
        if any(keyword in lowered for keyword in keywords)
    ]
    return intents or ["project_planning", "safety_risk_review"]


def extract_engineering_entities(text: str) -> dict:
    return {
        "voltages": _matches(VOLTAGE_RE, text),
        "currents": _matches(CURRENT_RE, text, "unit"),
        "power_ratings": _matches(POWER_RE, text),
        "resistances": _matches(RESISTANCE_RE, text, "unit"),
        "capacitances": _matches(CAPACITANCE_RE, text, "unit"),
        "battery_capacities": _matches(CAPACITY_RE, text),
        "budgets": _matches(BUDGET_RE, text),
        "dimensions": _matches(DIMENSION_RE, text, "unit"),
        "deadlines": [match.group("value") for match in DEADLINE_RE.finditer(text)],
    }


def infer_missing_information(cleaned_text: str, entities: dict) -> list[str]:
    lowered = cleaned_text.lower()
    missing = []
    if not any(name in lowered for name in ["arduino", "esp32", "pico", "microcontroller", "mcu"]):
        missing.append("microcontroller or main board")
    if not any(name in lowered for name in ["battery", "adapter", "usb", "power supply", "lipo", "18650"]):
        missing.append("power source type")
    if any(name in lowered for name in ["battery", "lipo", "18650", "aa pack"]) and not entities["battery_capacities"]:
        missing.append("battery capacity in mAh")
    if any(name in lowered for name in ["motor", "servo", "pump", "solenoid", "relay"]) and not any(name in lowered for name in ["driver", "mosfet", "l298n", "tb6612", "drv8833", "uln2003"]):
        missing.append("driver or switching part for high-current loads")
    if not entities["voltages"]:
        missing.append("voltage ratings for the supply and important parts")
    if not entities["currents"]:
        missing.append("current ratings for the supply or high-current loads")
    return missing


def understand_project_text(description_text: str) -> dict:
    cleaned = preprocess_description(description_text)
    entities = extract_engineering_entities(cleaned)
    return {
        "cleaned_text": cleaned,
        "intents": classify_intents(cleaned),
        "entities": entities,
        "missing_information": infer_missing_information(cleaned, entities),
    }
