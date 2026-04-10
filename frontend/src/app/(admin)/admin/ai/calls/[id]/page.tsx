"use client";

import { useEffect, useState } from "react";
import { use } from "react";
import PageHeader from "@/components/admin/PageHeader";
import StatusBadge from "@/components/admin/StatusBadge";
import TranscriptViewer from "@/components/admin/TranscriptViewer";
import QuickActions from "@/components/admin/QuickActions";
import { fetchAICall, reviewExtraction } from "@/lib/admin-api";

interface Extraction { id: string; can_cover?: string[]; cannot_cover?: string[]; counteroffer_price?: number; counteroffer_dates?: string; counteroffer_notes?: string; availability_notes?: string; final_status?: string; confidence_score?: number; requires_admin_review: boolean; extraction_model?: string; }
interface CallDetail { id: string; worker_name: string; worker_phone: string; call_type: string; status: string; vapi_call_id?: string; duration_seconds?: number; transcript?: string; recording_url?: string; started_at?: string; ended_at?: string; created_at: string; extractions: Extraction[]; }

export default function AICallDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [call, setCall] = useState<CallDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchAICall(id).then(setCall).catch(() => {}).finally(() => setLoading(false)); }, [id]);

  if (loading) return <div style={{ color: "var(--admin-muted)", padding: 40 }}>Cargando...</div>;
  if (!call) return <div style={{ color: "var(--admin-muted)", padding: 40 }}>Llamada no encontrada</div>;

  const ext = call.extractions[0];
  const confidence = ext?.confidence_score ?? 0;

  return (
    <div>
      <PageHeader title={`Llamada ${String(call.id).slice(0, 8)}`} subtitle={call.worker_name} backHref="/admin/ai/calls">
        <StatusBadge status={call.call_type} type="callType" />
        <StatusBadge status={call.status} type="call" />
      </PageHeader>

      <div className="grid grid-cols-1 xl:grid-cols-[2fr_1fr] gap-6">
        <div className="space-y-4">
          {/* Transcript */}
          {call.transcript ? (
            <TranscriptViewer transcript={call.transcript} />
          ) : (
            <div className="rounded-xl p-6 text-center" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
              <p style={{ fontSize: 14, color: "var(--admin-muted)" }}>Transcripción no disponible</p>
            </div>
          )}

          {/* Extraction */}
          {ext && (
            <div className="rounded-xl p-5" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
              <div className="flex items-center justify-between mb-4">
                <p style={{ fontSize: 14, fontWeight: 600, color: "var(--admin-text)" }}>Datos extraídos</p>
                <StatusBadge status="" label={`Confianza: ${(confidence * 100).toFixed(0)}%`} color={confidence >= 0.8 ? "green" : confidence >= 0.6 ? "amber" : "red"} />
              </div>
              <div className="space-y-2">
                {ext.can_cover && ext.can_cover.length > 0 && (
                  <div>
                    <p style={{ fontSize: 12, color: "var(--admin-dim)" }}>Puede cubrir</p>
                    <div className="flex flex-wrap gap-1 mt-1">{ext.can_cover.map((c) => <span key={c} className="rounded px-2 py-0.5" style={{ fontSize: 11, background: "var(--admin-green-bg)", border: "1px solid var(--admin-green-border)", color: "var(--admin-green)" }}>✓ {c}</span>)}</div>
                  </div>
                )}
                {ext.cannot_cover && ext.cannot_cover.length > 0 && (
                  <div>
                    <p style={{ fontSize: 12, color: "var(--admin-dim)" }}>No puede cubrir</p>
                    <div className="flex flex-wrap gap-1 mt-1">{ext.cannot_cover.map((c) => <span key={c} className="rounded px-2 py-0.5" style={{ fontSize: 11, background: "var(--admin-red-bg)", border: "1px solid var(--admin-red-border)", color: "var(--admin-red)" }}>✗ {c}</span>)}</div>
                  </div>
                )}
                {ext.availability_notes && <div><p style={{ fontSize: 12, color: "var(--admin-dim)" }}>Disponibilidad</p><p style={{ fontSize: 13, color: "var(--admin-text)" }}>{ext.availability_notes}</p></div>}
                {ext.counteroffer_price && <div><p style={{ fontSize: 12, color: "var(--admin-dim)" }}>Precio propuesto</p><p className="font-mono" style={{ fontSize: 14, fontWeight: 600, color: "var(--admin-amber)" }}>Q{ext.counteroffer_price}/día</p></div>}
                {ext.counteroffer_notes && <div><p style={{ fontSize: 12, color: "var(--admin-dim)" }}>Notas contrapropuesta</p><p style={{ fontSize: 13, color: "var(--admin-text)" }}>{ext.counteroffer_notes}</p></div>}
              </div>
              {ext.requires_admin_review && (
                <div className="mt-4 pt-4" style={{ borderTop: "1px solid var(--admin-border)" }}>
                  <StatusBadge status="" label="Requiere revisión manual" color="red" />
                </div>
              )}
            </div>
          )}
        </div>

        <div className="space-y-4">
          {/* Metadata */}
          <div className="rounded-xl p-4" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
            <p className="mb-3" style={{ fontSize: 12, fontWeight: 500, color: "var(--admin-muted)" }}>Metadatos</p>
            {[
              ["Duración", call.duration_seconds ? `${Math.floor(call.duration_seconds / 60)}:${String(call.duration_seconds % 60).padStart(2, "0")}` : "—"],
              ["Vapi ID", call.vapi_call_id || "—"],
              ["Modelo", ext?.extraction_model || "—"],
              ["Iniciada", call.started_at ? new Date(call.started_at).toLocaleString("es-GT") : "—"],
              ["Finalizada", call.ended_at ? new Date(call.ended_at).toLocaleString("es-GT") : "—"],
            ].map(([k, v]) => (
              <div key={k as string} className="flex justify-between py-1.5" style={{ fontSize: 12, borderBottom: "1px solid var(--admin-border)" }}>
                <span style={{ color: "var(--admin-dim)" }}>{k}</span>
                <span className="font-mono" style={{ color: "var(--admin-text)" }}>{v}</span>
              </div>
            ))}
          </div>

          <QuickActions actions={[
            ...(ext?.requires_admin_review ? [{ label: "Marcar como revisado", onClick: async () => { await reviewExtraction(call.id, {}); }, variant: "green" as const }] : []),
            { label: "Ver trabajador", onClick: async () => {}, variant: "default" as const },
          ]} />
        </div>
      </div>
    </div>
  );
}
