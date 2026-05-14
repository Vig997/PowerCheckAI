import type { ReactNode } from "react";

export function SummaryCard({
  title,
  value,
  detail,
  icon,
}: {
  title: string;
  value: ReactNode;
  detail?: ReactNode;
  icon?: ReactNode;
}) {
  return (
    <section className="panel p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="label">{title}</p>
          <div className="mt-2 text-2xl font-bold text-slate-950 dark:text-white">{value}</div>
          {detail ? <div className="mt-2 text-sm text-slate-900 dark:text-slate-400">{detail}</div> : null}
        </div>
        {icon ? <div className="rounded-md bg-slate-100 p-2 text-slate-900 dark:bg-slate-900 dark:text-cyan-300">{icon}</div> : null}
      </div>
    </section>
  );
}
