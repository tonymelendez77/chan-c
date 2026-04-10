"use client";

import { useEffect, useState } from "react";
import { use } from "react";
import PageHeader from "@/components/admin/PageHeader";
import StatusBadge from "@/components/admin/StatusBadge";
import QuickActions from "@/components/admin/QuickActions";
import { fetchMatch, updateMatchStatus, sendJobOffer } from "@/lib/admin-api";
import type { Match } from "@/lib/types";

export default function AdminMatchDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [match, setMatch] = useState<Match | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMatch(id).then(setMatch).catch(() => {}).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div style={{ color: "var(--admin-muted)", padding: 40 }}>Cargando...</div>;
  if (!match) return <div style={{ color: "var(--admin-muted)", padding: 40 }}>Match no encontrado</div>;

  const actions = [
    ...(match.status === "pending_company" ? [
      { label: "Notificar empresa", onClick: async () => {}, variant: "amber" as const },
    ] : []),
    ...(match.status === "pending_worker" || match.status === "pending_company" ? [
      { label: "Reenviar SMS", onClick: async () => { await sendJobOffer(match.id); }, variant: "default" as const },
    ] : []),
    { label: "Cambiar estado", onClick: async () => {}, variant: "default" as const },
  ];

  return (
    <div>
      <PageHeader title={`Match ${String(match.id).slice(0, 8)}`} subtitle={`${match.worker_name || "Trabajador"} → ${match.job_title || "Trabajo"}`} backHref="/admin/matches" />

      <div className="grid grid-cols-1 xl:grid-cols-[2fr_1fr] gap-6">
        <div className="space-y-4">
          {/* Details */}
          <div className="rounded-xl p-5" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
            <div className="flex items-center gap-3 mb-4">
              <StatusBadge status={match.status} type="match" />
              {match.worker_reply && <span className="font-mono text-xs" style={{ color: "var(--admin-dim)" }}>reply: {match.worker_reply}</span>}
            </div>
            <div className="grid grid-cols-2 gap-4">
              {[
                ["Trabajador", match.worker_name || "—"],
                ["Trabajo", match.job_title || "—"],
                ["Empresa", match.company_name || "—"],
                ["Tarifa ofrecida", `Q${match.offered_rate}/día`],
                ["Tarifa final", match.final_rate ? `Q${match.final_rate}/día` : "—"],
                ["Creado", new Date(match.created_at).toLocaleDateString("es-GT")],
              ].map(([k, v]) => (
                <div key={k as string}>
                  <p style={{ fontSize: 12, color: "var(--admin-dim)" }}>{k}</p>
                  <p className="font-mono" style={{ fontSize: 13, fontWeight: 500, color: "var(--admin-text)" }}>{v}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Timeline placeholder */}
          <div className="rounded-xl p-5" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
            <p style={{ fontSize: 13, fontWeight: 500, color: "var(--admin-text)", marginBottom: 12 }}>Línea de tiempo</p>
            <div className="space-y-3">
              <div className="flex gap-3">
                <div className="w-2 h-2 rounded-full mt-1.5" style={{ background: "var(--admin-green)" }} />
                <div>
                  <p style={{ fontSize: 13, color: "var(--admin-text)" }}>Match creado</p>
                  <p className="font-mono" style={{ fontSize: 11, color: "var(--admin-dim)" }}>{new Date(match.created_at).toLocaleString("es-GT")}</p>
                </div>
              </div>
              {match.worker_sms_sent_at && (
                <div className="flex gap-3">
                  <div className="w-2 h-2 rounded-full mt-1.5" style={{ background: "var(--admin-blue)" }} />
                  <div>
                    <p style={{ fontSize: 13, color: "var(--admin-text)" }}>SMS enviado al trabajador</p>
                    <p className="font-mono" style={{ fontSize: 11, color: "var(--admin-dim)" }}>{new Date(match.worker_sms_sent_at).toLocaleString("es-GT")}</p>
                  </div>
                </div>
              )}
              {match.worker_replied_at && (
                <div className="flex gap-3">
                  <div className="w-2 h-2 rounded-full mt-1.5" style={{ background: "var(--admin-amber)" }} />
                  <div>
                    <p style={{ fontSize: 13, color: "var(--admin-text)" }}>Trabajador respondió: {match.worker_reply}</p>
                    <p className="font-mono" style={{ fontSize: 11, color: "var(--admin-dim)" }}>{new Date(match.worker_replied_at).toLocaleString("es-GT")}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <QuickActions actions={actions} />
        </div>
      </div>
    </div>
  );
}
