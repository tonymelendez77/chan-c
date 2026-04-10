"use client";

import { useState, useEffect, useCallback } from "react";
import { X, ChevronDown, ChevronUp, Check, Plus, Trash2 } from "lucide-react";
import { TRADE_LABELS, SKILL_LABELS, type Trade, type SkillLevel } from "@/lib/types";
import { createWorkerManual, updateWorkerManual } from "@/lib/admin-api";

// ─── Types ───
interface Reference { name: string; phone: string; relationship: string; outcome: string; notes: string; }

export interface ManualFormData {
  full_name: string;
  phone: string;
  dpi: string;
  language: string;
  zone: string;
  preferred_zones: string[];
  excluded_zones: string[];
  availability_notes: string;
  trade: string;
  skill_level: string;
  years_experience: string;
  daily_rate: string;
  can_cover: string[];
  cannot_cover: string[];
  is_vetted: boolean;
  vetting_date: string;
  verification_method: string;
  verification_notes: string;
  manual_score: number;
  references: Reference[];
  admin_notes: string;
}

const EMPTY_FORM: ManualFormData = {
  full_name: "", phone: "", dpi: "", language: "spanish", zone: "",
  preferred_zones: [], excluded_zones: [], availability_notes: "",
  trade: "", skill_level: "mid", years_experience: "", daily_rate: "",
  can_cover: [], cannot_cover: [],
  is_vetted: false, vetting_date: new Date().toISOString().slice(0, 10),
  verification_method: "direct_call", verification_notes: "", manual_score: 0.7,
  references: [], admin_notes: "",
};

const EMPTY_REF: Reference = { name: "", phone: "", relationship: "ex_employer", outcome: "not_contacted", notes: "" };

const ZONES = Array.from({ length: 25 }, (_, i) => `Zona ${i + 1}`);
const TRADE_OPTIONS = Object.entries(TRADE_LABELS).map(([v, l]) => ({ value: v, label: l }));
const SKILL_OPTIONS = Object.entries(SKILL_LABELS).filter(([k]) => k !== "any").map(([v, l]) => ({ value: v, label: l }));
const LANG_OPTIONS = [{ value: "spanish", label: "Español" }, { value: "kiche", label: "K'iche" }, { value: "mam", label: "Mam" }, { value: "other", label: "Otro" }];
const REL_OPTIONS = [{ value: "ex_employer", label: "Ex-empleador" }, { value: "colleague", label: "Colega" }, { value: "client", label: "Cliente" }, { value: "other", label: "Otro" }];
const OUTCOME_OPTIONS = [{ value: "positive", label: "Positivo" }, { value: "neutral", label: "Neutral" }, { value: "negative", label: "Negativo" }, { value: "not_contacted", label: "No contactado" }];
const VERIFY_OPTIONS = [
  { value: "direct_call", label: "Llamada directa por Cece" },
  { value: "in_person", label: "Entrevista presencial" },
  { value: "documents", label: "Revisión de documentos" },
  { value: "referral", label: "Referido de confianza" },
  { value: "other", label: "Otro" },
];

// ─── Sub-components ───
function Section({ title, open, onToggle, complete, children }: { title: string; open: boolean; onToggle: () => void; complete: boolean; children: React.ReactNode }) {
  return (
    <div className="rounded-xl overflow-hidden" style={{ border: "1px solid var(--admin-border)" }}>
      <button onClick={onToggle} className="flex items-center gap-3 w-full px-4 py-3 text-left" style={{ background: "var(--admin-surface)" }}>
        <div className="w-5 h-5 rounded-full flex items-center justify-center" style={{ background: complete ? "var(--admin-green-bg)" : "#F5F5F4", border: `1px solid ${complete ? "var(--admin-green-border)" : "var(--admin-border)"}` }}>
          {complete && <Check className="w-3 h-3" style={{ color: "var(--admin-green)" }} />}
        </div>
        <span className="flex-1 text-sm font-medium" style={{ color: "var(--admin-text)" }}>{title}</span>
        {open ? <ChevronUp className="w-4 h-4" style={{ color: "var(--admin-dim)" }} /> : <ChevronDown className="w-4 h-4" style={{ color: "var(--admin-dim)" }} />}
      </button>
      {open && <div className="px-4 pb-4 pt-2 space-y-3" style={{ background: "var(--admin-surface)" }}>{children}</div>}
    </div>
  );
}

