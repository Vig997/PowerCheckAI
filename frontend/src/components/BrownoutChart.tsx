import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { AnalysisResult } from "../types";

export function BrownoutChart({ analysis }: { analysis: AnalysisResult }) {
  const nominal = analysis.regulated_voltage || analysis.power_source.voltage || 5;
  const resistance = analysis.power_source.internal_resistance_ohm ?? 0.08;
  const peakA = analysis.current.peak_total_mA / 1000;
  const typicalA = analysis.current.typical_total_mA / 1000;
  const data = Array.from({ length: 26 }, (_, index) => {
    const t = index / 5;
    const spike =
      Math.abs(t - 0.5) < 0.12 || Math.abs(t - 1.5) < 0.12 || Math.abs(t - 3.0) < 0.12 || Math.abs(t - 2.0) < 0.12;
    const currentA = spike ? peakA : typicalA + (index % 4) * 0.03;
    return {
      time: t.toFixed(1),
      voltage: Number(Math.max(0, nominal - currentA * resistance).toFixed(2)),
      current: Number((currentA * 1000).toFixed(0)),
    };
  });

  return (
    <section className="panel p-5">
      <p className="label">Voltage Sag</p>
      <div className="mt-4 h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
            <XAxis dataKey="time" tick={{ fontSize: 12 }} />
            <YAxis domain={["dataMin - 0.1", "dataMax + 0.1"]} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Line type="monotone" dataKey="voltage" stroke="#0f766e" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
