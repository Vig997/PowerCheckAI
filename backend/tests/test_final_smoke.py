from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_catalog_docs_and_helper_endpoints_respond() -> None:
    for path in [
        "/health",
        "/components",
        "/power-sources",
        "/regulators",
        "/example-projects",
        "/docs",
        "/openapi.json",
    ]:
        response = client.get(path)
        assert response.status_code == 200

    helper_checks = [
        ("/estimate-neopixel-current", {"led_count": 30, "brightness_percent": 50}),
        (
            "/estimate-regulator-heat",
            {"regulator_type": "buck", "input_voltage": 12, "output_voltage": 5, "output_current_mA": 1000},
        ),
        (
            "/estimate-battery-life",
            {"capacity_mAh": 2000, "typical_current_mA": 500, "peak_current_mA": 1000},
        ),
    ]
    for path, payload in helper_checks:
        response = client.post(path, json=payload)
        assert response.status_code == 200


def test_ai_description_analysis_handles_vague_and_specific_projects() -> None:
    vague_response = client.post(
        "/analyze-project-description",
        json={
            "project_name": "Vague Robot Idea",
            "description_text": "I want to make a small Arduino robot with some motors, a battery, and maybe lights.",
            "existing_project_config": {},
        },
    )
    assert vague_response.status_code == 200
    vague_data = vague_response.json()
    assert len(vague_data["modules"]) == 8
    assert vague_data["final_recommendation"]["verdict"]

    specific_response = client.post(
        "/analyze-project-description",
        json={
            "project_name": "Bluetooth RC Car",
            "description_text": (
                "Arduino Nano, HC-05 Bluetooth module, L298N motor driver, four TT motors, "
                "2x 18650 cells, and LM2596 buck converter."
            ),
            "existing_project_config": {},
        },
    )
    assert specific_response.status_code == 200
    specific_data = specific_response.json()
    assert len(specific_data["modules"]) == 8
    assert specific_data["matched_components"]
    assert specific_data["final_recommendation"]["verdict"]
