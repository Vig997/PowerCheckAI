from __future__ import annotations

from .module_explanation_generator import join_fixes
from .schemas import ModuleResult
from .utils import clamp, severity_from_score, status_from_score


MODULE_TITLES = [
    "Real-Time Current Profiling",
    "Brownout Prediction Engine",
    "GPIO Protection Analysis",
    "Battery Discharge Modeling",
    "Thermal Regulator Analysis",
    "Component Compatibility Engine",
    "Power Tree Visualization",
    "Startup Surge Analysis",
]


def _parts_by_category(matches: list[dict], category: str) -> list[str]:
    return [
        f"{match['component'].get('name', 'part')} x{match['extracted'].get('quantity', 1)}"
        for match in matches
        if match["component"].get("category") == category
    ]


def _parts_with_flag(matches: list[dict], flag: str) -> list[str]:
    return [
        f"{match['component'].get('name', 'part')} x{match['extracted'].get('quantity', 1)}"
        for match in matches
        if match["component"].get(flag)
    ]


def _driver_required_parts(matches: list[dict]) -> list[str]:
    return [
        f"{match['component'].get('name', 'part')} x{match['extracted'].get('quantity', 1)}"
        for match in matches
        if match["component"].get("requires_driver")
    ]


def _filter_warnings(warnings: list[dict], keywords: list[str]) -> list[dict]:
    return [
        warning
        for warning in warnings
        if any(keyword in warning.get("code", "").lower() or keyword in warning.get("issue", "").lower() for keyword in keywords)
    ]


def _join(items: list[str], fallback: str = "not detected") -> str:
    return ", ".join(items[:8]) if items else fallback


def _entity_values(input_context: dict, key: str) -> str:
    values = input_context.get("entities", {}).get(key, [])
    return ", ".join(item.get("raw", str(item.get("value"))) for item in values[:5]) or "none provided"


def _module_missing(input_context: dict, extra: list[str] | None = None) -> list[str]:
    missing = list(input_context.get("missing_information", []))
    for item in extra or []:
        if item and item not in missing:
            missing.append(item)
    return missing[:6]


def _known_values(input_context: dict, keys: list[str]) -> str:
    pieces = [f"{key.replace('_', ' ')}: {_entity_values(input_context, key)}" for key in keys]
    return "; ".join(pieces)


def _safety_module(
    title: str,
    safety_score: int,
    summary: str,
    detected: str,
    risks: list[str],
    fixes: list[str],
    missing_information: list[str],
    learning: list[str],
    confidence: float,
) -> ModuleResult:
    score = int(clamp(safety_score, 0, 100))
    risk_score = int(clamp(100 - score, 0, 100))
    return ModuleResult(
        title=title,
        status=status_from_score(risk_score),
        score=score,
        severity=severity_from_score(risk_score),
        summary=summary,
        details=detected,
        symptoms=risks[:6],
        fixes=list(dict.fromkeys(fixes))[:6],
        missing_information=missing_information[:6],
        formulas=learning[:6],
        confidence=confidence,
    )


def _score_from_margin(margin: float, recommended_current: float) -> int:
    if margin < 0:
        return 25
    if margin < recommended_current * 0.2:
        return 62
    return 88


def _replacement_advice(features: dict, final_recommendation: dict) -> list[str]:
    fixes: list[str] = []
    if features["number_of_motors"] and not features["has_external_driver"]:
        fixes.append("Add a motor driver so the motors do not pull power through the board pins.")
    if features["number_of_motors"] and features["has_external_driver"]:
        fixes.append("Keep the motor driver; if the project feels weak, use a more efficient driver than the L298N.")
    if features["number_of_servos"] > 1:
        fixes.append("Use a separate 5V supply for the servos and connect its ground to the board ground.")
    if features["led_count"] >= 30:
        fixes.append("Use a separate 5V supply for the LED strip, plus a data resistor and large capacitor near the strip.")
    if features["voltage_mismatch_count"]:
        fixes.append("Use a level shifter, or choose parts that are safe for 3.3V boards like ESP32 and Pico.")
    if features["has_inductive_load"]:
        fixes.append("Use a driver or protection diode for motors, relays, pumps, and solenoids.")
    fixes.extend(final_recommendation.get("parts_to_add", [])[:3])
    fixes.extend(final_recommendation.get("parts_to_replace", [])[:3])
    return list(dict.fromkeys(fixes))[:6]


