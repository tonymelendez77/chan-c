"use client";

import { useEffect, useState } from "react";
import PageHeader from "@/components/admin/PageHeader";
import AdminTable, { type Column } from "@/components/admin/AdminTable";
import StatusBadge from "@/components/admin/StatusBadge";
import api from "@/lib/api";

interface SMSLog { id: string; direction: string; message: string; twilio_sid?: string; status: string; sent_at: string; worker_id?: string; [key: string]: unknown; }

export default function SMSLogsPage() {
  const [logs, setLogs] = useState<SMSLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // SMS logs aren't in admin-api yet; use empty state for now
    setLoading(false);
  }, []);

  const columns: Column<SMSLog>[] = [
    { key: "direction", label: "Dir", render: (r) => r.direction === "inbound" ? <span style={{ color: "var(--admin-amber)" }}>← In</span> : <span style={{ color: "var(--admin-dim)" }}>→ Out</span> },
    { key: "message", label: "Mensaje", render: (r) => <span className="truncate block max-w-xs" style={{ fontSize: 13 }}>{String(r.message).slice(0, 60)}{String(r.message).length > 60 ? "..." : ""}</span> },
    { key: "status", label: "Estado", render: (r) => {
      const color = r.status === "delivered" ? "green" : r.status === "failed" ? "red" : r.status === "received" ? "amber" : "gray";
      return <StatusBadge status="" label={r.status} color={color} />;
    }},
    { key: "sent_at", label: "Fecha", mono: true, render: (r) => new Date(r.sent_at).toLocaleString("es-GT") },
  ];

  return (
    <div>
      <PageHeader title="Registro SMS / WhatsApp" />
      <AdminTable columns={columns} data={logs} loading={loading} emptyMessage="No hay registros de SMS. Los logs se poblarán cuando se envíen o reciban mensajes." />
    </div>
  );
}
