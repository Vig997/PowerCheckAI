from __future__ import annotations


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
