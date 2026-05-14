import pytest

from app.analysis_engine import (
    analyze_project,
    calculate_battery_life,
    calculate_current_draw,
    calculate_regulator_heat,
    calculate_risk_score,
    classify_risk,
    component_current,
    find_warnings,
    recommended_supply_current,
)


ARDUINO_UNO = {
    "name": "Arduino Uno",
    "category": "microcontroller",
    "voltage_min": 5.0,
    "voltage_max": 5.0,
    "typical_current_mA": 50,
    "max_current_mA": 100,
    "recommended_gpio_current_mA": 20,
    "logic_voltage": 5.0,
    "is_logic_sensitive": True,
}

ESP32 = {
    "name": "ESP32 Dev Board",
    "category": "microcontroller",
    "voltage_min": 3.3,
    "voltage_max": 5.0,
    "typical_current_mA": 100,
    "max_current_mA": 500,
    "recommended_gpio_current_mA": 12,
    "logic_voltage": 3.3,
    "is_logic_sensitive": True,
}

LED = {
    "name": "Standard LED",
    "category": "led",
    "voltage_min": 2.0,
    "voltage_max": 5.0,
    "typical_current_mA": 10,
    "max_current_mA": 20,
    "gpio_safe": True,
}

MOTOR = {
    "name": "Small DC Motor",
    "category": "motor",
    "voltage_min": 3.0,
    "voltage_max": 6.0,
    "typical_current_mA": 200,
    "max_current_mA": 600,
    "startup_current_mA": 800,
    "stall_current_mA": 1000,
    "gpio_safe": False,
    "requires_driver": True,
    "is_high_current": True,
    "is_inductive": True,
}

SERVO = {
    "name": "SG90 Micro Servo",
    "category": "servo",
    "voltage_min": 5.0,
    "voltage_max": 5.0,
    "typical_current_mA": 250,
    "max_current_mA": 500,
    "stall_current_mA": 700,
    "gpio_safe": False,
    "requires_driver": False,
    "is_high_current": True,
    "is_inductive": True,
}

NEOPIXEL_STRIP = {
    "name": "NeoPixel Strip",
    "category": "led",
    "voltage_min": 5.0,
    "voltage_max": 5.0,
    "typical_current_mA": 20,
    "max_current_mA": 60,
    "logic_voltage": 5.0,
    "gpio_safe": False,
    "requires_driver": False,
    "is_high_current": True,
    "is_logic_sensitive": True,
}

HC_SR04 = {
    "name": "HC-SR04 Ultrasonic Sensor",
    "category": "sensor",
    "voltage_min": 5.0,
    "voltage_max": 5.0,
    "typical_current_mA": 15,
    "max_current_mA": 20,
    "logic_voltage": 5.0,
    "gpio_safe": True,
    "is_logic_sensitive": True,
}

USB_500 = {
    "name": "USB 5V 500mA",
    "voltage": 5.0,
    "max_current_mA": 500,
    "capacity_mAh": None,
    "source_type": "usb",
}

ADAPTER_5V_5A = {
    "name": "5V Wall Adapter 5A",
    "voltage": 5.0,
    "max_current_mA": 5000,
    "capacity_mAh": None,
    "source_type": "adapter",
}

BATTERY_9V = {
    "name": "9V Rectangular Battery",
    "voltage": 9.0,
    "max_current_mA": 300,
    "capacity_mAh": 500,
    "source_type": "battery",
}


def codes(warnings):
    return {warning["code"] for warning in warnings}


def test_total_current_calculation_includes_microcontroller_and_components():
    result = calculate_current_draw(ARDUINO_UNO, [{"component": LED, "quantity": 2}])

    assert result["typical_total_mA"] == 70
    assert result["peak_total_mA"] == 140


def test_peak_current_uses_stall_current_for_motors():
    result = calculate_current_draw(ARDUINO_UNO, [{"component": MOTOR, "quantity": 2}])

    assert result["typical_total_mA"] == 450
    assert result["peak_total_mA"] == 2100


def test_recommended_current_uses_twenty_percent_safety_margin():
    assert recommended_supply_current(1000) == 1200


def test_battery_life_calculation_handles_typical_and_worst_case():
    result = calculate_battery_life(BATTERY_9V, typical_current_mA=100, peak_current_mA=250, efficiency=0.8)

    assert result["is_wall_powered"] is False
    assert result["runtime_hours_typical"] == 4.0
    assert result["runtime_hours_worst"] == 1.6


