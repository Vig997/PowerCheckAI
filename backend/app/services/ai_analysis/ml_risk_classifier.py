from __future__ import annotations

from functools import lru_cache

from app.analysis_engine import classify_risk


FEATURE_KEYS = [
    "total_typical_current",
    "peak_current",
    "supply_current_rating",
    "current_margin",
    "number_of_motors",
    "number_of_servos",
    "led_count",
    "has_esp32",
    "has_arduino",
    "has_wifi",
    "has_camera",
    "has_inductive_load",
    "has_external_driver",
    "has_regulator",
    "voltage_mismatch_count",
    "gpio_risk_count",
    "brownout_risk",
    "regulator_heat",
]


def _feature_vector(features: dict) -> list[float]:
    vector = []
    for key in FEATURE_KEYS:
        value = features.get(key, 0)
        vector.append(float(value is True) if isinstance(value, bool) else float(value or 0))
    vector.append(1.0 if features.get("battery_type") == "battery" else 0.0)
    return vector


def _fallback_score(features: dict, deterministic_risk: dict) -> int:
    score = deterministic_risk.get("score", 0)
    if features["number_of_motors"] and not features["has_external_driver"]:
        score += 20
    if features["led_count"] >= 60:
        score += 12
    if features["has_esp32"] and features["voltage_mismatch_count"]:
        score += 15
    if features["current_margin"] < 0:
        score += 25
    return min(100, int(score))


@lru_cache(maxsize=1)
def _train_random_forest():
    try:
        from sklearn.ensemble import RandomForestClassifier
    except Exception:
        return None

    rows: list[list[float]] = []
    labels: list[str] = []
    for motors in range(0, 5):
        for servos in range(0, 5):
            for leds in (0, 8, 30, 60, 120):
                for supply in (500, 1000, 2000, 5000, 10000):
                    peak = 120 + motors * 1000 + servos * 700 + leds * 60
                    typical = 70 + motors * 200 + servos * 250 + leds * 20
                    features = {
                        "total_typical_current": typical,
                        "peak_current": peak,
                        "supply_current_rating": supply,
                        "current_margin": supply - peak,
                        "number_of_motors": motors,
                        "number_of_servos": servos,
                        "led_count": leds,
                        "has_esp32": 1,
                        "has_arduino": 0,
                        "has_wifi": 1,
                        "has_camera": 0,
                        "has_inductive_load": motors > 0,
                        "has_external_driver": motors == 0 or supply >= 1000,
                        "has_regulator": supply != 500,
                        "voltage_mismatch_count": 0 if supply >= 1000 else 1,
                        "gpio_risk_count": 0 if motors == 0 else 1,
                        "brownout_risk": supply < peak * 1.2,
                        "regulator_heat": 0.4 if supply >= 2000 else 1.8,
                        "battery_type": "adapter",
                    }
                    score = 0
                    if supply < peak:
                        score += 35
                    elif supply < peak * 1.2:
                        score += 20
                    if motors and not features["has_external_driver"]:
                        score += 25
                    if servos > 1:
                        score += 18
                    if leds >= 60:
                        score += 18
                    if features["brownout_risk"]:
                        score += 20
                    score = min(100, score)
                    rows.append(_feature_vector(features))
                    labels.append(classify_risk(score))
    model = RandomForestClassifier(n_estimators=80, random_state=42, max_depth=8)
    model.fit(rows, labels)
    return model


def classify_project_risk(features: dict, deterministic_risk: dict) -> dict:
    model = _train_random_forest()
    fallback_score = _fallback_score(features, deterministic_risk)
    fallback_label = classify_risk(fallback_score)
    if model is None:
        return {"score": fallback_score, "label": fallback_label, "confidence": 0.72 if fallback_score else 0.62, "model": "rule-fallback"}

    probabilities = model.predict_proba([_feature_vector(features)])[0]
    predicted_label = str(model.predict([_feature_vector(features)])[0])
    confidence = float(max(probabilities))

    # Deterministic EE checks remain authoritative; the ML label is used as a consistency check.
    severity_rank = {"Safe": 0, "Borderline": 1, "Unsafe": 2}
    label = fallback_label
    if severity_rank.get(predicted_label, 0) > severity_rank.get(fallback_label, 0) and confidence > 0.78:
        label = predicted_label
    return {"score": fallback_score, "label": label, "confidence": round(confidence, 2), "model": "synthetic-random-forest"}
