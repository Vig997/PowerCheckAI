import { Wrench } from "lucide-react";

import type { TopFix } from "../types";

export function RecommendationPanel({ fixes }: { fixes: TopFix[] }) {
  return (
    <section className="panel p-5">
      <div className="flex items-center gap-3">
        <div className="rounded-md bg-cyan-50 p-2 text-cyan-700 dark:bg-cyan-950 dark:text-cyan-200">
          <Wrench className="h-5 w-5" />
        </div>
        <div>
          <p className="label">What should I change?</p>
          <h2 className="text-xl font-bold text-slate-950 dark:text-white">Top fixes</h2>
        </div>
      </div>
      <div className="mt-4 grid gap-3">
        {(fixes.length ? fixes : [{ code: "none", fix: "No fixes needed for this estimate.", difficulty: "Easy", cost: "$" }]).map((fix) => (
          <article key={fix.code} className="rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-900">
            <p className="font-semibold text-slate-950 dark:text-white">{fix.fix}</p>
            <div className="mt-3 flex gap-2 text-xs font-semibold">
              <span className="rounded-full bg-white px-2 py-1 text-slate-900 dark:bg-slate-950 dark:text-slate-300">{fix.difficulty}</span>
              <span className="rounded-full bg-white px-2 py-1 text-slate-900 dark:bg-slate-950 dark:text-slate-300">{fix.cost}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
