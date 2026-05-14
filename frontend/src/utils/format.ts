export function formatCurrent(value: number | null | undefined): string {
  if (value == null) return "n/a";
  if (Math.abs(value) >= 1000) return `${(value / 1000).toFixed(2)} A`;
  return `${Math.round(value)} mA`;
}

export function formatVoltage(value: number | null | undefined): string {
  if (value == null) return "n/a";
  return `${value.toFixed(value % 1 === 0 ? 0 : 1)} V`;
}

export function formatRuntime(value: number | null | undefined): string {
  if (value == null) return "wall powered";
  if (value < 1) return `${Math.round(value * 60)} min`;
  return `${value.toFixed(1)} h`;
}

export function riskTone(label: string): string {
  if (label === "Safe") return "bg-green-100 text-green-800 border-green-200 dark:bg-green-950 dark:text-green-200 dark:border-green-800";
  if (label === "Borderline")
    return "bg-amber-100 text-amber-900 border-amber-200 dark:bg-amber-950 dark:text-amber-200 dark:border-amber-800";
  return "bg-red-100 text-red-800 border-red-200 dark:bg-red-950 dark:text-red-200 dark:border-red-800";
}

export function severityTone(severity: string): string {
  if (severity === "critical") return "border-red-300 bg-red-50 text-red-900 dark:border-red-900 dark:bg-red-950 dark:text-red-100";
  if (severity === "warning") return "border-amber-300 bg-amber-50 text-amber-950 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-100";
  return "border-sky-200 bg-sky-50 text-sky-950 dark:border-sky-900 dark:bg-sky-950 dark:text-sky-100";
}
