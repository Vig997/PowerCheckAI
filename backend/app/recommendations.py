from collections import OrderedDict


FIX_BY_CODE = {
    "supply_undersized": ("Use a stronger power supply with at least 20% current margin.", "Easy", "$$"),
    "supply_margin_low": ("Choose a supply rated above the recommended current.", "Easy", "$$"),
    "voltage_too_low": ("Move the component to a compatible voltage rail or add a regulator.", "Medium", "$"),
    "voltage_too_high": ("Use a regulator or level-safe power rail before connecting the component.", "Medium", "$"),
    "esp32_5v_logic": ("Add a logic level shifter or resistor divider for 5V signals.", "Easy", "$"),
    "three_v_logic_on_5v_board": ("Use level shifting between 5V Arduino signals and 3.3V modules.", "Easy", "$"),
    "gpio_overload": ("Use GPIO only as a signal and add a driver stage for the load.", "Medium", "$"),
    "board_power_high_current": ("Power high-current loads externally and connect all grounds together.", "Medium", "$$"),
    "driver_required": ("Add the correct motor, MOSFET, relay, or stepper driver.", "Medium", "$$"),
    "inductive_load": ("Use flyback protection for motors, relays, pumps, and solenoids.", "Medium", "$"),
    "stall_or_startup_current": ("Size the supply for startup or stall current, not just normal current.", "Easy", "$$"),
    "neopixel_high_current": ("Use an external 5V supply, common ground, and a capacitor near the strip.", "Easy", "$$"),
    "nine_volt_high_current": ("Replace the 9V rectangular battery with AA, LiPo plus regulator, or wall power.", "Easy", "$$"),
    "multiple_servos_board_power": ("Use a separate 5V servo supply or servo driver board with external power.", "Medium", "$$"),
    "regulator_heat": ("Use a buck converter for high-current loads or large voltage drops.", "Easy", "$"),
}


def explain_warnings(warnings: list[dict]) -> list[dict]:
    return [
        {
            "issue": warning.get("issue"),
            "why_it_matters": warning.get("why_it_matters"),
            "likely_symptoms": warning.get("likely_symptoms", []),
            "recommended_fix": warning.get("recommended_fix"),
            "severity": warning.get("severity"),
            "component": warning.get("component"),
        }
        for warning in warnings
    ]


def top_fixes(warnings: list[dict], limit: int = 3) -> list[dict]:
    fixes: OrderedDict[str, dict] = OrderedDict()
    severity_rank = {"critical": 0, "warning": 1, "suggestion": 2}
    for warning in sorted(warnings, key=lambda item: severity_rank.get(item.get("severity"), 3)):
        code = warning.get("code")
        if code not in FIX_BY_CODE or code in fixes:
            continue
        fix, difficulty, cost = FIX_BY_CODE[code]
        fixes[code] = {
            "code": code,
            "fix": fix,
            "difficulty": difficulty,
            "cost": cost,
        }
        if len(fixes) == limit:
            break
    return list(fixes.values())
