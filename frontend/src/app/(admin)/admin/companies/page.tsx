"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import PageHeader from "@/components/admin/PageHeader";
import AdminTable, { type Column } from "@/components/admin/AdminTable";
import StatusBadge from "@/components/admin/StatusBadge";
import { fetchCompanies } from "@/lib/admin-api";
import type { Company } from "@/lib/types";

const TYPE_LABELS: Record<string, string> = { construction: "Construcción", architecture: "Arquitectura", property_management: "Propiedades", other: "Otro" };

export default function AdminCompaniesPage() {
  const router = useRouter();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchCompanies().then(setCompanies).catch(() => {}).finally(() => setLoading(false)); }, []);

  const columns: Column<Company>[] = [
    { key: "name", label: "Nombre", render: (r) => <span style={{ fontWeight: 500 }}>{r.name}</span> },
    { key: "contact_name", label: "Contacto" },
    { key: "email", label: "Email", mono: true, render: (r) => <span className="font-mono text-xs">{r.email}</span> },
    { key: "company_type", label: "Tipo", render: (r) => TYPE_LABELS[r.company_type] || r.company_type },
    { key: "subscription_plan", label: "Plan", render: (r) => <StatusBadge status="" label={r.subscription_plan} color={r.subscription_plan === "pro" ? "purple" : r.subscription_plan === "basic" ? "blue" : "gray"} /> },
    { key: "is_verified", label: "Estado", render: (r) => r.is_verified ? <StatusBadge status="" label="Verificada" color="green" /> : <StatusBadge status="" label="Pendiente" color="amber" /> },
    { key: "created_at", label: "Fecha", mono: true, render: (r) => new Date(r.created_at).toLocaleDateString("es-GT") },
  ];

  return (
    <div>
      <PageHeader title="Empresas" subtitle={`${companies.length} registradas`} />
      <AdminTable columns={columns} data={companies} loading={loading} onRowClick={(r) => router.push(`/admin/companies/${r.id}`)} emptyMessage="No hay empresas registradas" />
    </div>
  );
}
