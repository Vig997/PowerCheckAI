import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { AnalysisResult } from "../types";

export function CurrentChart({ analysis }: { analysis: AnalysisResult }) {
  const data = analysis.current.line_items.map((item) => ({
    name: item.name.length > 18 ? `${item.name.slice(0, 18)}...` : item.name,
    Typical: item.typical_mA,
    Peak: item.peak_mA,
  }));

  return (
    <section className="panel p-5">
      <p className="label">Current Draw</p>
      <div className="mt-4 h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey="Typical" fill="#0891b2" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Peak" fill="#f97316" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
