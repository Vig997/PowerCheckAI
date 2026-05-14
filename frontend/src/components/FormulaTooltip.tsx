import type { ReactNode } from "react";
import { Info } from "lucide-react";

export function FormulaTooltip({ label, children }: { label: string; children: ReactNode }) {
  return (
    <span className="group relative inline-flex items-center gap-1 text-slate-900 dark:text-slate-400">
      {label}
      <Info className="h-3.5 w-3.5" />
      <span className="pointer-events-none absolute bottom-full left-0 z-20 mb-2 hidden w-64 rounded-md border border-slate-200 bg-white p-3 text-xs leading-5 text-slate-950 shadow-soft group-hover:block dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200">
        {children}
      </span>
    </span>
  );
}
