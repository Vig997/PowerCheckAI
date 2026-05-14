import { Battery } from "lucide-react";

import type { AnalysisResult } from "../types";
import { formatRuntime } from "../utils/format";
import { SummaryCard } from "./SummaryCard";

export function BatteryLifeCard({ analysis }: { analysis: AnalysisResult }) {
  const battery = analysis.battery_life;
  return (
    <SummaryCard
      title="Battery Life"
      icon={<Battery className="h-5 w-5" />}
      value={battery.is_wall_powered ? "Wall powered" : formatRuntime(battery.runtime_hours_typical)}
      detail={
        battery.is_wall_powered
          ? "Runtime estimate is not needed for USB or wall power."
          : `Worst case: ${formatRuntime(battery.runtime_hours_worst)}`
      }
    />
  );
}
