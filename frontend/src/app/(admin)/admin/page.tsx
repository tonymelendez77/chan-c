"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import PageHeader from "@/components/admin/PageHeader";
import { Users, Clock, Briefcase, PhoneCall, TrendingUp, Building2 } from "lucide-react";
import { fetchDashboardStats, fetchPendingMatches } from "@/lib/admin-api";
import type { DashboardStats, Match } from "@/lib/types";

function StatCard({ label, value, icon: Icon, color, sub }: { label: string; value: number; icon: React.ElementType; color: string; sub: string }) {
  return (
    <div className="rounded-xl p-5" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
      <div className="flex items-start justify-between mb-3">
        <div className="rounded-lg p-2" style={{ background: color === "var(--admin-amber)" ? "var(--admin-amber-bg)" : color === "var(--admin-green)" ? "var(--admin-green-bg)" : color === "var(--admin-blue)" ? "var(--admin-blue-bg)" : color === "var(--admin-purple)" ? "var(--admin-purple-bg)" : "var(--admin-red-bg)", border: `1px solid ${color === "var(--admin-amber)" ? "var(--admin-amber-border)" : color === "var(--admin-green)" ? "var(--admin-green-border)" : color === "var(--admin-blue)" ? "var(--admin-blue-border)" : color === "var(--admin-purple)" ? "var(--admin-purple-border)" : "var(--admin-red-border)"}` }}>
          <Icon style={{ width: 18, height: 18, color }} />
        </div>
      </div>
      <p className="font-mono" style={{ fontSize: 36, fontWeight: 700, color, lineHeight: 1 }}>{value}</p>
      <p className="mt-1" style={{ fontSize: 13, fontWeight: 500, color: "var(--admin-text)" }}>{label}</p>
      <p style={{ fontSize: 12, color: "var(--admin-muted)" }}>{sub}</p>
    </div>
  );
}

function ActionCard({ title, subtitle, href, accentColor }: { title: string; subtitle: string; href: string; accentColor: string }) {
  return (
    <div className="flex items-center rounded-xl overflow-hidden" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
      <div style={{ width: 4, alignSelf: "stretch", background: accentColor }} />
      <div className="flex-1 flex items-center justify-between px-4 py-3.5">
        <div>
          <p style={{ fontSize: 14, fontWeight: 500, color: "var(--admin-text)" }}>{title}</p>
          <p style={{ fontSize: 13, color: "var(--admin-muted)" }}>{subtitle}</p>
        </div>
        <Link href={href} className="rounded-lg px-3 py-1.5 text-xs font-medium" style={{ border: "1px solid var(--admin-border)", color: "var(--admin-muted)" }}>
          Ver →
        </Link>
      </div>
    </div>
  );
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [pending, setPending] = useState<Match[]>([]);

  useEffect(() => {
    fetchDashboardStats().then(setStats).catch(() => {});
    fetchPendingMatches().then(setPending).catch(() => {});
  }, []);

  const s = stats || { active_workers: 0, vetted_workers: 0, open_jobs: 0, active_matches: 0, pending_matches: 0, completed_jobs_this_month: 0, total_companies: 0 };

  return (
    <div>
      <PageHeader title="Panel de operaciones" subtitle="Buen día. Aquí está el resumen de hoy." />

      <div className="grid grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
        <StatCard label="Trabajadores activos" value={s.active_workers} icon={Users} color="var(--admin-green)" sub={`${s.vetted_workers} verificados`} />
        <StatCard label="Matches pendientes" value={s.pending_matches} icon={Clock} color="var(--admin-amber)" sub="Requieren atención" />
        <StatCard label="Trabajos abiertos" value={s.open_jobs} icon={Briefcase} color="var(--admin-blue)" sub="Esperando match" />
        <StatCard label="Llamadas IA activas" value={0} icon={PhoneCall} color="var(--admin-purple)" sub="En este momento" />
        <StatCard label="Ingresos este mes" value={0} icon={TrendingUp} color="var(--admin-green)" sub="Comisiones cobradas" />
        <StatCard label="Empresas" value={s.total_companies} icon={Building2} color="var(--admin-blue)" sub="Registradas" />
      </div>

      {/* Pending Actions */}
      {pending.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: "var(--admin-amber)" }} />
            <h2 style={{ fontSize: 16, fontWeight: 600, color: "var(--admin-text)" }}>Acciones requeridas</h2>
          </div>
          <div className="space-y-2">
            {pending.slice(0, 5).map((m) => (
              <ActionCard
                key={m.id}
                title={`Match pendiente: ${m.worker_name || "Trabajador"} → ${m.job_title || "Trabajo"}`}
                subtitle={`Tarifa: Q${m.offered_rate}/día · Estado: ${m.status}`}
                href={`/admin/matches/${m.id}`}
                accentColor="var(--admin-amber)"
              />
            ))}
          </div>
        </div>
      )}

      {/* Activity placeholder */}
      <div>
        <h2 className="mb-4" style={{ fontSize: 16, fontWeight: 600, color: "var(--admin-text)" }}>Actividad reciente</h2>
        <div className="rounded-xl p-6 text-center" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
          <p style={{ fontSize: 14, color: "var(--admin-muted)" }}>La actividad se actualizará conforme la plataforma procese matches y llamadas.</p>
        </div>
      </div>
    </div>
  );
}
