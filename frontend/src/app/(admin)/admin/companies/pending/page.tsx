"use client";

import { useEffect, useState } from "react";
import PageHeader from "@/components/admin/PageHeader";
import AdminTable, { type Column } from "@/components/admin/AdminTable";
import { fetchCompanies } from "@/lib/admin-api";
import type { Company } from "@/lib/types";

export default function PendingCompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchCompanies().then((all: Company[]) => setCompanies(all.filter((c) => !c.is_verified))).catch(() => {}).finally(() => setLoading(false)); }, []);

  const columns: Column<Company>[] = [
    { key: "name", label: "Nombre", render: (r) => <span style={{ fontWeight: 500 }}>{r.name}</span> },
    { key: "contact_name", label: "Contacto" },
    { key: "email", label: "Email", mono: true },
    { key: "company_type", label: "Tipo" },
    { key: "created_at", label: "Fecha", mono: true, render: (r) => new Date(r.created_at).toLocaleDateString("es-GT") },
    { key: "actions", label: "Acciones", render: () => (
      <div className="flex gap-1">
        <button className="rounded px-2 py-1 text-xs font-medium" style={{ background: "var(--admin-green-bg)", border: "1px solid var(--admin-green-border)", color: "var(--admin-green)" }}>Aprobar</button>
        <button className="rounded px-2 py-1 text-xs font-medium" style={{ background: "var(--admin-red-bg)", border: "1px solid var(--admin-red-border)", color: "var(--admin-red)" }}>Rechazar</button>
      </div>
    )},
  ];

  return (
    <div>
      <PageHeader title="Empresas pendientes de aprobación" subtitle={`${companies.length} pendientes`} />
      <AdminTable columns={columns} data={companies} loading={loading} emptyMessage="No hay empresas pendientes" />
    </div>
  );
}
