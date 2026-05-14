import { ClipboardCopy } from "lucide-react";
import { useState } from "react";

import { api } from "../api/client";
import type { ProjectConfig } from "../types";

export function CopyReportButton({ project, disabled }: { project: ProjectConfig; disabled?: boolean }) {
  const [status, setStatus] = useState<"idle" | "copied" | "error">("idle");

  async function copyReport() {
    try {
      const response = await api.generateReport(project);
      await navigator.clipboard.writeText(response.report);
      setStatus("copied");
    } catch {
      setStatus("error");
    }
  }

  return (
    <button type="button" className="button-primary" onClick={copyReport} disabled={disabled}>
      <ClipboardCopy className="h-4 w-4" />
      {status === "copied" ? "Copied" : status === "error" ? "Copy failed" : "Copy Report"}
    </button>
  );
}