def test_wall_powered_sources_return_wall_power_message():
    result = calculate_battery_life(USB_500, typical_current_mA=100, peak_current_mA=250)

    assert result["is_wall_powered"] is True
    assert result["message"] == "wall powered"


def test_linear_regulator_heat_calculation_and_classification():
    regulator = {"name": "LM7805", "regulator_type": "linear"}

    result = calculate_regulator_heat(regulator, input_voltage=9.0, output_voltage=5.0, output_current_mA=500)

    assert result["heat_watts"] == 2.0
    assert result["classification"] == "Hot"


def test_buck_converter_loss_calculation():
    regulator = {"name": "Buck", "regulator_type": "buck", "efficiency": 0.9}

    result = calculate_regulator_heat(regulator, input_voltage=12.0, output_voltage=5.0, output_current_mA=1000)

    assert result["loss_watts"] == pytest.approx(0.5)
    assert result["classification"] == "Warm"


def test_boost_converter_estimates_input_current():
    regulator = {"name": "Boost", "regulator_type": "boost", "efficiency": 0.85}

    result = calculate_regulator_heat(regulator, input_voltage=3.7, output_voltage=5.0, output_current_mA=1000)

    assert result["input_current_mA"] == pytest.approx(1590.0, abs=1.0)


def test_voltage_mismatch_warning_for_5v_component_on_3v7_lipo():
    lipo_1s = {"name": "1S LiPo Battery", "voltage": 3.7, "max_current_mA": 5000, "capacity_mAh": 1200}

    warnings = find_warnings(ESP32, [{"component": HC_SR04, "quantity": 1}], lipo_1s)

    assert "voltage_too_low" in codes(warnings)


def test_esp32_5v_logic_warning():
    warnings = find_warnings(ESP32, [{"component": HC_SR04, "quantity": 1}], ADAPTER_5V_5A)

    assert "esp32_5v_logic" in codes(warnings)


def test_gpio_overload_warning_for_motor_powered_from_gpio():
    warnings = find_warnings(ARDUINO_UNO, [{"component": MOTOR, "quantity": 1, "powered_from": "gpio"}], USB_500)

    assert "gpio_overload" in codes(warnings)
    assert "driver_required" in codes(warnings)


def test_neopixel_high_current_warning_and_brightness_scaling():
    current = component_current(NEOPIXEL_STRIP, quantity=60, settings={"brightness_percent": 50})
    warnings = find_warnings(
        ARDUINO_UNO,
        [{"component": NEOPIXEL_STRIP, "quantity": 60, "powered_from": "board"}],
        USB_500,
        settings={"brightness_percent": 50},
    )

    assert current["typical_mA"] == 600
    assert current["peak_mA"] == 1800
    assert "neopixel_high_current" in codes(warnings)


def test_servo_warning_mentions_stall_current_and_external_power():
    warnings = find_warnings(ARDUINO_UNO, [{"component": SERVO, "quantity": 2, "powered_from": "board"}], USB_500)

    assert "stall_or_startup_current" in codes(warnings)
    assert "multiple_servos_board_power" in codes(warnings)


def test_9v_battery_high_current_warning():
    warnings = find_warnings(ARDUINO_UNO, [{"component": SERVO, "quantity": 1}], BATTERY_9V)

    assert "nine_volt_high_current" in codes(warnings)


def test_risk_score_classification_clamps_to_unsafe():
    current = calculate_current_draw(ARDUINO_UNO, [{"component": MOTOR, "quantity": 2, "powered_from": "gpio"}])
    warnings = find_warnings(ARDUINO_UNO, [{"component": MOTOR, "quantity": 2, "powered_from": "gpio"}], BATTERY_9V, current=current)
    risk = calculate_risk_score(warnings, current, BATTERY_9V, brownout_detected=True)

    assert risk["score"] == 100
    assert risk["label"] == "Unsafe"


def test_analyze_project_returns_phase_one_dashboard_metrics():
    result = analyze_project(
        ARDUINO_UNO,
        [{"component": LED, "quantity": 2}],
        ADAPTER_5V_5A,
    )

    assert result["current"]["recommended_current_mA"] == 168
    assert result["battery_life"]["message"] == "wall powered"
    assert result["risk"]["label"] == "Safe"
    assert result["warnings"] == []


def test_classify_risk_boundaries():
    assert classify_risk(30) == "Safe"
    assert classify_risk(31) == "Borderline"
    assert classify_risk(65) == "Borderline"
    assert classify_risk(66) == "Unsafe"
