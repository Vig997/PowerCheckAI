from app.seed_data import COMPONENTS, EXAMPLE_PROJECTS, POWER_SOURCES, REGULATORS


def test_phase_one_seed_catalog_has_expected_size():
    assert len(COMPONENTS) >= 50
    assert len(POWER_SOURCES) >= 11
    assert len(REGULATORS) >= 4
    assert len(EXAMPLE_PROJECTS) >= 10


def test_seed_catalog_contains_core_beginner_parts():
    component_names = {component["name"] for component in COMPONENTS}
    source_names = {source["name"] for source in POWER_SOURCES}
    regulator_names = {regulator["name"] for regulator in REGULATORS}

    assert "Arduino Uno" in component_names
    assert "ESP32 Dev Board" in component_names
    assert "NeoPixel Strip" in component_names
    assert "SG90 Micro Servo" in component_names
    assert "Small DC Motor" in component_names
    assert "9V Rectangular Battery" in source_names
    assert "5V Wall Adapter 5A" in source_names
    assert "Adjustable Buck Converter" in regulator_names
