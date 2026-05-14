from __future__ import annotations


def _component_names(matches: list[dict]) -> list[str]:
    names = []
    for match in matches:
        component = match["component"]
        quantity = match["extracted"].get("quantity", 1)
        names.append(f"{component.get('name')} x{quantity}")
    return names


def build_final_recommendation(matches: list[dict], unmatched: list[dict], ee_result: dict, risk: dict, features: dict, input_context: dict | None = None) -> dict:
    analysis = ee_result["analysis"]
    warnings = analysis.get("warnings", [])
    warning_codes = {warning.get("code") for warning in warnings}
    score = int(risk.get("score", analysis.get("risk", {}).get("score", 0)))
    safety_score = max(0, min(100, 100 - score))
    label = risk.get("label", analysis.get("risk", {}).get("label", "Safe"))

    if score <= 30:
        verdict = "Safe to build"
    elif score <= 50:
        verdict = "Buildable with minor changes"
    elif score <= 75:
        verdict = "Buildable but risky"
    else:
        verdict = "Not recommended until parts are changed"

    parts_to_add: list[str] = []
    parts_to_replace: list[str] = []
    parts_to_remove: list[str] = []
    missing_information: list[str] = []
    input_context = input_context or {}

    if features["number_of_motors"] and not features["has_external_driver"]:
        parts_to_add.append("TB6612FNG, DRV8833, or L298N motor driver sized for the motors")
    if features["has_inductive_load"]:
        parts_to_add.append("Flyback diode or driver module protection for inductive loads")
    if features["led_count"] >= 10:
        parts_to_add.extend(["5V LED supply sized for the LED count", "330 ohm data resistor", "1000 uF capacitor near the strip"])
    if features["number_of_servos"] > 1:
        parts_to_add.append("Separate 5V servo supply with common ground")
    if features["voltage_mismatch_count"]:
        parts_to_add.append("Logic level shifter for unsafe 5V-to-3.3V signal paths")
    if not features["has_regulator"] and ee_result["power_source"].get("voltage", 5) > 5.5:
        parts_to_add.append("Buck converter to create a stable 5V logic rail")
    if "regulator_heat" in warning_codes:
        parts_to_replace.append("Replace a hot linear regulator with a buck converter")
    if "nine_volt_high_current" in warning_codes:
        parts_to_replace.append("Replace the rectangular 9V battery with AA, LiPo, or wall adapter power")
    if any(part.get("reason") == "no_database_match" for part in unmatched):
        missing_information.append("Datasheet voltage/current specs for unmatched parts")
    for item in input_context.get("missing_information", []):
        if item not in missing_information:
            missing_information.append(item)
    if any(part.get("reason") == "power_source_candidate" for part in unmatched) and not ee_result.get("power_source"):
        missing_information.append("Power source voltage, current rating, and capacity")

    highest_priority = "Project looks electrically reasonable. Verify datasheets before wiring."
    if warnings:
        highest_priority = warnings[0].get("recommended_fix", highest_priority)

    summary = (
        f"PowerCheck classified this project as {label}. "
        f"Estimated peak current is {analysis['current']['peak_total_mA']} mA from a "
        f"{ee_result['power_source'].get('name', 'selected supply')}."
    )

    return {
        "verdict": verdict,
        "overall_score": safety_score,
        "risk_score": score,
        "summary": summary,
        "parts_to_keep": _component_names(matches),
        "parts_to_add": parts_to_add[:8],
        "parts_to_replace": parts_to_replace[:5],
        "parts_to_remove": parts_to_remove,
        "missing_information": missing_information,
        "highest_priority_fix": highest_priority,
        "known_facts": {
            "matched_parts": _component_names(matches),
            "detected_intents": input_context.get("intents", []),
            "explicit_values": input_context.get("entities", {}),
        },
        "assumptions": [
            f"Inferred power source: {ee_result['power_source'].get('name', 'unknown')}",
            f"Inferred controller: {ee_result['microcontroller'].get('name', 'unknown')}",
            "Database current values are simplified beginner-friendly estimates, not datasheet guarantees.",
        ],
        "beginner_build_advice": (
            "Build and test one power rail at a time. Keep GPIO pins for signals, use drivers for loads, "
            "size the supply from peak current, and connect grounds between external rails and the controller."
        ),
        "confidence": risk.get("confidence", 0.7),
    }
