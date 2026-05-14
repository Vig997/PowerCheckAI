import { riskTone } from "../utils/format";

export function RiskBadge({ label, score }: { label: string; score?: number }) {
  const safetyScore = typeof score === "number" ? Math.max(0, Math.min(100, 100 - score)) : null;
  return (
    <span className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm font-semibold ${safetyScore === null ? riskTone(label) : scoreTone(safetyScore)}`}>
      <span className="h-2 w-2 rounded-full bg-current" />
      {label}
      {safetyScore !== null ? <span className="text-xs opacity-75">{safetyScore}/100</span> : null}
    </span>
  );
}

function scoreTone(score: number): string {
  if (score >= 70) {
    return "border-green-300 bg-green-100 text-green-900 dark:border-green-300/40 dark:bg-green-400/15 dark:text-green-100";
  }
  if (score >= 30) {
    return "border-yellow-300 bg-yellow-100 text-yellow-900 dark:border-yellow-300/40 dark:bg-yellow-400/15 dark:text-yellow-100";
  }
  return "border-red-300 bg-red-100 text-red-900 dark:border-red-300/40 dark:bg-red-400/15 dark:text-red-100";
}
