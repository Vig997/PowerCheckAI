import type { WarningItem } from "../types";
import { severityTone } from "../utils/format";

const groups = [
  ["critical", "Critical"],
  ["warning", "Warnings"],
  ["suggestion", "Suggestions"],
] as const;

export function WarningList({ warnings }: { warnings: WarningItem[] }) {
  if (warnings.length === 0) {
    return (
      <section className="panel p-5">
        <p className="label">Warnings</p>
        <p className="mt-2 text-sm text-slate-900 dark:text-slate-300">No major warnings for this estimate.</p>
      </section>
    );
  }

  return (
    <section className="panel p-5">
      <p className="label">Warnings</p>
      <div className="mt-4 space-y-5">
        {groups.map(([severity, title]) => {
          const groupWarnings = warnings.filter((warning) => warning.severity === severity);
          if (groupWarnings.length === 0) return null;
          return (
            <div key={severity}>
              <h3 className="font-semibold text-slate-950 dark:text-white">{title}</h3>
              <div className="mt-2 space-y-2">
                {groupWarnings.map((warning, index) => (
                  <article key={`${warning.code}-${index}`} className={`rounded-lg border p-3 ${severityTone(warning.severity)}`}>
                    <div className="font-semibold">{warning.issue}</div>
                    <p className="mt-1 text-sm opacity-90">{warning.why_it_matters}</p>
                    {warning.recommended_fix ? <p className="mt-2 text-sm font-semibold">Fix: {warning.recommended_fix}</p> : null}
                  </article>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
