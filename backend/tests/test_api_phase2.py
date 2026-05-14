from fastapi.testclient import TestClient

from app.main import app


def test_phase_two_get_endpoints_return_data():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}

        components = client.get("/components").json()
        power_sources = client.get("/power-sources").json()
        regulators = client.get("/regulators").json()
        examples = client.get("/example-projects").json()

    assert len(components) >= 50
    assert len(power_sources) >= 11
    assert len(regulators) >= 4
    assert len(examples) >= 10


def test_components_category_filter_uses_query_param_not_body():
    with TestClient(app) as client:
        response = client.get("/components", params={"category": "sensor"})

    assert response.status_code == 200
    assert response.json()
    assert all(component["category"] == "sensor" for component in response.json())


def test_analyze_endpoint_returns_risk_and_warnings():
    payload = {
        "selected_microcontroller_id": 4,
        "selected_components": [
            {"component_id": 36, "quantity": 2, "powered_from": "external"},
            {"component_id": 43, "quantity": 1},
            {"component_id": 7, "quantity": 1},
        ],
        "selected_power_source_id": 59,
        "settings": {"wifi_enabled": True, "brightness_percent": 100},
    }

    with TestClient(app) as client:
        response = client.post("/analyze", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["current"]["peak_total_mA"] > body["current"]["typical_total_mA"]
    assert "risk" in body
    assert "warnings" in body
    assert "top_fixes" in body


def test_parse_project_description_endpoint():
    with TestClient(app) as client:
        response = client.post(
            "/parse-project-description",
            json={"description": "I want to build an ESP32 robot car with 2 motors, an ultrasonic sensor, and 30 NeoPixels."},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["selected_microcontroller"]["component_id"] == 4
    assert {"component_id": 36, "name": "Small DC Motor", "quantity": 2} in body["selected_components"]
    assert {"component_id": 30, "name": "NeoPixel Strip", "quantity": 30} in body["selected_components"]


def test_generate_report_endpoint_returns_copyable_text():
    payload = {
        "project_name": "Smoke Test Project",
        "selected_microcontroller_id": 1,
        "selected_components": [{"component_id": 27, "quantity": 2}],
        "selected_power_source_id": 58,
    }

    with TestClient(app) as client:
        response = client.post("/generate-report", json=payload)

    assert response.status_code == 200
    assert "PowerCheck AI Report: Smoke Test Project" in response.json()["report"]


def test_estimator_endpoints_return_valid_responses():
    with TestClient(app) as client:
        neopixel = client.post("/estimate-neopixel-current", json={"led_count": 60, "brightness_percent": 50})
        heat = client.post(
            "/estimate-regulator-heat",
            json={
                "regulator_type": "buck",
                "input_voltage": 12,
                "output_voltage": 5,
                "output_current_mA": 1000,
                "efficiency": 0.9,
            },
        )
        battery = client.post(
            "/estimate-battery-life",
            json={"capacity_mAh": 1200, "typical_current_mA": 300, "peak_current_mA": 900},
        )

    assert neopixel.status_code == 200
    assert neopixel.json()["max_current_mA"] == 1800
    assert heat.status_code == 200
    assert heat.json()["loss_watts"] == 0.5
    assert heat.json()["classification"] == "Warm"
    assert battery.status_code == 200
    assert battery.json()["runtime_hours_typical"] == 4.0


def test_openapi_docs_and_ai_description_endpoint_render():
    payload = {
        "project_name": "Bluetooth RC Car",
        "description_text": (
            "I am building a Bluetooth RC car using an Arduino Nano, HC-05 Bluetooth module, "
            "L298N motor driver, 4 TT motors, 2x 18650 batteries, and an LM2596 buck converter."
        ),
    }

    with TestClient(app) as client:
        docs = client.get("/docs")
        openapi = client.get("/openapi.json")
        response = client.post("/analyze-project-description", json=payload)

    assert docs.status_code == 200
    assert openapi.status_code == 200
    assert response.status_code == 200

    body = response.json()
    assert body["project_name"] == "Bluetooth RC Car"
    assert len(body["modules"]) == 8
    assert all(0 <= module["score"] <= 100 for module in body["modules"])
    assert body["final_recommendation"]["overall_score"] == 100 - body["final_recommendation"]["risk_score"]
    assert "next_steps" not in body["final_recommendation"]
    assert any("motor" in part["raw_text"] for part in body["extracted_components"])
