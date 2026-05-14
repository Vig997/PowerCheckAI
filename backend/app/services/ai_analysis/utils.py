from typing import Any


def model_to_dict(model: Any) -> dict[str, Any]:
    return {column.name: getattr(model, column.name) for column in model.__table__.columns}


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def status_from_score(score: int) -> str:
    if score <= 30:
        return "safe"
    if score <= 65:
        return "warning"
    return "danger"


def severity_from_score(score: int) -> str:
    if score <= 30:
        return "low"
    if score <= 65:
        return "medium"
    return "high"
