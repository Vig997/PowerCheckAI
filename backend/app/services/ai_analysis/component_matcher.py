from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any

from .schemas import ExtractedComponent
from .utils import model_to_dict


def _similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, left.lower(), right.lower()).ratio()


def match_components(extracted: list[ExtractedComponent], components: list[Any]) -> tuple[list[dict], list[dict]]:
    component_dicts = [model_to_dict(component) for component in components]
    matched: list[dict] = []
    unmatched: list[dict] = []

    for item in extracted:
        if item.category == "power":
            unmatched.append({**item.model_dump(), "reason": "power_source_candidate"})
            continue

        exact = next((component for component in component_dicts if component["name"].lower() == item.normalized_name.lower()), None)
        if exact:
            matched.append({"extracted": item.model_dump(), "component": exact, "match_type": "alias/exact", "confidence": item.confidence})
            continue

        scored = sorted(
            ((_similarity(item.normalized_name, component["name"]), component) for component in component_dicts),
            key=lambda pair: pair[0],
            reverse=True,
        )
        best_score, best_component = scored[0]
        if best_score >= 0.62:
            matched.append({"extracted": item.model_dump(), "component": best_component, "match_type": "fuzzy", "confidence": round(best_score, 2)})
        else:
            unmatched.append({**item.model_dump(), "reason": "no_database_match"})

    return matched, unmatched
