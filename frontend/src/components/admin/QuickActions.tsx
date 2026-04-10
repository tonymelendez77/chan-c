"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";

interface Action {
  label: string;
  onClick: () => Promise<void>;
  variant?: "default" | "green" | "red" | "amber" | "purple";
}

const VARIANTS: Record<string, { bg: string; border: string; text: string }> = {
  default: { bg: "var(--admin-surface)", border: "var(--admin-border)", text: "var(--admin-text)" },
  green: { bg: "var(--admin-green-bg)", border: "var(--admin-green-border)", text: "var(--admin-green)" },
  red: { bg: "var(--admin-red-bg)", border: "var(--admin-red-border)", text: "var(--admin-red)" },
  amber: { bg: "var(--admin-amber-bg)", border: "var(--admin-amber-border)", text: "var(--admin-amber)" },
  purple: { bg: "var(--admin-purple-bg)", border: "var(--admin-purple-border)", text: "var(--admin-purple)" },
};

export default function QuickActions({ actions, title = "Acciones" }: { actions: Action[]; title?: string }) {
  const [loadingIdx, setLoadingIdx] = useState<number | null>(null);

  const handle = async (action: Action, idx: number) => {
    setLoadingIdx(idx);
    try { await action.onClick(); } finally { setLoadingIdx(null); }
  };

  return (
    <div className="rounded-xl" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)", padding: 16 }}>
      <p className="mb-3" style={{ fontSize: 12, fontWeight: 500, color: "var(--admin-muted)" }}>{title}</p>
      <div className="space-y-2">
        {actions.map((a, i) => {
          const v = VARIANTS[a.variant || "default"];
          return (
            <button
              key={a.label}
              onClick={() => handle(a, i)}
              disabled={loadingIdx !== null}
              className="flex items-center justify-center gap-2 w-full rounded-lg py-2.5 text-sm font-medium disabled:opacity-50"
              style={{ background: v.bg, border: `1px solid ${v.border}`, color: v.text }}
            >
              {loadingIdx === i && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
              {a.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
