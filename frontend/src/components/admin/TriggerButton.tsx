"use client";

import { useState } from "react";
import { Loader2, Play, CheckCircle, XCircle } from "lucide-react";

interface TriggerButtonProps {
  label: string;
  subtitle?: string;
  onTrigger: () => Promise<{ count?: number; detail?: string }>;
}

export default function TriggerButton({ label, subtitle, onTrigger }: TriggerButtonProps) {
  const [state, setState] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [result, setResult] = useState("");

  const handleClick = async () => {
    setState("loading");
    try {
      const res = await onTrigger();
      setResult(res.detail || `${res.count ?? 0} procesados`);
      setState("success");
      setTimeout(() => setState("idle"), 3000);
    } catch {
      setResult("Error al ejecutar");
      setState("error");
      setTimeout(() => setState("idle"), 3000);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={state === "loading"}
      className="flex items-center gap-3 rounded-xl px-5 py-3.5 text-left w-full disabled:opacity-60"
      style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)", transition: "all 0.15s" }}
    >
      <div className="shrink-0 flex items-center justify-center rounded-lg w-9 h-9" style={{ background: "var(--admin-amber-bg)", border: "1px solid var(--admin-amber-border)" }}>
        {state === "loading" ? <Loader2 className="h-4 w-4 animate-spin" style={{ color: "var(--admin-amber)" }} /> :
         state === "success" ? <CheckCircle className="h-4 w-4" style={{ color: "var(--admin-green)" }} /> :
         state === "error" ? <XCircle className="h-4 w-4" style={{ color: "var(--admin-red)" }} /> :
         <Play className="h-4 w-4" style={{ color: "var(--admin-amber)" }} />}
      </div>
      <div className="flex-1 min-w-0">
        <p style={{ fontSize: 14, fontWeight: 500, color: "var(--admin-text)" }}>{label}</p>
        <p style={{ fontSize: 12, color: "var(--admin-muted)" }}>
          {state === "success" || state === "error" ? result : subtitle}
        </p>
      </div>
    </button>
  );
}
