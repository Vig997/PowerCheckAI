from __future__ import annotations

import re

from .aliases import ALIASES, CATEGORY_HINTS
from .regex_patterns import CAPACITY_RE, CURRENT_RE, LED_COUNT_RE, VOLTAGE_RE, parse_quantity
from .schemas import ExtractedComponent


def _guess_category(text: str) -> str:
    lowered = text.lower()
    for category, hints in CATEGORY_HINTS.items():
        if any(hint in lowered for hint in hints):
            return category
    return "unknown"


def _specs(text: str) -> tuple[float | None, float | None, float | None]:
    voltage = None
    current = None
    capacity = None
    if match := VOLTAGE_RE.search(text):
        voltage = float(match.group("value"))
    if match := CURRENT_RE.search(text):
        value = float(match.group("value"))
        current = value * 1000 if match.group("unit").lower() == "a" else value
    if match := CAPACITY_RE.search(text):
        capacity = float(match.group("value"))
    return voltage, current, capacity


def extract_components(description_text: str) -> list[ExtractedComponent]:
    text = description_text.replace("\u2192", " to ").replace("->", " to ")
    lowered = text.lower()
    extracted: list[ExtractedComponent] = []
    seen: set[tuple[str, int]] = set()

    for alias, canonical in sorted(ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        pattern = re.compile(rf"(?P<context>(?:\d+\s*x\s+|\d+\s+|\(x\d+\)\s+)?[^\n,.;]*{re.escape(alias)}[^\n,.;]*)", re.I)
        for match in pattern.finditer(lowered):
            context = match.group("context").strip()
            quantity = parse_quantity(context)
            if "neopixel" in context or "ws2812" in context or "led strip" in context:
                if led_match := LED_COUNT_RE.search(context):
                    quantity = int(led_match.group("count"))
            voltage, current, capacity = _specs(context)
            key = (canonical, quantity)
            if key in seen:
                continue
            seen.add(key)
            extracted.append(
                ExtractedComponent(
                    raw_text=context,
                    normalized_name=canonical,
                    category=_guess_category(context),
                    quantity=quantity,
                    voltage=voltage,
                    current_mA=current,
                    capacity_mAh=capacity,
                    confidence=0.9,
                )
            )

    # Power supplies and batteries may not exist in the component DB, but they are crucial for analysis.
    for power_match in re.finditer(r"(?P<context>[^\n,.;]*(?:battery|adapter|power supply|18650|lipo|li-ion|usb-c|usb)[^\n,.;]*)", lowered, re.I):
        context = power_match.group("context").strip()
        if not context or any(item.raw_text == context for item in extracted):
            continue
        voltage, current, capacity = _specs(context)
        extracted.append(
            ExtractedComponent(
                raw_text=context,
                normalized_name=context,
                category="power",
                quantity=parse_quantity(context),
                voltage=voltage,
                current_mA=current,
                capacity_mAh=capacity,
                confidence=0.65,
            )
        )

    return extracted
