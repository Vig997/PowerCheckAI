import type { AnalysisResult, PowerSource } from "../types";
import { formatCurrent, formatRuntime } from "../utils/format";
import { RiskBadge } from "./RiskBadge";

export function PowerSourceComparison({ analysis, powerSources }: { analysis: AnalysisResult; powerSources: PowerSource[] }) {
  const names = ["USB 5V 500mA", "5V Wall Adapter 2A", "5V Wall Adapter 5A", "9V Rectangular Battery", "2S LiPo Battery"];
  const rows = powerSources
    .filter((source) => names.includes(source.name))
    .map((source) => {
      const peak = analysis.current.peak_total_mA;
      const recommended = analysis.current.recommended_current_mA;
      const label = source.max_current_mA < peak ? "Unsafe" : source.max_current_mA < recommended ? "Borderline" : "Safe";
      const runtime = source.capacity_mAh ? source.capacity_mAh / Math.max(analysis.current.typical_total_mA, 1) : null;
      return { source, label, runtime };
    });

  return (
    <section className="panel p-5">
      <p className="label">Power Source Comparison</p>
      <div className="mt-4 grid gap-3">
        {rows.map(({ source, label, runtime }) => (
          <div key={source.id} className="flex flex-col gap-3 rounded-lg border border-slate-200 p-3 dark:border-slate-800 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="font-semibold text-slate-950 dark:text-white">{source.name}</div>
              <div className="text-sm text-slate-900">
                {formatCurrent(source.max_current_mA)} available {runtime ? `- ${formatRuntime(runtime)} typical` : "- wall powered"}
              </div>
            </div>
            <RiskBadge label={label} />
          </div>
        ))}
      </div>
    </section>
  );
}
