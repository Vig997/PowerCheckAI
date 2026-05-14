def build_features(matches: list[dict], ee_result: dict) -> dict:
    components = [match["component"] for match in matches]
    current = ee_result["analysis"]["current"]
    warnings = ee_result["analysis"]["warnings"]
    source = ee_result["power_source"]
    return {
        "total_typical_current": current["typical_total_mA"],
        "peak_current": current["peak_total_mA"],
        "supply_current_rating": source.get("max_current_mA", 0),
        "current_margin": current["current_margin_mA"],
        "number_of_motors": sum(1 for component in components if component.get("category") == "motor"),
        "number_of_servos": sum(1 for component in components if component.get("category") == "servo"),
        "led_count": sum(match["extracted"]["quantity"] for match in matches if "led" in match["component"].get("category", "") or "NeoPixel" in match["component"].get("name", "")),
        "has_esp32": any("esp32" in component.get("name", "").lower() for component in components),
        "has_arduino": any("arduino" in component.get("name", "").lower() for component in components),
        "has_wifi": any("wifi" in component.get("name", "").lower() or "esp32" in component.get("name", "").lower() for component in components),
        "has_camera": any("cam" in component.get("name", "").lower() for component in components),
        "has_inductive_load": any(component.get("is_inductive") for component in components),
        "has_external_driver": any(component.get("category") == "driver" for component in components),
        "has_regulator": ee_result.get("regulator") is not None,
        "voltage_mismatch_count": sum(1 for warning in warnings if "voltage" in warning["code"] or "logic" in warning["code"]),
        "gpio_risk_count": sum(1 for warning in warnings if "gpio" in warning["code"]),
        "brownout_risk": any("brownout" in warning["code"] or "supply" in warning["code"] for warning in warnings),
        "regulator_heat": ee_result["analysis"].get("regulator_heat", {}).get("heat_watts", ee_result["analysis"].get("regulator_heat", {}).get("loss_watts", 0)) or 0,
        "battery_type": source.get("source_type", "unknown"),
    }