function Field({ label, required, children }: { label: string; required?: boolean; children: React.ReactNode }) {
  return (
    <div>
      <label className="block mb-1" style={{ fontSize: 12, fontWeight: 500, color: "var(--admin-muted)" }}>{label}{required && <span style={{ color: "var(--admin-red)" }}> *</span>}</label>
      {children}
    </div>
  );
}

function TextInput({ value, onChange, placeholder, mono, type = "text" }: { value: string; onChange: (v: string) => void; placeholder?: string; mono?: boolean; type?: string }) {
  return <input type={type} value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} className="w-full rounded-lg px-3 py-2 text-sm outline-none" style={{ border: "1px solid var(--admin-border)", color: "var(--admin-text)", fontFamily: mono ? "'JetBrains Mono', monospace" : "inherit" }} />;
}

function SelectInput({ value, onChange, options, placeholder }: { value: string; onChange: (v: string) => void; options: { value: string; label: string }[]; placeholder?: string }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} className="w-full rounded-lg px-3 py-2 text-sm outline-none" style={{ border: "1px solid var(--admin-border)", color: "var(--admin-text)", background: "var(--admin-surface)" }}>
      {placeholder && <option value="">{placeholder}</option>}
      {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select>
  );
}

function ChipSelector({ selected, onChange, options, variant = "green" }: { selected: string[]; onChange: (v: string[]) => void; options: string[]; variant?: "green" | "red" }) {
  const toggle = (z: string) => onChange(selected.includes(z) ? selected.filter((s) => s !== z) : [...selected, z]);
  const colors = variant === "green"
    ? { bg: "var(--admin-green-bg)", border: "var(--admin-green-border)", text: "var(--admin-green)" }
    : { bg: "var(--admin-red-bg)", border: "var(--admin-red-border)", text: "var(--admin-red)" };
  return (
    <div className="flex flex-wrap gap-1.5">
      {options.map((z) => {
        const active = selected.includes(z);
        return (
          <button key={z} onClick={() => toggle(z)} className="rounded-full px-2.5 py-1 text-xs" style={{ background: active ? colors.bg : "#F5F5F4", border: `1px solid ${active ? colors.border : "var(--admin-border)"}`, color: active ? colors.text : "var(--admin-dim)", fontWeight: active ? 500 : 400 }}>
            {z}{active && " ✕"}
          </button>
        );
      })}
    </div>
  );
}

function TagInput({ tags, onChange, placeholder, variant = "green" }: { tags: string[]; onChange: (v: string[]) => void; placeholder?: string; variant?: "green" | "red" }) {
  const [input, setInput] = useState("");
  const add = () => { if (input.trim() && !tags.includes(input.trim())) { onChange([...tags, input.trim()]); setInput(""); } };
  const colors = variant === "green"
    ? { bg: "var(--admin-green-bg)", border: "var(--admin-green-border)", text: "var(--admin-green)" }
    : { bg: "var(--admin-red-bg)", border: "var(--admin-red-border)", text: "var(--admin-red)" };
  return (
    <div>
      <div className="flex gap-2 mb-2">
        <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), add())} placeholder={placeholder} className="flex-1 rounded-lg px-3 py-2 text-sm outline-none" style={{ border: "1px solid var(--admin-border)", color: "var(--admin-text)" }} />
        <button onClick={add} className="rounded-lg px-3 py-2 text-xs font-medium" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)", color: "var(--admin-muted)" }}>Agregar</button>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {tags.map((t) => (
          <span key={t} className="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs" style={{ background: colors.bg, border: `1px solid ${colors.border}`, color: colors.text }}>
            {t}
            <button onClick={() => onChange(tags.filter((x) => x !== t))}><X className="w-3 h-3" /></button>
          </span>
        ))}
      </div>
    </div>
  );
}

