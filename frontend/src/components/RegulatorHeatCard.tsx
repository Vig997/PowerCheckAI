import { Thermometer } from "lucide-react";

import type { AnalysisResult } from "../types";
import { SummaryCard } from "./SummaryCard";

export function RegulatorHeatCard({ analysis }: { analysis: AnalysisResult }) {
  const heat = analysis.regulator_heat;
  const present = Boolean(heat.present);
  if (!present) {
    return <SummaryCard title="Regulator Heat" icon={<Thermometer className="h-5 w-5" />} value="No regulator" detail="No converter selected." />;
  }
  const watts = (heat.heat_watts ?? heat.loss_watts) as number | undefined;
  return (
    <SummaryCard
      title="Regulator Heat"
      icon={<Thermometer className="h-5 w-5" />}
      value={String(heat.classification ?? "Unknown")}
      detail={typeof watts === "number" ? `${watts.toFixed(2)} W estimated heat/loss` : "Estimate available from selected converter."}
    />
  );
}
