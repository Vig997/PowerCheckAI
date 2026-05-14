from app.recommendations import top_fixes


def generate_text_report(project_name: str, analysis: dict, components: list[dict], power_source: dict) -> str:
    current = analysis["current"]
    battery = analysis["battery_life"]
    risk = analysis["risk"]
    warnings = analysis["warnings"]
    fixes = top_fixes(warnings)

    component_lines = [
        f"- {item['quantity']}x {item['component']['name']}"
        for item in components
    ]
    warning_lines = [f"- [{warning['severity']}] {warning['issue']}" for warning in warnings] or ["- No major warnings."]
    fix_lines = [f"- {fix['fix']} ({fix['difficulty']}, {fix['cost']})" for fix in fixes] or ["- No fixes needed for the current estimate."]

    battery_line = (
        battery["message"]
        if battery.get("is_wall_powered")
        else f"{battery.get('runtime_hours_typical')}h typical, {battery.get('runtime_hours_worst')}h worst case"
    )

    return "\n".join(
        [
            f"PowerCheck AI Report: {project_name}",
            "",
            f"Risk: {risk['label']} ({risk['score']}/100)",
            f"Power source: {power_source['name']}",
            f"Typical current: {current['typical_total_mA']} mA",
            f"Peak current: {current['peak_total_mA']} mA",
            f"Recommended supply: {current['recommended_current_mA']} mA",
            f"Battery estimate: {battery_line}",
            "",
            "Components:",
            *component_lines,
            "",
            "Warnings:",
            *warning_lines,
            "",
            "Recommended fixes:",
            *fix_lines,
            "",
            "Disclaimer: PowerCheck AI provides estimates and educational warnings. Verify with datasheets and safe electrical practices.",
        ]
    )