// ─── Main Drawer ───
interface DrawerProps {
  open: boolean;
  onClose: () => void;
  existingWorker?: { id: string; full_name: string; phone: string; dpi?: string; zone: string; language: string; notes?: string; trades?: { trade: string; skill_level: string; years_experience: number; can_cover?: string[]; cannot_cover?: string[] }[] } | null;
  onSaved?: () => void;
}

export default function ManualRegistrationDrawer({ open, onClose, existingWorker, onSaved }: DrawerProps) {
  const [form, setForm] = useState<ManualFormData>(EMPTY_FORM);
  const [openSections, setOpenSections] = useState<Record<number, boolean>>({ 0: true, 1: false, 2: false, 3: false, 4: false, 5: false });
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);

  const isEdit = !!existingWorker;

  // Pre-fill from existing worker
  useEffect(() => {
    if (existingWorker) {
      const t = existingWorker.trades?.[0];
      setForm({
        ...EMPTY_FORM,
        full_name: existingWorker.full_name === "Pendiente" ? "" : existingWorker.full_name,
        phone: existingWorker.phone,
        dpi: existingWorker.dpi || "",
        zone: existingWorker.zone,
        language: existingWorker.language || "spanish",
        trade: t?.trade || "",
        skill_level: t?.skill_level || "mid",
        years_experience: t?.years_experience ? String(t.years_experience) : "",
        can_cover: t?.can_cover || [],
        cannot_cover: t?.cannot_cover || [],
        admin_notes: existingWorker.notes || "",
      });
    } else {
      setForm(EMPTY_FORM);
    }
    setDirty(false);
  }, [existingWorker, open]);

  const update = useCallback(<K extends keyof ManualFormData>(key: K, value: ManualFormData[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    setDirty(true);
  }, []);

  const toggleSection = (i: number) => setOpenSections((prev) => ({ ...prev, [i]: !prev[i] }));

  const handleClose = () => {
    if (dirty && !confirm("Tienes cambios sin guardar. ¿Cerrar de todos modos?")) return;
    onClose();
  };

  const save = async (activate: boolean) => {
    if (!form.full_name || !form.phone || !form.zone) { alert("Completa los campos requeridos: nombre, teléfono y zona."); return; }
    if (activate && (!form.trade || !form.skill_level)) { alert("Para activar, indica oficio y nivel de experiencia."); return; }
    setSaving(true);
    try {
      const body = {
        full_name: form.full_name, phone: form.phone, dpi: form.dpi || undefined,
        zone: form.zone, language: form.language, notes: form.admin_notes || undefined,
        is_available: true,
        ...(activate ? { is_vetted: true } : {}),
        trades: form.trade ? [{ trade: form.trade, skill_level: form.skill_level, years_experience: Number(form.years_experience) || 0, can_cover: form.can_cover.length ? form.can_cover : undefined, cannot_cover: form.cannot_cover.length ? form.cannot_cover : undefined }] : undefined,
        references: form.references.filter((r) => r.name && r.phone).map((r) => ({ reference_name: r.name, reference_phone: r.phone, relationship: r.relationship })) || undefined,
        profile: { bio: [form.verification_notes, form.preferred_zones.length ? `Zonas preferidas: ${form.preferred_zones.join(", ")}` : "", form.excluded_zones.length ? `Zonas excluidas: ${form.excluded_zones.join(", ")}` : ""].filter(Boolean).join(". ") || undefined, initial_score: form.manual_score },
      };
      if (isEdit && existingWorker) {
        await updateWorkerManual(existingWorker.id, body);
      } else {
        await createWorkerManual(body);
      }
      setDirty(false);
      onSaved?.();
      onClose();
    } catch (e) {
      alert("Error al guardar: " + (e instanceof Error ? e.message : "desconocido"));
    } finally {
      setSaving(false);
    }
  };

  if (!open) return null;

  const s1Complete = !!(form.full_name && form.phone && form.zone);
  const s3Complete = !!(form.trade && form.skill_level);

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 z-[200]" style={{ background: "rgba(0,0,0,0.3)" }} onClick={handleClose} />

      {/* Drawer */}
      <div className="fixed top-0 right-0 bottom-0 z-[201] flex flex-col" style={{ width: 560, background: "var(--admin-bg)", borderLeft: "1px solid var(--admin-border)", animation: "slideInRight 0.3s ease" }}>
        {/* Header */}
        <div className="px-6 py-4 flex items-start justify-between shrink-0" style={{ borderBottom: "1px solid var(--admin-border)", background: "var(--admin-surface)" }}>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h2 style={{ fontSize: 18, fontWeight: 600, color: "var(--admin-text)" }}>
                {isEdit ? `Completar perfil — ${existingWorker?.full_name}` : "Registro manual"}
              </h2>
              <span className="rounded-full px-2 py-0.5 text-xs font-medium" style={{ background: isEdit ? "var(--admin-amber-bg)" : "var(--admin-green-bg)", border: `1px solid ${isEdit ? "var(--admin-amber-border)" : "var(--admin-green-border)"}`, color: isEdit ? "var(--admin-amber)" : "var(--admin-green)" }}>
                {isEdit ? "Completando existente" : "Nuevo trabajador"}
              </span>
            </div>
            <p style={{ fontSize: 13, color: "var(--admin-muted)" }}>Información recopilada por llamada directa</p>
          </div>
          <button onClick={handleClose} className="p-1 rounded" style={{ color: "var(--admin-dim)" }}><X className="w-5 h-5" /></button>
        </div>

        {/* Scrollable form */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
          {/* Section 1 — Personal */}
          <Section title="Información personal" open={openSections[0]} onToggle={() => toggleSection(0)} complete={s1Complete}>
            <Field label="Nombre completo" required><TextInput value={form.full_name} onChange={(v) => update("full_name", v)} placeholder="Pedro Ramírez López" /></Field>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Teléfono" required><TextInput value={form.phone} onChange={(v) => update("phone", v)} placeholder="55551234" mono /></Field>
              <Field label="DPI"><TextInput value={form.dpi} onChange={(v) => update("dpi", v)} placeholder="1234567890101" mono /></Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Idioma"><SelectInput value={form.language} onChange={(v) => update("language", v)} options={LANG_OPTIONS} /></Field>
              <Field label="Zona donde vive" required><SelectInput value={form.zone} onChange={(v) => update("zone", v)} options={ZONES.map((z) => ({ value: z.replace("Zona ", ""), label: z }))} placeholder="Seleccionar..." /></Field>
            </div>
          </Section>

          {/* Section 2 — Zones */}
          <Section title="Zonas de trabajo" open={openSections[1]} onToggle={() => toggleSection(1)} complete={form.preferred_zones.length > 0}>
            <Field label="Zonas preferidas">
              <div className="flex items-center gap-2 mb-2">
                <button onClick={() => update("preferred_zones", form.preferred_zones.length === 25 ? [] : ZONES)} className="text-xs rounded px-2 py-1" style={{ border: "1px solid var(--admin-border)", color: "var(--admin-muted)" }}>
                  {form.preferred_zones.length === 25 ? "Quitar todas" : "Todas las zonas"}
                </button>
              </div>
              <ChipSelector selected={form.preferred_zones} onChange={(v) => update("preferred_zones", v)} options={ZONES} variant="green" />
            </Field>
            <Field label="Zonas excluidas">
              <ChipSelector selected={form.excluded_zones} onChange={(v) => update("excluded_zones", v)} options={ZONES} variant="red" />
            </Field>
            <Field label="Notas de disponibilidad"><textarea value={form.availability_notes} onChange={(e) => update("availability_notes", e.target.value)} rows={2} placeholder="Ej: Solo disponible lunes a viernes, 7am-5pm" className="w-full rounded-lg px-3 py-2 text-sm outline-none resize-none" style={{ border: "1px solid var(--admin-border)", color: "var(--admin-text)" }} /></Field>
          </Section>

          {/* Section 3 — Trade */}
          <Section title="Oficio y experiencia" open={openSections[2]} onToggle={() => toggleSection(2)} complete={s3Complete}>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Oficio principal" required><SelectInput value={form.trade} onChange={(v) => update("trade", v)} options={TRADE_OPTIONS} placeholder="Seleccionar..." /></Field>
              <Field label="Nivel" required><SelectInput value={form.skill_level} onChange={(v) => update("skill_level", v)} options={SKILL_OPTIONS} /></Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Años de experiencia" required><TextInput value={form.years_experience} onChange={(v) => update("years_experience", v)} type="number" placeholder="5" mono /></Field>
              <Field label="Tarifa diaria (Q)" required><TextInput value={form.daily_rate} onChange={(v) => update("daily_rate", v)} type="number" placeholder="350" mono /></Field>
            </div>
            <Field label="Puede cubrir"><TagInput tags={form.can_cover} onChange={(v) => update("can_cover", v)} placeholder="Ej: Instalación residencial" variant="green" /></Field>
            <Field label="No puede cubrir"><TagInput tags={form.cannot_cover} onChange={(v) => update("cannot_cover", v)} placeholder="Ej: Instalaciones trifásicas" variant="red" /></Field>
          </Section>

          {/* Section 4 — Verification */}
          <Section title="Verificación" open={openSections[3]} onToggle={() => toggleSection(3)} complete={form.is_vetted}>
            <div className="flex items-center justify-between p-3 rounded-lg" style={{ background: form.is_vetted ? "var(--admin-green-bg)" : "#F5F5F4", border: `1px solid ${form.is_vetted ? "var(--admin-green-border)" : "var(--admin-border)"}` }}>
              <span style={{ fontSize: 14, fontWeight: 500, color: form.is_vetted ? "var(--admin-green)" : "var(--admin-muted)" }}>
                {form.is_vetted ? "✓ Verificado" : "Sin verificar"}
              </span>
              <button onClick={() => update("is_vetted", !form.is_vetted)} className="w-11 h-6 rounded-full relative" style={{ background: form.is_vetted ? "var(--admin-green)" : "var(--admin-border-strong)" }}>
                <span className="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform" style={{ left: form.is_vetted ? 22 : 2 }} />
              </button>
            </div>
            {form.is_vetted && (
              <>
                <Field label="Fecha de verificación"><TextInput value={form.vetting_date} onChange={(v) => update("vetting_date", v)} type="date" mono /></Field>
                <Field label="Método de verificación">
                  <div className="space-y-1.5">
                    {VERIFY_OPTIONS.map((o) => (
                      <label key={o.value} className="flex items-center gap-2 cursor-pointer">
                        <input type="radio" name="verify" checked={form.verification_method === o.value} onChange={() => update("verification_method", o.value)} className="accent-amber-600" />
                        <span style={{ fontSize: 13, color: "var(--admin-text)" }}>{o.label}</span>
                      </label>
                    ))}
                  </div>
                </Field>
                <Field label="Notas de verificación"><textarea value={form.verification_notes} onChange={(e) => update("verification_notes", e.target.value)} rows={2} placeholder="Ej: Llamé el 5 de mayo. Confirmó experiencia..." className="w-full rounded-lg px-3 py-2 text-sm outline-none resize-none" style={{ border: "1px solid var(--admin-border)", color: "var(--admin-text)" }} /></Field>
                <Field label={`Score manual: ${form.manual_score.toFixed(2)}`}>
                  <input type="range" min={0} max={1} step={0.05} value={form.manual_score} onChange={(e) => update("manual_score", parseFloat(e.target.value))} className="w-full accent-amber-600" />
                  <div className="flex justify-between" style={{ fontSize: 11, color: "var(--admin-dim)" }}><span>0.0</span><span className="font-mono" style={{ color: form.manual_score >= 0.8 ? "var(--admin-green)" : form.manual_score >= 0.6 ? "var(--admin-amber)" : "var(--admin-red)", fontWeight: 600 }}>{form.manual_score.toFixed(2)}</span><span>1.0</span></div>
                </Field>
              </>
            )}
          </Section>

          {/* Section 5 — References */}
          <Section title={`Referencias (${form.references.length}/3)`} open={openSections[4]} onToggle={() => toggleSection(4)} complete={form.references.length > 0}>
            {form.references.map((ref, i) => (
              <div key={i} className="rounded-lg p-3 relative" style={{ background: "#FAFAF9", border: "1px solid var(--admin-border)" }}>
                <button onClick={() => update("references", form.references.filter((_, j) => j !== i))} className="absolute top-2 right-2" style={{ color: "var(--admin-dim)" }}><Trash2 className="w-3.5 h-3.5" /></button>
                <div className="grid grid-cols-2 gap-2 mb-2">
                  <Field label="Nombre"><TextInput value={ref.name} onChange={(v) => { const r = [...form.references]; r[i] = { ...r[i], name: v }; update("references", r); }} placeholder="Juan Pérez" /></Field>
                  <Field label="Teléfono"><TextInput value={ref.phone} onChange={(v) => { const r = [...form.references]; r[i] = { ...r[i], phone: v }; update("references", r); }} placeholder="55551234" mono /></Field>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <Field label="Relación"><SelectInput value={ref.relationship} onChange={(v) => { const r = [...form.references]; r[i] = { ...r[i], relationship: v }; update("references", r); }} options={REL_OPTIONS} /></Field>
                  <Field label="Resultado"><SelectInput value={ref.outcome} onChange={(v) => { const r = [...form.references]; r[i] = { ...r[i], outcome: v }; update("references", r); }} options={OUTCOME_OPTIONS} /></Field>
                </div>
              </div>
            ))}
            {form.references.length < 3 && (
              <button onClick={() => update("references", [...form.references, { ...EMPTY_REF }])} className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm w-full justify-center" style={{ border: "1px dashed var(--admin-border)", color: "var(--admin-muted)" }}>
                <Plus className="w-4 h-4" /> Agregar referencia
              </button>
            )}
          </Section>

          {/* Section 6 — Notes */}
          <Section title="Notas internas" open={openSections[5]} onToggle={() => toggleSection(5)} complete={!!form.admin_notes}>
            <Field label="Notas privadas"><textarea value={form.admin_notes} onChange={(e) => update("admin_notes", e.target.value)} rows={4} placeholder="Solo visibles para el equipo de CHAN-C" className="w-full rounded-lg px-3 py-2 text-sm outline-none resize-none" style={{ border: "1px solid var(--admin-border)", color: "var(--admin-text)" }} /></Field>
            <p style={{ fontSize: 11, color: "var(--admin-dim)" }}>Registrado por: Admin · {new Date().toLocaleDateString("es-GT")}</p>
          </Section>
        </div>

        {/* Bottom bar */}
        <div className="shrink-0 px-6 py-4 flex items-center justify-between" style={{ borderTop: "1px solid var(--admin-border)", background: "var(--admin-surface)" }}>
          <p style={{ fontSize: 11, color: "var(--admin-dim)" }}>* Campos requeridos</p>
          <div className="flex gap-2">
            <button onClick={handleClose} className="rounded-lg px-4 py-2 text-sm" style={{ border: "1px solid var(--admin-border)", color: "var(--admin-muted)" }}>Cancelar</button>
            <button onClick={() => save(false)} disabled={saving} className="rounded-lg px-4 py-2 text-sm font-medium" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)", color: "var(--admin-text)" }}>
              {saving ? "Guardando..." : "Guardar borrador"}
            </button>
            <button onClick={() => save(true)} disabled={saving} className="rounded-lg px-4 py-2 text-sm font-bold" style={{ background: "var(--admin-amber)", color: "#fff" }}>
              {saving ? "Guardando..." : "Guardar y activar"}
            </button>
          </div>
        </div>
      </div>

      <style>{`@keyframes slideInRight { from { transform: translateX(100%); } to { transform: translateX(0); } }`}</style>
    </>
  );
}
