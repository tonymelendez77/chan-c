"use client";

import { useEffect, useState } from "react";
import { use } from "react";
import PageHeader from "@/components/admin/PageHeader";
import StatusBadge from "@/components/admin/StatusBadge";
import QuickActions from "@/components/admin/QuickActions";
import AdminNotes from "@/components/admin/AdminNotes";
import ManualRegistrationDrawer from "@/components/admin/ManualRegistrationDrawer";
import { fetchWorker, sendTestSMS, approveWorker, updateWorkerManual } from "@/lib/admin-api";
import { TRADE_LABELS, SKILL_LABELS, type Worker } from "@/lib/types";

export default function AdminWorkerDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [worker, setWorker] = useState<Worker | null>(null);
  const [loading, setLoading] = useState(true);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const reload = () => fetchWorker(id).then(setWorker).catch(() => {});

  useEffect(() => { fetchWorker(id).then(setWorker).catch(() => {}).finally(() => setLoading(false)); }, [id]);

  if (loading) return <div style={{ color: "var(--admin-muted)", padding: 40 }}>Cargando...</div>;
  if (!worker) return <div style={{ color: "var(--admin-muted)", padding: 40 }}>Trabajador no encontrado</div>;

  return (
    <div>
      <PageHeader title={worker.full_name} subtitle={`Zona ${worker.zone} · ${worker.phone}`} backHref="/admin/workers">
        {worker.paused ? <StatusBadge status="" label="⏸️ Pausado" color="amber" /> :
         worker.is_active && worker.is_vetted ? <StatusBadge status="" label="Activo" color="green" /> :
         worker.is_active ? <StatusBadge status="" label="Sin vetar" color="amber" /> :
         <StatusBadge status="" label="Inactivo" color="red" />}
      </PageHeader>

      {worker.paused && (
        <div className="flex items-center justify-between rounded-xl px-5 py-3 mb-6" style={{ background: "var(--admin-amber-bg)", border: "1px solid var(--admin-amber-border)" }}>
          <p style={{ fontSize: 14, color: "var(--admin-amber)" }}>⏸️ Este trabajador pausó sus ofertas{worker.paused_reason ? ` — ${worker.paused_reason}` : ""}</p>
          <button onClick={async () => { await updateWorkerManual(worker.id, { paused: false, is_available: true }); reload(); }} className="rounded-lg px-3 py-1.5 text-xs font-medium" style={{ background: "var(--admin-green-bg)", border: "1px solid var(--admin-green-border)", color: "var(--admin-green)" }}>Reactivar manualmente</button>
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-[2fr_1fr] gap-6">
        <div className="space-y-4">
          {/* Profile */}
          <div className="rounded-xl p-5" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
            <div className="flex items-center gap-4 mb-4">
              <div className="flex items-center justify-center rounded-2xl text-white text-xl font-bold" style={{ width: 64, height: 64, background: worker.is_active ? "var(--admin-green)" : "var(--admin-dim)" }}>{worker.full_name.charAt(0)}</div>
              <div>
                <p style={{ fontSize: 18, fontWeight: 600, color: "var(--admin-text)" }}>{worker.full_name}</p>
                <p className="font-mono" style={{ fontSize: 13, color: "var(--admin-muted)" }}>{worker.phone}</p>
                <p style={{ fontSize: 13, color: "var(--admin-muted)" }}>DPI: {worker.dpi || "—"} · Idioma: {worker.language}</p>
              </div>
            </div>
            <div className="grid grid-cols-4 gap-4 pt-4" style={{ borderTop: "1px solid var(--admin-border)" }}>
              {[
                ["Rating", `★ ${Number(worker.rating_avg).toFixed(1)}`],
                ["Trabajos", String(worker.total_jobs)],
                ["Disponible", worker.is_available ? "Sí" : "No"],
                ["Miembro desde", new Date(worker.created_at).toLocaleDateString("es-GT")],
              ].map(([k, v]) => (
                <div key={k as string}>
                  <p style={{ fontSize: 11, color: "var(--admin-dim)" }}>{k}</p>
                  <p className="font-mono" style={{ fontSize: 14, fontWeight: 600, color: "var(--admin-text)" }}>{v}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Trades */}
          {worker.trades && worker.trades.length > 0 && (
            <div className="rounded-xl p-5" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
              <p className="mb-3" style={{ fontSize: 14, fontWeight: 500, color: "var(--admin-text)" }}>Oficios</p>
              {worker.trades.map((t) => (
                <div key={t.id} className="mb-3 last:mb-0">
                  <div className="flex items-center gap-2 mb-2">
                    <StatusBadge status="" label={TRADE_LABELS[t.trade]} color="blue" />
                    <span style={{ fontSize: 12, color: "var(--admin-muted)" }}>{SKILL_LABELS[t.skill_level]} · {t.years_experience} años</span>
                  </div>
                  {t.can_cover && t.can_cover.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-1">
                      {t.can_cover.map((c) => <span key={c} className="rounded px-2 py-0.5" style={{ fontSize: 11, background: "var(--admin-green-bg)", border: "1px solid var(--admin-green-border)", color: "var(--admin-green)" }}>✓ {c}</span>)}
                    </div>
                  )}
                  {t.cannot_cover && t.cannot_cover.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {t.cannot_cover.map((c) => <span key={c} className="rounded px-2 py-0.5" style={{ fontSize: 11, background: "var(--admin-red-bg)", border: "1px solid var(--admin-red-border)", color: "var(--admin-red)" }}>✗ {c}</span>)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Bio */}
          {worker.profile?.bio && (
            <div className="rounded-xl p-5" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
              <p className="mb-2" style={{ fontSize: 14, fontWeight: 500, color: "var(--admin-text)" }}>Perfil IA</p>
              <p style={{ fontSize: 13, color: "var(--admin-muted)", lineHeight: 1.6 }}>{worker.profile.bio}</p>
            </div>
          )}
        </div>

        <div className="space-y-4">
          {/* Availability toggle */}
          <div className="rounded-xl p-4" style={{ background: worker.paused ? "var(--admin-amber-bg)" : "var(--admin-green-bg)", border: `1px solid ${worker.paused ? "var(--admin-amber-border)" : "var(--admin-green-border)"}` }}>
            <p className="mb-2" style={{ fontSize: 14, fontWeight: 500, color: worker.paused ? "var(--admin-amber)" : "var(--admin-green)" }}>
              {worker.paused ? "⏸️ Ofertas pausadas" : "✅ Recibiendo ofertas"}
            </p>
            <p className="mb-3" style={{ fontSize: 12, color: "var(--admin-muted)" }}>
              {worker.paused ? "Este trabajador no recibe ofertas" : "Este trabajador recibe ofertas normalmente"}
            </p>
            <button
              onClick={async () => { await updateWorkerManual(worker.id, worker.paused ? { paused: false, is_available: true } : { paused: true, is_available: false }); reload(); }}
              className="w-full rounded-lg py-2 text-xs font-medium"
              style={{ background: worker.paused ? "var(--admin-green-bg)" : "var(--admin-amber-bg)", border: `1px solid ${worker.paused ? "var(--admin-green-border)" : "var(--admin-amber-border)"}`, color: worker.paused ? "var(--admin-green)" : "var(--admin-amber)" }}
            >
              {worker.paused ? "Reactivar ofertas" : "Pausar ofertas"}
            </button>
          </div>

          <QuickActions actions={[
            { label: "✎ Completar manualmente", onClick: async () => { setDrawerOpen(true); }, variant: "amber" },
            { label: "Enviar SMS de prueba", onClick: async () => { await sendTestSMS(worker.phone, "Test desde admin CHAN-C"); }, variant: "default" },
            ...(!worker.is_vetted ? [{ label: "Aprobar trabajador", onClick: async () => { await approveWorker(worker.id); setWorker({ ...worker, is_active: true, is_vetted: true }); }, variant: "green" as const }] : []),
            { label: "Suspender trabajador", onClick: async () => {}, variant: "red" },
          ]} />
          <AdminNotes initialValue={worker.notes || ""} onSave={async () => {}} />
        </div>
      </div>

      <ManualRegistrationDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} existingWorker={worker} onSaved={reload} />
    </div>
  );
}
