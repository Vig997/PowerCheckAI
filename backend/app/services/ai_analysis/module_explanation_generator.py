from __future__ import annotations


def warning_explanation(warning: dict) -> str:
    issue = warning.get("issue", "PowerCheck found a possible electrical issue.")
    why = warning.get("why_it_matters", "This can make the project unreliable or unsafe.")
    symptoms = ", ".join(warning.get("likely_symptoms", []) or ["unstable behavior"])
    fix = warning.get("recommended_fix", "Check datasheets and use a safer power path.")
    return (
        f"Issue: {issue}\n"
        f"Why it matters: {why}\n"
        f"Likely symptoms: {symptoms}.\n"
        f"Recommended fix: {fix}"
    )


def top_warning_text(warnings: list[dict], fallback: str) -> str:
    if not warnings:
        return fallback
    return warning_explanation(warnings[0])


def join_fixes(warnings: list[dict], extra: list[str] | None = None) -> list[str]:
    fixes = []
    for warning in warnings:
        fix = warning.get("recommended_fix")
        if fix and fix not in fixes:
            fixes.append(fix)
    for fix in extra or []:
        if fix not in fixes:
            fixes.append(fix)
    return fixes[:5]
