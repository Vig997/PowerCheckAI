from __future__ import annotations

from typing import Any

from app.analysis_engine import analyze_project

from .utils import model_to_dict


def infer_microcontroller(matches: list[dict]) -> dict | None:
    for match in matches:
        component = match["component"]
        if component.get("category") == "microcontroller":
            return component
    return None


def infer_power_source(unmatched: list[dict], power_sources: list[Any]) -> dict:
    text = " ".join(part.get("raw_text", "") for part in unmatched).lower()
    sources = [model_to_dict(source) for source in power_sources]
    if "10a" in text or "10 a" in text:
        return {"name": "Custom 5V 10A Power Supply", "voltage": 5.0, "max_current_mA": 10000, "capacity_mAh": None, "internal_resistance_ohm": 0.04, "source_type": "adapter"}
    if "18650" in text or "7.4" in text or "2x" in text and "battery" in text:
        return {"name": "2x 18650 Battery Pack", "voltage": 7.4, "max_current_mA": 6000, "capacity_mAh": 3000, "internal_resistance_ohm": 0.08, "source_type": "battery"}
    if "12v" in text or "12 v" in text:
        return next((source for source in sources if source["name"] == "12V Wall Adapter 2A"), sources[0])
    if "usb-c" in text:
        return next((source for source in sources if source["name"] == "USB-C 5V 3A"), sources[0])
    if "5v" in text and ("2a" in text or "2 a" in text):
        return next((source for source in sources if source["name"] == "5V Wall Adapter 2A"), sources[0])
    if "lipo" in text:
        return next((source for source in sources if source["name"] == "2S LiPo Battery"), sources[0])
    return next((source for source in sources if source["name"] == "5V Wall Adapter 2A"), sources[0])


def infer_regulator(matches: list[dict], unmatched: list[dict], regulators: list[Any]) -> dict | None:
    regs = [model_to_dict(regulator) for regulator in regulators]
    text = " ".join(
        [match["extracted"]["raw_text"] for match in matches]
        + [part.get("raw_text", "") + " " + part.get("normalized_name", "") for part in unmatched]
    ).lower()
    if "buck" in text or "lm2596" in text or "xl4015" in text:
        return next((reg for reg in regs if reg["name"] == "Adjustable Buck Converter"), None)
    if "boost" in text:
        return next((reg for reg in regs if reg["name"] == "Boost Converter"), None)
    if "ams1117" in text:
        return next((reg for reg in regs if reg["name"] == "AMS1117 Linear Regulator"), None)
    return None


def run_ee_check(matches: list[dict], unmatched: list[dict], power_sources: list[Any], regulators: list[Any]) -> dict:
    microcontroller = infer_microcontroller(matches)
    selected = [
        {"component": match["component"], "quantity": match["extracted"]["quantity"], "powered_from": "same_supply"}
        for match in matches
        if match["component"].get("category") != "microcontroller"
    ]
    power_source = infer_power_source(unmatched, power_sources)
    regulator = infer_regulator(matches, unmatched, regulators)
    if not microcontroller:
        microcontroller = {"name": "Inferred Arduino Uno", "category": "microcontroller", "typical_current_mA": 50, "max_current_mA": 100, "logic_voltage": 5.0, "recommended_gpio_current_mA": 20}
    return {
        "microcontroller": microcontroller,
        "selected_components": selected,
        "power_source": power_source,
        "regulator": regulator,
        "analysis": analyze_project(microcontroller, selected, power_source, regulator, {"brightness_percent": 80, "wifi_enabled": True}),
    }
