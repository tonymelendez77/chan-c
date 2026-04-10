"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import PageHeader from "@/components/admin/PageHeader";
import ManualRegistrationDrawer, { type ManualFormData } from "@/components/admin/ManualRegistrationDrawer";
import { TRADE_LABELS, SKILL_LABELS } from "@/lib/types";

export default function ManualRegistrationPage() {
  const router = useRouter();
  const [drawerOpen, setDrawerOpen] = useState(true);

  return (
    <div>
      <PageHeader title="Registro manual de trabajador" subtitle="Ingresa la información recopilada durante una llamada directa" backHref="/admin/workers" />

      <div className="grid grid-cols-1 xl:grid-cols-[1fr_360px] gap-6">
        {/* Left — instructions */}
        <div className="space-y-4">
          <div className="rounded-xl p-6" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
            <h3 style={{ fontSize: 16, fontWeight: 600, color: "var(--admin-text)", marginBottom: 12 }}>Cómo usar el registro manual</h3>
            <div className="space-y-4">
              {[
                { num: "1", title: "Llama al trabajador", desc: "Usa el número de CHAN-C o tu teléfono personal. Recuerda ser amable y claro." },
                { num: "2", title: "Recopila información", desc: "Nombre completo, DPI, zona, oficio, experiencia, tarifa esperada, y hasta 3 referencias." },
                { num: "3", title: "Llena el formulario", desc: "Abre el panel de registro y completa cada sección. Los campos marcados con * son obligatorios." },
                { num: "4", title: "Verifica y activa", desc: "Si estás segura del trabajador, marca 'Verificado' y haz click en 'Guardar y activar'. Si no, guarda como borrador." },
              ].map((step) => (
                <div key={step.num} className="flex gap-3">
                  <div className="shrink-0 w-7 h-7 rounded-lg flex items-center justify-center font-mono" style={{ background: "var(--admin-amber-bg)", border: "1px solid var(--admin-amber-border)", color: "var(--admin-amber)", fontSize: 12, fontWeight: 700 }}>{step.num}</div>
                  <div>
                    <p style={{ fontSize: 14, fontWeight: 500, color: "var(--admin-text)" }}>{step.title}</p>
                    <p style={{ fontSize: 13, color: "var(--admin-muted)" }}>{step.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick reference */}
          <div className="rounded-xl p-6" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
            <h3 style={{ fontSize: 14, fontWeight: 600, color: "var(--admin-text)", marginBottom: 8 }}>Preguntas de referencia rápida</h3>
            <div className="space-y-2" style={{ fontSize: 13, color: "var(--admin-muted)" }}>
              <p>1. ¿Cómo se llama completo?</p>
              <p>2. ¿Tiene su DPI a la mano?</p>
              <p>3. ¿En qué zona vive?</p>
              <p>4. ¿En qué zonas prefiere trabajar?</p>
              <p>5. ¿Cuál es su oficio principal?</p>
              <p>6. ¿Cuántos años de experiencia tiene?</p>
              <p>7. ¿Qué trabajos puede cubrir?</p>
              <p>8. ¿Qué trabajos NO puede hacer?</p>
              <p>9. ¿Cuánto cobra por día?</p>
              <p>10. ¿Tiene 2-3 referencias laborales?</p>
            </div>
          </div>

          {!drawerOpen && (
            <button onClick={() => setDrawerOpen(true)} className="w-full rounded-xl py-4 text-center font-bold" style={{ background: "var(--admin-amber)", color: "#fff", fontSize: 15 }}>
              ✎ Abrir formulario de registro
            </button>
          )}
        </div>

        {/* Right — live preview placeholder */}
        <div className="rounded-xl p-5" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)", alignSelf: "start" }}>
          <p className="mb-4" style={{ fontSize: 12, fontWeight: 500, color: "var(--admin-dim)", textTransform: "uppercase", letterSpacing: "0.5px" }}>Vista previa del perfil</p>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold" style={{ background: "var(--admin-dim)", fontSize: 16 }}>?</div>
            <div>
              <p style={{ fontSize: 15, fontWeight: 600, color: "var(--admin-text)" }}>Nuevo trabajador</p>
              <p style={{ fontSize: 12, color: "var(--admin-muted)" }}>Completar información →</p>
            </div>
          </div>
          <div className="space-y-2">
            {["Nombre", "Oficio", "Zona", "Tarifa", "Skills"].map((f) => (
              <div key={f} className="h-4 rounded" style={{ background: "#F5F5F4", width: `${60 + Math.random() * 40}%` }} />
            ))}
          </div>
          <p className="mt-4" style={{ fontSize: 11, color: "var(--admin-dim)" }}>La vista previa se actualizará al llenar el formulario</p>
        </div>
      </div>

      <ManualRegistrationDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} onSaved={() => router.push("/admin/workers")} />
    </div>
  );
}
