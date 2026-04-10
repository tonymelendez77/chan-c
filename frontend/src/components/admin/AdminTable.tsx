"use client";

import { Inbox } from "lucide-react";

export interface Column<T> {
  key: string;
  label: string;
  render?: (row: T) => React.ReactNode;
  mono?: boolean;
}

interface AdminTableProps<T> {
  columns: Column<T>[];
  data: T[];
  onRowClick?: (row: T) => void;
  loading?: boolean;
  emptyMessage?: string;
  keyField?: string;
}

function Skeleton() {
  return (
    <div className="space-y-2 p-4">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="h-10 rounded" style={{ background: "#F5F5F4" }} />
      ))}
    </div>
  );
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export default function AdminTable<T extends Record<string, any>>({
  columns, data, onRowClick, loading, emptyMessage = "No hay datos", keyField = "id",
}: AdminTableProps<T>) {
  if (loading) return <Skeleton />;

  if (data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 rounded-xl" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
        <Inbox className="h-8 w-8 mb-3" style={{ color: "var(--admin-dim)" }} />
        <p style={{ fontSize: 14, color: "var(--admin-muted)" }}>{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
      <table className="w-full">
        <thead>
          <tr style={{ borderBottom: "1px solid var(--admin-border)" }}>
            {columns.map((col) => (
              <th key={col.key} className="text-left px-4 py-3" style={{ fontSize: 12, fontWeight: 500, color: "var(--admin-muted)", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr
              key={String(row[keyField] ?? i)}
              onClick={() => onRowClick?.(row)}
              className={onRowClick ? "cursor-pointer" : ""}
              style={{ borderBottom: i < data.length - 1 ? "1px solid var(--admin-border)" : "none", transition: "background 0.1s" }}
              onMouseEnter={(e) => { if (onRowClick) (e.currentTarget as HTMLElement).style.background = "var(--admin-amber-bg)"; }}
              onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = ""; }}
            >
              {columns.map((col) => (
                <td key={col.key} className="px-4 py-3" style={{ fontSize: 13, color: "var(--admin-text)", fontFamily: col.mono ? "'JetBrains Mono', monospace" : "inherit" }}>
                  {col.render ? col.render(row) : String(row[col.key] ?? "—")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