def build_module_results(
    project_name: str,
    description_text: str,
    matches: list[dict],
    unmatched: list[dict],
    ee_result: dict,
    features: dict,
    risk: dict,
    final_recommendation: dict,
    input_context: dict | None = None,
) -> list[ModuleResult]:
    input_context = input_context or {}
    analysis = ee_result["analysis"]
    current = analysis["current"]
    battery = analysis["battery_life"]
    heat = analysis["regulator_heat"]
    warnings = analysis["warnings"]
    source = ee_result["power_source"]
    regulator = ee_result.get("regulator")

    microcontrollers = _parts_by_category(matches, "microcontroller")
    motors = _parts_by_category(matches, "motor")
    servos = _parts_by_category(matches, "servo")
    leds = _parts_by_category(matches, "led")
    drivers = _parts_by_category(matches, "driver")
    sensors = _parts_by_category(matches, "sensor")
    displays = _parts_by_category(matches, "display")
    high_current = _parts_with_flag(matches, "is_high_current")
    inductive = _parts_with_flag(matches, "is_inductive")
    logic_sensitive = _parts_with_flag(matches, "is_logic_sensitive")
    driver_required = _driver_required_parts(matches)
    unmatched_names = [part.get("raw_text", "unknown part") for part in unmatched if part.get("reason") == "no_database_match"]

    typical = float(current["typical_total_mA"])
    peak = float(current["peak_total_mA"])
    recommended_current = float(current.get("recommended_current_mA") or peak * 1.2)
    margin = float(current.get("current_margin_mA", 0))
    heat_value = float(heat.get("heat_watts", heat.get("loss_watts", 0)) if heat.get("present") else 0)
    source_name = source.get("name", "inferred power source")
    source_current = source.get("max_current_mA", "unknown")
    regulator_name = regulator.get("name") if regulator else "none detected"
    replacement_advice = _replacement_advice(features, final_recommendation)

    supply_warnings = _filter_warnings(warnings, ["supply", "current"])
    brownout_warnings = _filter_warnings(warnings, ["brownout", "voltage sag"])
    gpio_warnings = _filter_warnings(warnings, ["gpio", "driver", "inductive"])
    voltage_warnings = _filter_warnings(warnings, ["voltage", "logic", "3.3", "5v"])
    heat_warnings = _filter_warnings(warnings, ["regulator", "heat"])

    current_score = _score_from_margin(margin, recommended_current)
    brownout_score = 35 if features["brownout_risk"] or margin < 0 else 64 if margin < peak * 0.2 else 88
    gpio_score = int(clamp(92 - 20 * len(gpio_warnings), 15, 96))
    if driver_required and not drivers:
        gpio_score = min(gpio_score, 35)
    if source.get("source_type") == "battery" and battery.get("runtime_hours_worst") is not None:
        battery_score = 35 if battery["runtime_hours_worst"] < 1 else 65 if battery["runtime_hours_worst"] < 3 else 88
    elif source.get("source_type") == "battery":
        battery_score = 55
    else:
        battery_score = 86
    heat_score = 25 if heat_value >= 2.5 else 45 if heat_value >= 1.5 else 68 if heat_value >= 0.5 else 90
    compatibility_score = int(clamp(92 - 18 * len(voltage_warnings) - 10 * len(unmatched_names), 15, 96))
    rail_score = 58 if high_current and not (drivers or regulator) else 72 if high_current else 90
    surge_score = 42 if features["number_of_motors"] or features["number_of_servos"] or features["led_count"] >= 30 else 82

    shared_detected = (
        f"Project: {project_name}. Parts PowerCheck recognized: {_join([match['component'].get('name', 'part') for match in matches], 'no database parts matched')}. "
        f"Parts to double-check manually: {_join(unmatched_names, 'none')}. Numbers found in the text: {_known_values(input_context, ['voltages', 'currents', 'battery_capacities'])}."
    )

    tree_branch = [
        source_name,
        regulator_name if regulator else "direct rail",
        _join(microcontrollers, "controller"),
    ]
    if sensors or displays:
        tree_branch.append(_join((sensors + displays)[:4], "sensors/displays"))
    if high_current:
        tree_branch.append(_join(high_current, "high-current loads"))

    return [
        _safety_module(
            "Real-Time Current Profiling",
            current_score,
            f"Your project may use about {typical:.0f} mA normally and up to {peak:.0f} mA during heavier moments.",
            (
                f"{shared_detected} Parts that may use a lot of power: {_join(high_current, 'none clearly detected')}. "
                f"Motors: {_join(motors, 'none')}. Servos: {_join(servos, 'none')}. LEDs: {_join(leds, 'none')}. "
                f"Power source: {source_name}, current rating: {source_current} mA."
            ),
            [
                f"The project may need about {-margin:.0f} mA more than the supply can safely provide." if margin < 0 else f"The supply has about {margin:.0f} mA of extra room.",
                "A project can look fine at low power, then fail when motors, servos, LEDs, or WiFi suddenly need more current.",
                "Weak USB supplies, breadboards, and thin jumper wires can drop voltage when current jumps.",
                "Use the normal current number to understand everyday power use, but use the peak current number when choosing the supply.",
                "If the peak current is close to the supply rating, the project may work on the desk but fail when everything turns on at once.",
                "If you add more motors, brighter LEDs, or extra wireless modules later, rerun this check because the current budget can change quickly.",
            ],
            join_fixes(supply_warnings, ["Choose the power supply using peak current, not just normal current.", "Leave extra current headroom so the supply is not running at its limit.", "Write the supply current rating next to the project parts list so it is easy to compare against the peak draw.", *replacement_advice]),
            _module_missing(input_context, ["exact current draw for the power-hungry parts", "power supply current rating"] if high_current else []),
            [
                f"Recommended supply current = peak current x 1.2 = {peak:.0f} mA x 1.2 = {recommended_current:.0f} mA.",
                "Students should size power from the worst case because motors, servos, LEDs, and radios do not draw constant current.",
            ],
            risk.get("confidence", 0.75),
        ),
        _safety_module(
            "Brownout Prediction Engine",
            brownout_score,
            "This checks whether the board might reset when the project suddenly needs more power.",
            (
                f"Controller: {_join(microcontrollers, ee_result['microcontroller'].get('name', 'inferred controller'))}. "
                f"Supply: {source_name}. Voltage converter/regulator: {regulator_name}. Parts that can cause sudden power jumps: {_join((motors + servos + leds + inductive)[:8], 'none clearly detected')}. "
                f"Peak current: {peak:.0f} mA. Extra supply room: {margin:.0f} mA."
            ),
            [
                "The Arduino or ESP32 may reset if motors, servos, LEDs, WiFi, or camera bursts pull the voltage down.",
                "ESP32 boards can be picky about power when WiFi turns on.",
                "A weak shared power line can make the project act broken even if the code is fine.",
                "Brownout problems often look like software bugs because the board restarts or freezes randomly.",
                "The risk is higher when the board and motors or LEDs share the same weak supply path.",
                "If resets happen only when a motor starts, a servo moves, or WiFi connects, the power system is more suspicious than the code.",
            ],
            join_fixes(brownout_warnings, ["Power motors, servos, or LEDs from a separate power line when needed.", "Add a large capacitor near motors, servos, or LED strips.", "Use a stronger supply if peak current is close to the limit.", "Keep the board power line short and avoid running high-current loads through the board.", "Test the board alone first, then add high-power loads one at a time so the cause of a reset is easier to find."]),
            _module_missing(input_context, ["wire length and how the power lines are connected", "whether the board and high-power loads share one supply"]),
            [
                "Brownout means the voltage drops below what the controller needs to run reliably.",
                "Voltage sag increases when load current is high or the source has high internal resistance.",
            ],
            risk.get("confidence", 0.75),
        ),
        _safety_module(
            "GPIO Protection Analysis",
            gpio_score,
            "Board pins should send signals; they should not directly power motors, relays, pumps, or LED strips.",
            (
                f"Driver or protection parts found: {_join(drivers, 'none')}. "
                f"Parts that need safer control hardware: {_join(driver_required + inductive + high_current, 'none obvious')}. "
                f"Parts that may be sensitive to signal voltage: {_join(logic_sensitive, 'none obvious')}."
            ),
            [
                "Powering motors, relays, pumps, solenoids, LED strips, or big buzzers from a pin can damage the board.",
                "Motors and relays can send a voltage spike backward when they turn off unless a driver or diode protects the circuit.",
                "A 5V signal going into a 3.3V board like an ESP32 or Pico can be unsafe.",
                "A safe GPIO connection usually means the pin only controls something else; it does not carry the load's main power.",
                "If a load moves, clicks, spins, heats up, or lights many LEDs, assume it needs a driver until the part specs prove otherwise.",
                "Servo signal wires can connect to GPIO, but the servo power wire should usually come from a separate 5V supply.",
            ],
            join_fixes(gpio_warnings, ["Use board pins only as control signals into a driver, MOSFET, relay module, or motor driver.", "Connect the board ground and external supply ground together.", "Check whether each signal is 3.3V or 5V before connecting it to the board.", "For inductive parts like motors, pumps, solenoids, and relays, include flyback protection or use a module that already has it."]),
            _module_missing(input_context, ["which parts are connected directly to board pins", "signal voltage for sensors and modules"]),
            [
                "A GPIO pin is a logic interface, not a power supply.",
                "Driver hardware lets a tiny control signal switch a larger load safely.",
            ],
            risk.get("confidence", 0.75),
        ),
        _safety_module(
            "Battery Discharge Modeling",
            battery_score,
            battery.get("message") or f"Estimated runtime is {battery.get('runtime_hours_typical')} hr typical and {battery.get('runtime_hours_worst')} hr worst case.",
            (
                f"Power source: {source_name}. Source type: {source.get('source_type', 'unknown')}. "
                f"Voltage: {source.get('voltage', 'unknown')} V. Battery size: {source.get('capacity_mAh', 'not provided')} mAh. "
                f"Typical load: {typical:.0f} mA. Peak load: {peak:.0f} mA."
            ),
            [
                "Battery life is hard to estimate if the battery size or current rating is missing.",
                "Small batteries can still sag even if the capacity number looks okay.",
                "If a converter boosts a battery up to 5V, the battery may have to provide more current than expected.",
                "A battery that is fine for sensors may be too weak for motors, pumps, servos, or long LED strips.",
                "The worst-case runtime can be much shorter than the normal runtime when the project has moving parts or bright LEDs.",
                "Capacity tells you about runtime, but discharge current tells you whether the battery can safely handle the load right now.",
            ],
            ["Enter the battery capacity in mAh and the max current it can provide.", "Avoid rectangular 9V batteries for motors, servos, pumps, and LED strips.", "Use a battery pack or wall adapter rated for the peak current.", "If you use a converter, make sure the battery can handle the converter input current.", "For classroom demos, test battery runtime with the project doing its hardest task, not just sitting idle."],
            _module_missing(input_context, ["battery capacity in mAh", "battery max discharge current"] if source.get("source_type") == "battery" and not source.get("capacity_mAh") else []),
            [
                "Runtime is roughly capacity in mAh divided by average current in mA.",
                "Peak current matters for whether the battery can hold voltage, not just for runtime.",
            ],
            risk.get("confidence", 0.72),
        ),
        _safety_module(
            "Thermal Regulator Analysis",
            heat_score,
            f"The voltage converter/regulator may waste about {heat_value:.2f} W as heat. Status: {heat.get('classification', 'not calculated')}.",
            (
                f"Voltage converter/regulator found: {regulator_name}. Input voltage: {source.get('voltage', 'unknown')} V. "
                f"Output voltage used by PowerCheck: {analysis.get('regulated_voltage', 'unknown')} V. "
                f"Estimated current through this path: {typical:.0f} mA. Heat estimate: {heat_value:.2f} W."
            ),
            [
                "If the regulator gets hot, the voltage can drop and the board may reset.",
                "Small linear regulators are not good for dropping a lot of voltage at high current.",
                "Motors, servos, pumps, and LED strips should not be powered through the board's tiny regulator.",
                "Heat risk goes up when the input voltage is much higher than the output voltage.",
                "Even if the project turns on, a hot regulator can slowly become unstable after running for a while.",
                "A regulator that is only warm at first can get hotter after several minutes, especially inside an enclosure.",
            ],
            join_fixes(heat_warnings, ["Use a buck converter for high current or large voltage drops.", "Give motors, servos, pumps, and LED strips their own properly rated power path.", "Touch-test carefully only after powering down, or use a temperature reading if available.", "Avoid using the Arduino onboard regulator as the main supply for high-current accessories."]),
            _module_missing(input_context, ["regulator part number or converter efficiency", "input and output voltage"] if not regulator else []),
            [
                "Linear regulator heat is roughly (input voltage - output voltage) x current.",
                "Buck converters waste less power as heat when stepping voltage down.",
            ],
            risk.get("confidence", 0.72),
        ),
        _safety_module(
            "Component Compatibility Engine",
            compatibility_score,
            f"PowerCheck found {len(voltage_warnings)} possible voltage/signal issue(s) and {len(unmatched_names)} part(s) to double-check.",
            (
                f"Controller: {_join(microcontrollers, 'not specified')}. Parts that may care about signal voltage: {_join(logic_sensitive, 'none obvious')}. "
                f"Parts that need drivers: {_join(driver_required, 'none detected')}. Parts to check manually: {_join(unmatched_names, 'none')}."
            ),
            [
                "Parts can plug together physically but still be wrong electrically.",
                "Common mistakes include sending 5V signals into 3.3V boards, powering 3.3V parts from 5V, or skipping a driver.",
                "Parts PowerCheck does not recognize should be checked from their product page or datasheet.",
                "Voltage, signal level, and current draw all need to match; matching only one of them is not enough.",
                "For beginner projects, the safest habit is to check every module's VCC pin, signal pins, and required driver before wiring.",
                "Communication modules also need TX/RX signal levels checked, not only their power pin voltage.",
            ],
            join_fixes(voltage_warnings, ["Use a level shifter when a 5V signal goes to a 3.3V board.", "Check unknown parts for voltage, current draw, and signal voltage before wiring.", "Do not assume a module is 5V-safe or 3.3V-safe unless the listing or datasheet says so.", "Before building, make a small table with each part's voltage, current, and driver requirement."]),
            _module_missing(input_context, ["part specs for: " + ", ".join(unmatched_names[:4]), "logic voltage for communication modules"] if unmatched_names else []),
            [
                "Compatibility means voltage range, logic level, current draw, and driver requirement all make sense together.",
                "When a spec is unknown, the safe answer is to verify it, not guess it.",
            ],
            risk.get("confidence", 0.7),
        ),
        _safety_module(
            "Power Tree Visualization",
            rail_score,
            "This shows the order power should follow from the supply to the board and project parts.",
            (
                f"Suggested tree: {' -> '.join(tree_branch)}. "
                f"Low-power side: {_join(microcontrollers + sensors + displays, 'controller and small modules')}. "
                f"High-power side: {_join(high_current + inductive + leds + servos, 'no separate high-power branch detected')}."
            ),
            [
                "If the power path is unclear, it is easy to connect a part to the wrong voltage.",
                "Sending motor or LED power through the controller board can overload small traces or regulators.",
                "If grounds are not connected together, signal wires may act strangely even when the power wires look right.",
                "The power tree helps you separate low-power logic parts from high-power loads before the wiring gets messy.",
                "A clear power tree also makes debugging easier because you can test one branch at a time.",
                "For student projects, the power tree is often easier to understand than a full schematic because it only tracks where power goes.",
            ],
            ["Draw the battery or adapter first, then converters, then the board and loads.", "Keep motors, servos, pumps, and LED strips on separate power paths when possible.", "Label every power line with its voltage.", "Show where grounds connect so signal wires have a shared reference.", "Put fuses, switches, and converters in the tree if they are part of the build."],
            _module_missing(input_context, ["whether motors/servos/LEDs use a separate supply", "which regulator powers each rail"]),
            [
                "A power tree is a map of power flow, not a schematic of every signal wire.",
                "For student projects, clear rail labels prevent many wiring mistakes.",
            ],
            risk.get("confidence", 0.74),
        ),
        _safety_module(
            "Startup Surge Analysis",
            surge_score,
            "This checks whether the project may need a big burst of current when parts first turn on.",
            (
                f"Surge sources detected: motors [{_join(motors, 'none')}], servos [{_join(servos, 'none')}], "
                f"LEDs [{_join(leds, 'none')}], inductive loads [{_join(inductive, 'none')}]. "
                f"Typical current: {typical:.0f} mA. Peak current: {peak:.0f} mA."
            ),
            [
                "Motors can draw much more current when they first start spinning.",
                "Servos can spike when they first move or push against something.",
                "LED strips, pumps, solenoids, cameras, and WiFi can make short power bursts that reset weak systems.",
                "This short burst may last less than a second, but it can still be enough to make the board restart.",
                "Projects with several motors or servos are more likely to have startup problems because many parts can spike at the same time.",
                "Startup surge is usually worst when parts start from rest or when many loads turn on together.",
            ],
            ["Choose the supply using peak current plus extra room.", "Avoid turning on every high-power part at the same time.", "Add capacitors near noisy loads and use separate power paths for motors, servos, and LEDs.", "If possible, start motors slowly in code instead of jumping straight to full speed.", "When testing, listen and watch for resets exactly when the project first powers on or starts moving."],
            _module_missing(input_context, ["startup current for motors or servos", "whether high-power parts turn on at the same time"] if motors or servos else []),
            [
                "Startup surge is why a project can fail at turn-on but seem fine in a steady-current estimate.",
                "Peak current is the number to use for supply sizing.",
            ],
            risk.get("confidence", 0.73),
        ),
    ]
