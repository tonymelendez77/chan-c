"use client";

import { useState } from "react";

interface AdminNotesProps {
  initialValue?: string;
  onSave: (notes: string) => Promise<void>;
}

export default function AdminNotes({ initialValue = "", onSave }: AdminNotesProps) {
  const [value, setValue] = useState(initialValue);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(value);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } finally { setSaving(false); }
  };

  return (
    <div className="rounded-xl" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)", padding: 16 }}>
      <p className="mb-2" style={{ fontSize: 12, fontWeight: 500, color: "var(--admin-muted)" }}>Notas de admin</p>
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onBlur={handleSave}
        rows={3}
        className="w-full rounded-lg px-3 py-2 text-sm resize-none outline-none"
        style={{ border: "1px solid var(--admin-border)", color: "var(--admin-text)", fontSize: 13 }}
        placeholder="Notas privadas sobre este registro..."
      />
      <div className="flex items-center justify-between mt-2">
        <span style={{ fontSize: 11, color: saved ? "var(--admin-green)" : "var(--admin-dim)" }}>
          {saving ? "Guardando..." : saved ? "Guardado" : ""}
        </span>
        <button onClick={handleSave} disabled={saving} className="rounded px-3 py-1 text-xs font-medium" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)", color: "var(--admin-muted)" }}>
          Guardar nota
        </button>
      </div>
    </div>
  );
}
