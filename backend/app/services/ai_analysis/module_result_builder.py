from __future__ import annotations

import re

from .module_explanation_generator import join_fixes
from .schemas import ModuleResult
from .utils import clamp, severity_from_score, status_from_score


MODULE_TITLES = [
    "Current Draw Check",
    "Board Reset Risk",
    "GPIO Pin Safety",
    "Battery Life Estimate",
    "Regulator Heat Check",
    "Parts Compatibility Check",
    "Power Path Map",
    "Startup Spike Check",
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


def _first_useful_sentence(description_text: str) -> str:
    text = description_text.strip()
    parts_marker = text.lower().find("parts needed")
    if parts_marker > 0:
        text = text[:parts_marker].strip()
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        sentence = sentence.strip(" -")
        if len(sentence) >= 24:
            return sentence[:220].rstrip(" ,.;")
    return text[:220].rstrip(" ,.;")


def _project_context(project_name: str, description_text: str) -> dict[str, str]:
    label = project_name.strip() or "this project"
    combined = f"{project_name} {description_text}".lower()

    if "bluetooth" in combined and any(word in combined for word in ["rc car", "car", "vehicle"]):
        goal = "make a Bluetooth-controlled car move smoothly while the Arduino keeps a stable connection"
        focus = "motor power and controller stability both matter because the car needs to move and still listen to commands"
    elif "plant" in combined and any(word in combined for word in ["water", "pump", "soil"]):
        goal = "water a plant automatically when the soil gets dry"
        focus = "the pump must switch on without dragging down the controller or sensor readings"
    elif "weather" in combined or "bme280" in combined or "dht" in combined:
        goal = "collect sensor readings and show or send weather data reliably"
        focus = "the project is mostly low power, so stable sensor and display power matters more than raw motor current"
    elif "obstacle" in combined or "ultrasonic" in combined:
        goal = "detect obstacles and move the robot without resets during motor movement"
        focus = "sensor readings and motor power have to stay stable at the same time"
    elif "rfid" in combined or "door lock" in combined:
        goal = "read an RFID tag and unlock the latch safely"
        focus = "the reader, controller, and lock mechanism need compatible voltage and separated load power"
    elif "music" in combined or "visualizer" in combined:
        goal = "turn sound into LED patterns without overloading the LED power rail"
        focus = "the microphone signal is small, but the LED strip can become the main power load"
    elif "smart home" in combined or "relay" in combined:
        goal = "switch loads from a microcontroller without putting those loads directly on GPIO pins"
        focus = "the controller should only command the relays while the relay board handles the actual switching load"
    elif "alarm clock" in combined or "rtc" in combined:
        goal = "keep time, drive the display, and trigger alerts reliably"
        focus = "the current is usually modest, so stable 5V or 3.3V power and clean wiring are the main concerns"
    elif "line following" in combined or "line follower" in combined:
        goal = "follow a line while the motors and sensors stay powered together"
        focus = "motor surges can disturb the sensors, so the power path needs enough headroom"
    elif "camera" in combined or "esp32-cam" in combined:
        goal = "capture or stream images without WiFi and camera spikes resetting the ESP32-CAM"
        focus = "the camera board is sensitive to weak 5V input and short current spikes"
    elif "servo arm" in combined or ("servo" in combined and "arm" in combined):
        goal = "move the arm predictably without servo current spikes pulling down the controller"
        focus = "servo power should be treated as a main load, not as a small accessory"
    elif "neopixel" in combined or "led strip" in combined:
        goal = "light the LEDs at the intended brightness without overloading USB or board power"
        focus = "LED brightness changes can quickly change the current draw"
    elif "robot" in combined or "motor" in combined:
        goal = "run the moving parts while keeping the controller and sensors stable"
        focus = "motor power is the main stress point for the whole build"
    else:
        goal = f"build {label} safely and keep the controller stable while the parts run"
        focus = "the power system should support the whole build, not just the microcontroller"

    sentence = _first_useful_sentence(description_text)
    if sentence:
        story = f"{label} is described as: {sentence}."
    else:
        story = f"{label} is being reviewed as a beginner electronics project."

    return {
        "label": label,
        "goal": goal,
        "focus": focus,
        "story": story,
    }


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
    project_context = _project_context(project_name, description_text)
    project_label = project_context["label"]
    project_goal = project_context["goal"]
    project_focus = project_context["focus"]

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
        f"{project_context['story']} The main goal appears to be to {project_goal}. "
        f"Parts PowerCheck recognized: {_join([match['component'].get('name', 'part') for match in matches], 'no database parts matched')}. "
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
            "Current Draw Check",
            current_score,
            f"For {project_label}, the goal is to {project_goal}. The build may use about {typical:.0f} mA normally and up to {peak:.0f} mA during its hardest moments.",
            (
                f"{shared_detected} Parts that may use a lot of power: {_join(high_current, 'none clearly detected')}. "
                f"Motors: {_join(motors, 'none')}. Servos: {_join(servos, 'none')}. LEDs: {_join(leds, 'none')}. "
                f"Power source: {source_name}, current rating: {source_current} mA. For this project, {project_focus}."
            ),
            [
                f"{project_label} may need about {-margin:.0f} mA more than the supply can safely provide during its busiest moment." if margin < 0 else f"{project_label} has about {margin:.0f} mA of extra supply room for the parts listed so far.",
                f"The important question is not just whether the controller turns on, but whether the whole {project_label} can do its main job while every load is active.",
                "Weak USB supplies, breadboards, and thin jumper wires can drop voltage when current jumps.",
                "Use the normal current number to understand everyday power use, but use the peak current number when choosing the supply.",
                f"If the peak current is close to the supply rating, {project_label} may work during a simple test but fail when it tries to {project_goal}.",
                f"If you add more loads to {project_label}, rerun this check because the current budget can change quickly.",
            ],
            join_fixes(supply_warnings, [f"Choose the power supply for {project_label} using peak current, not just normal current.", "Leave extra current headroom so the supply is not running at its limit.", "Write the supply current rating next to the project parts list so it is easy to compare against the peak draw.", *replacement_advice]),
            _module_missing(input_context, ["exact current draw for the power-hungry parts", "power supply current rating"] if high_current else []),
            [
                f"Recommended supply current = peak current x 1.2 = {peak:.0f} mA x 1.2 = {recommended_current:.0f} mA.",
                "Students should size power from the worst case because motors, servos, LEDs, and radios do not draw constant current.",
            ],
            risk.get("confidence", 0.75),
        ),
        _safety_module(
            "Board Reset Risk",
            brownout_score,
            f"This checks whether {project_label} might reset when it tries to {project_goal}.",
            (
                f"Controller: {_join(microcontrollers, ee_result['microcontroller'].get('name', 'inferred controller'))}. "
                f"Supply: {source_name}. Voltage converter/regulator: {regulator_name}. Parts that can cause sudden power jumps: {_join((motors + servos + leds + inductive)[:8], 'none clearly detected')}. "
                f"Peak current: {peak:.0f} mA. Extra supply room: {margin:.0f} mA. In the context of {project_label}, {project_focus}."
            ),
            [
                f"The Arduino or ESP32 in {project_label} may reset if motors, servos, LEDs, WiFi, or camera bursts pull the voltage down.",
                "ESP32 boards can be picky about power when WiFi turns on.",
                f"A weak shared power line can make {project_label} act broken even if the code is fine.",
                "Brownout problems often look like software bugs because the board restarts or freezes randomly.",
                "The risk is higher when the board and motors or LEDs share the same weak supply path.",
                f"If resets happen only when {project_label} starts doing its main action, the power system is more suspicious than the code.",
            ],
            join_fixes(brownout_warnings, [f"For {project_label}, keep the controller rail stable while the power-hungry parts turn on.", "Power motors, servos, or LEDs from a separate power line when needed.", "Add a large capacitor near motors, servos, or LED strips.", "Use a stronger supply if peak current is close to the limit.", "Keep the board power line short and avoid running high-current loads through the board.", "Test the board alone first, then add high-power loads one at a time so the cause of a reset is easier to find."]),
            _module_missing(input_context, ["wire length and how the power lines are connected", "whether the board and high-power loads share one supply"]),
            [
                "Brownout means the voltage drops below what the controller needs to run reliably.",
                "Voltage sag increases when load current is high or the source has high internal resistance.",
            ],
            risk.get("confidence", 0.75),
        ),
        _safety_module(
            "GPIO Pin Safety",
            gpio_score,
            f"For {project_label}, board pins should help control the project, not directly power the heavy loads.",
            (
                f"Driver or protection parts found: {_join(drivers, 'none')}. "
                f"Parts that need safer control hardware: {_join(driver_required + inductive + high_current, 'none obvious')}. "
                f"Parts that may be sensitive to signal voltage: {_join(logic_sensitive, 'none obvious')}. "
                f"Because this project is trying to {project_goal}, the GPIO pins should act like command signals while driver hardware handles load power."
            ),
            [
                f"Powering the active parts of {project_label} from a pin can damage the board.",
                "Motors and relays can send a voltage spike backward when they turn off unless a driver or diode protects the circuit.",
                "A 5V signal going into a 3.3V board like an ESP32 or Pico can be unsafe.",
                f"A safe GPIO connection for {project_label} usually means the pin only controls something else; it does not carry the load's main power.",
                "If a load moves, clicks, spins, heats up, or lights many LEDs, assume it needs a driver until the part specs prove otherwise.",
                "Servo signal wires can connect to GPIO, but the servo power wire should usually come from a separate 5V supply.",
            ],
            join_fixes(gpio_warnings, [f"Wire {project_label} so the microcontroller sends signals and the driver hardware carries the real load current.", "Use board pins only as control signals into a driver, MOSFET, relay module, or motor driver.", "Connect the board ground and external supply ground together.", "Check whether each signal is 3.3V or 5V before connecting it to the board.", "For inductive parts like motors, pumps, solenoids, and relays, include flyback protection or use a module that already has it."]),
            _module_missing(input_context, ["which parts are connected directly to board pins", "signal voltage for sensors and modules"]),
            [
                "A GPIO pin is a logic interface, not a power supply.",
                "Driver hardware lets a tiny control signal switch a larger load safely.",
            ],
            risk.get("confidence", 0.75),
        ),
        _safety_module(
            "Battery Life Estimate",
            battery_score,
            f"For {project_label}, battery life depends on whether the power source can support the full project while it tries to {project_goal}. "
            + (battery.get("message") or f"Estimated runtime is {battery.get('runtime_hours_typical')} hr typical and {battery.get('runtime_hours_worst')} hr worst case."),
            (
                f"Power source: {source_name}. Source type: {source.get('source_type', 'unknown')}. "
                f"Voltage: {source.get('voltage', 'unknown')} V. Battery size: {source.get('capacity_mAh', 'not provided')} mAh. "
                f"Typical load: {typical:.0f} mA. Peak load: {peak:.0f} mA. For {project_label}, {project_focus}."
            ),
            [
                f"Battery life for {project_label} is hard to estimate if the battery size or current rating is missing.",
                "Small batteries can still sag even if the capacity number looks okay.",
                "If a converter boosts a battery up to 5V, the battery may have to provide more current than expected.",
                f"A battery that is fine for only the controller may be too weak for the full {project_label}.",
                f"The worst-case runtime can be much shorter than normal runtime when {project_label} is doing its main job.",
                "Capacity tells you about runtime, but discharge current tells you whether the battery can safely handle the load right now.",
            ],
            [f"Pick a battery or adapter based on what {project_label} does at full load, not only idle current.", "Enter the battery capacity in mAh and the max current it can provide.", "Avoid rectangular 9V batteries for motors, servos, pumps, and LED strips.", "Use a battery pack or wall adapter rated for the peak current.", "If you use a converter, make sure the battery can handle the converter input current.", "For classroom demos, test battery runtime with the project doing its hardest task, not just sitting idle."],
            _module_missing(input_context, ["battery capacity in mAh", "battery max discharge current"] if source.get("source_type") == "battery" and not source.get("capacity_mAh") else []),
            [
                "Runtime is roughly capacity in mAh divided by average current in mA.",
                "Peak current matters for whether the battery can hold voltage, not just for runtime.",
            ],
            risk.get("confidence", 0.72),
        ),
        _safety_module(
            "Regulator Heat Check",
            heat_score,
            f"For {project_label}, the regulator has to support the parts that make the project useful, not just the board. It may waste about {heat_value:.2f} W as heat. Status: {heat.get('classification', 'not calculated')}.",
            (
                f"Voltage converter/regulator found: {regulator_name}. Input voltage: {source.get('voltage', 'unknown')} V. "
                f"Output voltage used by PowerCheck: {analysis.get('regulated_voltage', 'unknown')} V. "
                f"Estimated current through this path: {typical:.0f} mA. Heat estimate: {heat_value:.2f} W. "
                f"In this project, heat matters because {project_focus}."
            ),
            [
                f"If the regulator in {project_label} gets hot, the voltage can drop and the board may reset.",
                "Small linear regulators are not good for dropping a lot of voltage at high current.",
                "Motors, servos, pumps, and LED strips should not be powered through the board's tiny regulator.",
                "Heat risk goes up when the input voltage is much higher than the output voltage.",
                f"Even if {project_label} turns on, a hot regulator can slowly become unstable after running for a while.",
                "A regulator that is only warm at first can get hotter after several minutes, especially inside an enclosure.",
            ],
            join_fixes(heat_warnings, [f"Make sure the regulator path is sized for the way {project_label} will actually be used.", "Use a buck converter for high current or large voltage drops.", "Give motors, servos, pumps, and LED strips their own properly rated power path.", "Touch-test carefully only after powering down, or use a temperature reading if available.", "Avoid using the Arduino onboard regulator as the main supply for high-current accessories."]),
            _module_missing(input_context, ["regulator part number or converter efficiency", "input and output voltage"] if not regulator else []),
            [
                "Linear regulator heat is roughly (input voltage - output voltage) x current.",
                "Buck converters waste less power as heat when stepping voltage down.",
            ],
            risk.get("confidence", 0.72),
        ),
        _safety_module(
            "Parts Compatibility Check",
            compatibility_score,
            f"For {project_label}, compatibility means the parts can work together while the project tries to {project_goal}. PowerCheck found {len(voltage_warnings)} possible voltage/signal issue(s) and {len(unmatched_names)} part(s) to double-check.",
            (
                f"Controller: {_join(microcontrollers, 'not specified')}. Parts that may care about signal voltage: {_join(logic_sensitive, 'none obvious')}. "
                f"Parts that need drivers: {_join(driver_required, 'none detected')}. Parts to check manually: {_join(unmatched_names, 'none')}. "
                f"This matters for {project_label} because {project_focus}."
            ),
            [
                f"Parts in {project_label} can plug together physically but still be wrong electrically.",
                "Common mistakes include sending 5V signals into 3.3V boards, powering 3.3V parts from 5V, or skipping a driver.",
                "Parts PowerCheck does not recognize should be checked from their product page or datasheet.",
                "Voltage, signal level, and current draw all need to match; matching only one of them is not enough.",
                f"For {project_label}, the safest habit is to check every module's VCC pin, signal pins, and required driver before wiring.",
                "Communication modules also need TX/RX signal levels checked, not only their power pin voltage.",
            ],
            join_fixes(voltage_warnings, [f"Make a quick compatibility table for {project_label}: part, voltage, signal level, current, and driver needed.", "Use a level shifter when a 5V signal goes to a 3.3V board.", "Check unknown parts for voltage, current draw, and signal voltage before wiring.", "Do not assume a module is 5V-safe or 3.3V-safe unless the listing or datasheet says so.", "Before building, make a small table with each part's voltage, current, and driver requirement."]),
            _module_missing(input_context, ["part specs for: " + ", ".join(unmatched_names[:4]), "logic voltage for communication modules"] if unmatched_names else []),
            [
                "Compatibility means voltage range, logic level, current draw, and driver requirement all make sense together.",
                "When a spec is unknown, the safe answer is to verify it, not guess it.",
            ],
            risk.get("confidence", 0.7),
        ),
        _safety_module(
            "Power Path Map",
            rail_score,
            f"This maps how power should move through {project_label} so each part can support the goal: {project_goal}.",
            (
                f"Suggested tree: {' -> '.join(tree_branch)}. "
                f"Low-power side: {_join(microcontrollers + sensors + displays, 'controller and small modules')}. "
                f"High-power side: {_join(high_current + inductive + leds + servos, 'no separate high-power branch detected')}. "
                f"For this project, {project_focus}."
            ),
            [
                f"If the power path in {project_label} is unclear, it is easy to connect a part to the wrong voltage.",
                "Sending motor or LED power through the controller board can overload small traces or regulators.",
                "If grounds are not connected together, signal wires may act strangely even when the power wires look right.",
                f"The power tree helps you separate the low-power control side of {project_label} from the parts that actually do the work.",
                "A clear power tree also makes debugging easier because you can test one branch at a time.",
                "For student projects, the power tree is often easier to understand than a full schematic because it only tracks where power goes.",
            ],
            [f"Draw the {project_label} power path from source to controller and loads before wiring.", "Draw the battery or adapter first, then converters, then the board and loads.", "Keep motors, servos, pumps, and LED strips on separate power paths when possible.", "Label every power line with its voltage.", "Show where grounds connect so signal wires have a shared reference.", "Put fuses, switches, and converters in the tree if they are part of the build."],
            _module_missing(input_context, ["whether motors/servos/LEDs use a separate supply", "which regulator powers each rail"]),
            [
                "A power tree is a map of power flow, not a schematic of every signal wire.",
                "For student projects, clear rail labels prevent many wiring mistakes.",
            ],
            risk.get("confidence", 0.74),
        ),
        _safety_module(
            "Startup Spike Check",
            surge_score,
            f"This checks whether {project_label} may need a big burst of current when it starts doing its main action.",
            (
                f"Surge sources detected: motors [{_join(motors, 'none')}], servos [{_join(servos, 'none')}], "
                f"LEDs [{_join(leds, 'none')}], inductive loads [{_join(inductive, 'none')}]. "
                f"Typical current: {typical:.0f} mA. Peak current: {peak:.0f} mA. "
                f"For {project_label}, this connects directly to the goal to {project_goal}."
            ),
            [
                f"Motors in {project_label} can draw much more current when they first start spinning.",
                f"Servos in {project_label} can spike when they first move or push against something.",
                f"LED strips, pumps, solenoids, cameras, and WiFi can make short power bursts that reset weak systems before {project_label} can finish its job.",
                "This short burst may last less than a second, but it can still be enough to make the board restart.",
                f"Projects like {project_label} are more likely to have startup problems when several active parts begin at the same time.",
                "Startup surge is usually worst when parts start from rest or when many loads turn on together.",
            ],
            [f"Test {project_label} during the moment when it first starts doing the task you built it for.", "Choose the supply using peak current plus extra room.", "Avoid turning on every high-power part at the same time.", "Add capacitors near noisy loads and use separate power paths for motors, servos, and LEDs.", "If possible, start motors slowly in code instead of jumping straight to full speed.", "When testing, listen and watch for resets exactly when the project first powers on or starts moving."],
            _module_missing(input_context, ["startup current for motors or servos", "whether high-power parts turn on at the same time"] if motors or servos else []),
            [
                "Startup surge is why a project can fail at turn-on but seem fine in a steady-current estimate.",
                "Peak current is the number to use for supply sizing.",
            ],
            risk.get("confidence", 0.73),
        ),
    ]
