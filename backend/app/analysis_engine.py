from __future__ import annotations

from collections import Counter
from typing import Any


RISK_LABELS = {
    "safe": "Safe",
    "borderline": "Borderline",
    "unsafe": "Unsafe",
}


def _as_dict(value: Any) -> dict:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    return {
        key: getattr(value, key)
        for key in dir(value)
        if not key.startswith("_") and not callable(getattr(value, key))
    }


def _num(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _contains(component: dict, text: str) -> bool:
    return text.lower() in component.get("name", "").lower()


def _is_neopixel(component: dict) -> bool:
    return _contains(component, "neopixel") or _contains(component, "ws2812")


def _is_esp32(component: dict) -> bool:
    return "esp32" in component.get("name", "").lower()


def _is_arduino(component: dict) -> bool:
    return "arduino" in component.get("name", "").lower()


def _warning(
    code: str,
    severity: str,
    issue: str,
    why: str,
    symptoms: list[str] | None = None,
    fix: str | None = None,
    component: str | None = None,
) -> dict:
    return {
        "code": code,
        "severity": severity,
        "component": component,
        "issue": issue,
        "why_it_matters": why,
        "likely_symptoms": symptoms or [],
        "recommended_fix": fix,
    }


def normalize_selection(selection: dict) -> dict:
    component = _as_dict(selection.get("component", selection))
    quantity = int(_num(selection.get("quantity", 1), 1))
    return {
        "component": component,
        "quantity": max(1, quantity),
        "powered_from": selection.get("powered_from", "same_supply"),
        "rail_voltage": selection.get("rail_voltage"),
    }


def component_current(component: dict, quantity: int = 1, settings: dict | None = None) -> dict:
    settings = settings or {}
    brightness = max(0, min(100, _num(settings.get("brightness_percent", 100), 100))) / 100
    typical_per_unit = _num(component.get("typical_current_mA"))
    peak_per_unit = max(
        _num(component.get("max_current_mA"), typical_per_unit),
        _num(component.get("startup_current_mA"), 0),
        _num(component.get("stall_current_mA"), 0),
        typical_per_unit,
    )

    if _is_neopixel(component):
        typical_per_unit *= brightness
        peak_per_unit *= brightness

    return {
        "typical_mA": typical_per_unit * quantity,
        "peak_mA": peak_per_unit * quantity,
        "typical_per_unit_mA": typical_per_unit,
        "peak_per_unit_mA": peak_per_unit,
    }


def calculate_current_draw(
    selected_microcontroller: dict | None,
    selected_components: list[dict],
    settings: dict | None = None,
) -> dict:
    settings = settings or {}
    line_items = []
    typical_total = 0.0
    peak_total = 0.0

    if selected_microcontroller:
        microcontroller = _as_dict(selected_microcontroller)
        micro_current = component_current(microcontroller, 1, settings)
        typical_total += micro_current["typical_mA"]
        peak_total += micro_current["peak_mA"]
        line_items.append(
            {
                "name": microcontroller.get("name"),
                "quantity": 1,
                "typical_mA": micro_current["typical_mA"],
                "peak_mA": micro_current["peak_mA"],
                "powered_from": "board",
            }
        )

    for raw_selection in selected_components:
        selection = normalize_selection(raw_selection)
        component = selection["component"]
        current = component_current(component, selection["quantity"], settings)
        typical_total += current["typical_mA"]
        peak_total += current["peak_mA"]
        line_items.append(
            {
                "name": component.get("name"),
                "quantity": selection["quantity"],
                "typical_mA": current["typical_mA"],
                "peak_mA": current["peak_mA"],
                "powered_from": selection["powered_from"],
            }
        )

    return {
        "typical_total_mA": round(typical_total, 2),
        "peak_total_mA": round(peak_total, 2),
        "line_items": line_items,
    }


def recommended_supply_current(peak_current_mA: float, safety_margin: float = 1.2) -> float:
    return round(max(0, peak_current_mA) * safety_margin, 2)


def calculate_current_margin(power_source: dict, peak_current_mA: float) -> dict:
    source = _as_dict(power_source)
    max_current = _num(source.get("max_current_mA"))
    margin = max_current - peak_current_mA
    margin_percent = margin / max_current if max_current else 0
    return {
        "current_margin_mA": round(margin, 2),
        "current_margin_percent": round(margin_percent, 3),
    }


def calculate_battery_life(
    power_source: dict,
    typical_current_mA: float,
    peak_current_mA: float,
    efficiency: float = 1.0,
) -> dict:
    source = _as_dict(power_source)
    capacity = source.get("capacity_mAh")
    if not capacity:
        return {
            "is_wall_powered": True,
            "runtime_hours_typical": None,
            "runtime_hours_worst": None,
            "message": "wall powered",
        }

    typical = (capacity * efficiency / typical_current_mA) if typical_current_mA > 0 else None
    worst = (capacity * efficiency / peak_current_mA) if peak_current_mA > 0 else None
    return {
        "is_wall_powered": False,
        "runtime_hours_typical": round(typical, 2) if typical is not None else None,
        "runtime_hours_worst": round(worst, 2) if worst is not None else None,
        "message": None,
    }


def classify_heat(power_watts: float) -> str:
    watts = round(power_watts, 3)
    if watts < 0.5:
        return "Safe"
    elif watts < 1.5:
        return "Warm"
    elif watts < 2.5:
        return "Hot"
    else:
        return "Unsafe"


def calculate_regulator_heat(
    regulator: dict | None,
    input_voltage: float,
    output_voltage: float,
    output_current_mA: float,
) -> dict:
    if not regulator:
        return {"present": False}

    reg = _as_dict(regulator)
    current_a = max(0, output_current_mA) / 1000
    regulator_type = reg.get("regulator_type")

    if regulator_type == "linear":
        heat_w = max(0, input_voltage - output_voltage) * current_a
        return {
            "present": True,
            "regulator_type": "linear",
            "heat_watts": round(heat_w, 3),
            "classification": classify_heat(heat_w),
        }

    if regulator_type == "buck":
        efficiency = _num(reg.get("efficiency"), 0.9)
        output_power_w = output_voltage * current_a
        loss_w = output_power_w * (1 - efficiency)
        return {
            "present": True,
            "regulator_type": "buck",
            "output_power_watts": round(output_power_w, 3),
            "loss_watts": round(loss_w, 3),
            "classification": classify_heat(loss_w),
        }

    if regulator_type == "boost":
        efficiency = _num(reg.get("efficiency"), 0.85)
        output_power_w = output_voltage * current_a
        input_current_a = output_power_w / (input_voltage * efficiency) if input_voltage > 0 and efficiency > 0 else None
        loss_w = output_power_w * (1 - efficiency)
        return {
            "present": True,
            "regulator_type": "boost",
            "output_power_watts": round(output_power_w, 3),
            "loss_watts": round(loss_w, 3),
            "input_current_mA": round(input_current_a * 1000, 2) if input_current_a is not None else None,
            "classification": classify_heat(loss_w),
        }

    return {"present": True, "regulator_type": regulator_type, "classification": "Unknown"}


def infer_regulated_voltage(selected_microcontroller: dict | None, power_source: dict, regulator: dict | None, settings: dict) -> float:
    if settings.get("regulated_output_voltage"):
        return float(settings["regulated_output_voltage"])
    if regulator:
        outputs = _as_dict(regulator).get("output_voltage_options") or []
        if selected_microcontroller and _is_esp32(_as_dict(selected_microcontroller)) and 5.0 in outputs:
            return 5.0
        if 5.0 in outputs:
            return 5.0
        if outputs:
            return float(outputs[0])
    return _num(_as_dict(power_source).get("voltage"), 5.0)


def find_warnings(
    selected_microcontroller: dict | None,
    selected_components: list[dict],
    power_source: dict,
    regulator: dict | None = None,
    settings: dict | None = None,
    current: dict | None = None,
    regulator_heat: dict | None = None,
) -> list[dict]:
    settings = settings or {}
    current = current or calculate_current_draw(selected_microcontroller, selected_components, settings)
    source = _as_dict(power_source)
    microcontroller = _as_dict(selected_microcontroller)
    supply_voltage = infer_regulated_voltage(microcontroller, source, regulator, settings)
    micro_logic = _num(microcontroller.get("logic_voltage"), supply_voltage)
    gpio_limit = _num(microcontroller.get("recommended_gpio_current_mA"), 20)
    warnings: list[dict] = []

    recommended = recommended_supply_current(current["peak_total_mA"])
    if _num(source.get("max_current_mA")) < current["peak_total_mA"]:
        warnings.append(
            _warning(
                "supply_undersized",
                "critical",
                "Your project may need more current than the power supply can provide.",
                "When the supply cannot provide enough current, voltage drops.",
                ["board resets", "LED flicker", "motor slowdown"],
                "Use a supply rated above the peak current with a 20% safety margin.",
            )
        )
    elif _num(source.get("max_current_mA")) < recommended:
        warnings.append(
            _warning(
                "supply_margin_low",
                "warning",
                "Your supply meets peak current but has little safety margin.",
                "Motors, servos, and wireless boards can briefly draw more than expected.",
                ["random resets", "unstable behavior"],
                "Choose a supply rated at least 20% above estimated peak current.",
            )
        )

    driver_selected = any(normalize_selection(item)["component"].get("category") == "driver" for item in selected_components)
    high_current_count = 0
    servo_count = 0
    has_high_current_load = False

    for raw_selection in selected_components:
        selection = normalize_selection(raw_selection)
        component = selection["component"]
        quantity = selection["quantity"]
        powered_from = selection["powered_from"]
        rail_voltage = selection["rail_voltage"]
        component_voltage = float(rail_voltage) if rail_voltage is not None else supply_voltage
        name = component.get("name")
        current_info = component_current(component, quantity, settings)
        peak_per_unit = current_info["peak_per_unit_mA"]

        if component.get("is_high_current"):
            high_current_count += quantity
            has_high_current_load = True
        if component.get("category") == "servo":
            servo_count += quantity

        if component.get("voltage_min") is not None and component_voltage + 0.05 < _num(component.get("voltage_min")):
            warnings.append(
                _warning(
                    "voltage_too_low",
                    "critical",
                    f"{name} may be under-volted on this rail.",
                    "A component below its rated voltage may behave unpredictably or fail to start.",
                    ["sensor glitches", "motor slowdown", "display instability"],
                    "Power the component from a compatible rail or add the right regulator.",
                    name,
                )
            )
        if component.get("voltage_max") is not None and component_voltage - 0.05 > _num(component.get("voltage_max")):
            warnings.append(
                _warning(
                    "voltage_too_high",
                    "critical",
                    f"{name} may be over-volted on this rail.",
                    "Too much voltage can permanently damage beginner electronics modules.",
                    ["hot components", "board failure"],
                    "Use a regulator or choose a power source with the correct voltage.",
                    name,
                )
            )

        logic_voltage = component.get("logic_voltage")
        if micro_logic <= 3.3 and logic_voltage and _num(logic_voltage) >= 5.0 and component.get("is_logic_sensitive"):
            warnings.append(
                _warning(
                    "esp32_5v_logic",
                    "critical",
                    f"{name} can expose 3.3V GPIO to a 5V signal.",
                    "ESP32 and Pico GPIO pins are not 5V tolerant.",
                    ["damaged GPIO pin", "unreliable readings"],
                    "Use a logic level shifter or voltage divider on 5V outputs.",
                    name,
                )
            )
        if micro_logic >= 5.0 and logic_voltage and _num(logic_voltage) <= 3.3 and component.get("is_logic_sensitive"):
            warnings.append(
                _warning(
                    "three_v_logic_on_5v_board",
                    "warning",
                    f"{name} is a 3.3V logic module connected to a 5V board.",
                    "Some 3.3V modules can be damaged by 5V logic signals.",
                    ["module failure", "unreliable communication"],
                    "Use level shifting and power the module at 3.3V.",
                    name,
                )
            )

        if powered_from == "gpio" and (not component.get("gpio_safe") or peak_per_unit > gpio_limit):
            warnings.append(
                _warning(
                    "gpio_overload",
                    "critical",
                    f"{name} should not be powered directly from a GPIO pin.",
                    "GPIO pins are for signals, not powering motors or high-current devices.",
                    ["damaged pin", "unstable output", "board failure"],
                    "Use a driver transistor, MOSFET module, relay module, or motor driver.",
                    name,
                )
            )

        if powered_from in {"board", "gpio"} and component.get("is_high_current"):
            warnings.append(
                _warning(
                    "board_power_high_current",
                    "warning",
                    f"{name} is a high-current load powered from the board.",
                    "Board 5V pins and onboard regulators are not meant for large load spikes.",
                    ["board resets", "servo jitter", "LED flicker"],
                    "Power high-current loads from a separate supply and connect grounds together.",
                    name,
                )
            )

        if component.get("requires_driver") and not driver_selected:
            warnings.append(
                _warning(
                    "driver_required",
                    "critical",
                    f"{name} needs a driver stage.",
                    "Motors, pumps, solenoids, and steppers draw more current than GPIO pins can handle.",
                    ["damaged GPIO pin", "motor not moving", "board resets"],
                    "Add a motor driver, MOSFET module, relay module, or ULN2003 as appropriate.",
                    name,
                )
            )

        if component.get("is_inductive"):
            warnings.append(
                _warning(
                    "inductive_load",
                    "suggestion",
                    f"{name} is an inductive load.",
                    "Inductive loads create voltage spikes when switched off.",
                    ["random resets", "damaged switch transistor"],
                    "Use a driver with flyback protection and connect grounds together.",
                    name,
                )
            )

        if component.get("category") in {"motor", "servo"}:
            warnings.append(
                _warning(
                    "stall_or_startup_current",
                    "warning",
                    f"{name} can briefly draw much more than its normal running current.",
                    "Startup or stall current can pull down the supply voltage.",
                    ["servo jitter", "motor slowdown", "board resets"],
                    "Size the supply for stall/startup current and keep motor power separate from logic power.",
                    name,
                )
            )

        if _is_neopixel(component):
            if powered_from in {"board", "gpio"} or current_info["peak_mA"] >= 1000:
                warnings.append(
                    _warning(
                        "neopixel_high_current",
                        "warning",
                        f"{name} can draw a lot of current at full brightness.",
                        "A long strip can need several amps.",
                        ["flickering", "color glitches", "board resets"],
                        "Use an external 5V supply, common ground, and a capacitor near the strip.",
                        name,
                    )
                )

    if "9v" in source.get("name", "").lower() and (has_high_current_load or current["peak_total_mA"] > 300):
        warnings.append(
            _warning(
                "nine_volt_high_current",
                "critical",
                "A 9V rectangular battery is a poor fit for this high-current project.",
                "9V rectangular batteries have high internal resistance and sag badly under load.",
                ["board resets", "weak motors", "short runtime"],
                "Use an AA pack, LiPo with regulator, or a properly rated wall adapter.",
            )
        )

    if servo_count > 1 and any(normalize_selection(item)["powered_from"] in {"board", "gpio"} for item in selected_components):
        warnings.append(
            _warning(
                "multiple_servos_board_power",
                "warning",
                "Multiple servos should not be powered from the microcontroller board.",
                "Servo stall current can add up quickly.",
                ["servo jitter", "board resets"],
                "Use a separate 5V servo supply or a servo driver board with external power.",
            )
        )

    if high_current_count > 0 and regulator and regulator_heat:
        heat_value = regulator_heat.get("heat_watts", regulator_heat.get("loss_watts", 0))
        if heat_value > 0.5:
            warnings.append(
                _warning(
                    "regulator_heat",
                    "warning" if heat_value < 2.0 else "critical",
                    "Your regulator may get hot.",
                    "Extra voltage or converter losses turn into heat.",
                    ["hot regulator", "voltage drop", "board resets"],
                    "Use a buck converter for high-current loads or large voltage drops.",
                )
            )

    return warnings


def classify_risk(score: float) -> str:
    if score <= 30:
        return RISK_LABELS["safe"]
    if score <= 65:
        return RISK_LABELS["borderline"]
    return RISK_LABELS["unsafe"]


def calculate_risk_score(
    warnings: list[dict],
    current: dict,
    power_source: dict,
    regulator_heat: dict | None = None,
    brownout_detected: bool = False,
) -> dict:
    source = _as_dict(power_source)
    score = 0
    peak = current["peak_total_mA"]
    recommended = recommended_supply_current(peak)
    source_max = _num(source.get("max_current_mA"))
    warning_codes = Counter(warning["code"] for warning in warnings)

    if source_max < peak:
        score += 35
    elif source_max < recommended:
        score += 20

    score += 25 * (warning_codes["voltage_too_low"] + warning_codes["voltage_too_high"])
    score += 30 * warning_codes["gpio_overload"]
    score += 20 * warning_codes["driver_required"]
    score += 15 * warning_codes["inductive_load"]
    score += 20 * warning_codes["multiple_servos_board_power"]
    score += 25 * warning_codes["neopixel_high_current"]
    score += 25 * warning_codes["nine_volt_high_current"]
    score += 20 * warning_codes["esp32_5v_logic"]

    if regulator_heat:
        heat = regulator_heat.get("heat_watts", regulator_heat.get("loss_watts", 0)) or 0
        if heat > 2.0:
            score += 30
        elif heat > 1.0:
            score += 15

    if brownout_detected:
        score += 30

    score = min(100, score)
    return {"score": score, "label": classify_risk(score)}


def analyze_project(
    selected_microcontroller: dict,
    selected_components: list[dict],
    power_source: dict,
    regulator: dict | None = None,
    settings: dict | None = None,
) -> dict:
    settings = settings or {}
    current = calculate_current_draw(selected_microcontroller, selected_components, settings)
    recommended = recommended_supply_current(current["peak_total_mA"])
    margin = calculate_current_margin(power_source, current["peak_total_mA"])
    regulated_voltage = infer_regulated_voltage(selected_microcontroller, power_source, regulator, settings)
    heat = calculate_regulator_heat(
        regulator,
        input_voltage=_num(_as_dict(power_source).get("voltage")),
        output_voltage=regulated_voltage,
        output_current_mA=current["typical_total_mA"],
    )
    battery = calculate_battery_life(power_source, current["typical_total_mA"], current["peak_total_mA"])
    warnings = find_warnings(
        selected_microcontroller,
        selected_components,
        power_source,
        regulator,
        settings,
        current,
        heat,
    )
    risk = calculate_risk_score(warnings, current, power_source, heat)

    return {
        "current": {
            **current,
            "recommended_current_mA": recommended,
            **margin,
        },
        "battery_life": battery,
        "regulator_heat": heat,
        "warnings": warnings,
        "warning_summary": dict(Counter(warning["severity"] for warning in warnings)),
        "risk": risk,
        "regulated_voltage": regulated_voltage,
    }
