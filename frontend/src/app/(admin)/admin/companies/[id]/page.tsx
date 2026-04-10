"use client";

import { useEffect, useState } from "react";
import { use } from "react";
import PageHeader from "@/components/admin/PageHeader";
import StatusBadge from "@/components/admin/StatusBadge";
import AdminNotes from "@/components/admin/AdminNotes";
import { fetchCompany } from "@/lib/admin-api";
import type { Company } from "@/lib/types";

const TYPE_LABELS: Record<string, string> = { construction: "Construcción", architecture: "Arquitectura", property_management: "Propiedades", other: "Otro" };

export default function AdminCompanyDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [company, setCompany] = useState<(Company & { job_count?: number }) | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchCompany(id).then(setCompany).catch(() => {}).finally(() => setLoading(false)); }, [id]);

  if (loading) return <div style={{ color: "var(--admin-muted)", padding: 40 }}>Cargando...</div>;
  if (!company) return <div style={{ color: "var(--admin-muted)", padding: 40 }}>Empresa no encontrada</div>;

  return (
    <div>
      <PageHeader title={company.name} subtitle={company.email} backHref="/admin/companies">
        {company.is_verified ? <StatusBadge status="" label="Verificada" color="green" /> : <StatusBadge status="" label="Pendiente" color="amber" />}
      </PageHeader>

      <div className="grid grid-cols-1 xl:grid-cols-[2fr_1fr] gap-6">
        <div className="rounded-xl p-5" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
          <div className="grid grid-cols-2 gap-4">
            {[
              ["Contacto", company.contact_name],
              ["Teléfono", company.phone],
              ["Email", company.email],
              ["Tipo", TYPE_LABELS[company.company_type]],
              ["NIT", company.tax_id],
              ["Zona", `Zona ${company.zone}`],
              ["Plan", company.subscription_plan],
              ["Trabajos publicados", String(company.job_count ?? 0)],
              ["Registrada", new Date(company.created_at).toLocaleDateString("es-GT")],
            ].map(([k, v]) => (
              <div key={k as string}>
                <p style={{ fontSize: 12, color: "var(--admin-dim)" }}>{k}</p>
                <p className="font-mono" style={{ fontSize: 13, fontWeight: 500, color: "var(--admin-text)" }}>{v}</p>
              </div>
            ))}
          </div>
        </div>
        <AdminNotes onSave={async () => {}} />
      </div>
    </div>
  );
}
