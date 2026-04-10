import Link from "next/link";

/* ─── Reusable micro-components ─── */

function PulseDot({ color = "bg-amber-500" }: { color?: string }) {
  return <span className={`inline-block w-2 h-2 rounded-full ${color} animate-pulse-dot`} />;
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: "var(--amber)", letterSpacing: "1px" }}>
      {children}
    </p>
  );
}

/* ═══════════════════════════════════ NAV ═══════════════════════════════════ */

function Nav() {
  return (
    <nav
      className="fixed top-0 left-0 right-0 z-[100] flex items-center justify-between px-6 lg:px-14 h-16"
      style={{ background: "rgba(6,14,23,0.92)", backdropFilter: "blur(20px)", WebkitBackdropFilter: "blur(20px)", borderBottom: "1px solid var(--border)" }}
    >
      <Link href="/" className="flex items-center gap-2">
        <span style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: 26, letterSpacing: -1, color: "var(--text)" }}>
          CHAN<span style={{ color: "var(--amber)" }}>-C</span>
        </span>
        <PulseDot />
      </Link>

      <div className="hidden lg:flex items-center gap-8">
        {["Cómo funciona", "Para empresas", "Trabajadores", "Precios"].map((t) => (
          <a key={t} href="#" className="text-sm hover:!text-[var(--text)]" style={{ fontFamily: "'DM Sans',sans-serif", fontSize: 14, color: "var(--muted)" }}>{t}</a>
        ))}
      </div>

      <div className="flex items-center gap-3">
        <span className="hidden sm:flex items-center gap-1 rounded-full text-xs" style={{ background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.15)", padding: "4px 8px" }}>
          <span style={{ color: "var(--amber)", fontWeight: 600 }}>ES</span>
          <span style={{ color: "var(--dim)" }}>|</span>
          <span style={{ color: "var(--dim)" }}>EN</span>
        </span>
        <Link href="/login" className="hidden sm:inline-flex items-center rounded-lg px-4 py-2 text-sm hover:!border-[var(--amber)] hover:!text-[var(--amber)]" style={{ border: "1px solid var(--border)", color: "var(--muted)" }}>
          Entrar
        </Link>
        <Link href="/register" className="inline-flex items-center rounded-lg px-4 py-2 text-sm font-bold" style={{ background: "var(--amber)", color: "#060E17" }}>
          Registrar empresa&nbsp;→
        </Link>
      </div>
    </nav>
  );
}

/* ═══════════════════════════════════ HERO ═══════════════════════════════════ */

function HeroCard() {
  return (
    <div className="relative hidden lg:block">
      <div className="absolute rounded-2xl" style={{ top: 20, left: 20, right: -20, bottom: -10, zIndex: -2, opacity: 0.3, background: "var(--bg3)", border: "1px solid var(--border)" }} />
      <div className="absolute rounded-2xl" style={{ top: 10, left: 10, right: -10, bottom: 0, zIndex: -1, opacity: 0.6, background: "var(--bg3)", border: "1px solid var(--border)" }} />

      <div className="relative rounded-2xl" style={{ background: "var(--bg3)", border: "1px solid var(--border)", padding: 28, boxShadow: "0 40px 80px rgba(0,0,0,0.5)" }}>
        <div className="flex items-center gap-2 rounded-full w-fit mb-5" style={{ background: "rgba(16,185,129,0.15)", border: "1px solid rgba(16,185,129,0.25)", padding: "4px 12px" }}>
          <PulseDot color="bg-emerald-500" />
          <span style={{ color: "var(--green)", fontSize: 11 }}>IA verificó este perfil · hace 2 horas</span>
        </div>

        <div className="flex items-center gap-3.5 mb-5">
          <div className="flex items-center justify-center rounded-[14px] text-white" style={{ width: 52, height: 52, background: "linear-gradient(135deg,#1D9E75,#0F6E56)", fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: 18 }}>PR</div>
          <div>
            <p style={{ fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 18, color: "var(--text)" }}>Pedro Ramírez</p>
            <p style={{ fontSize: 13, color: "var(--muted)" }}>Electricista Senior · Zona 6, Guatemala</p>
            <div className="flex items-center gap-1.5 mt-1">
              <span style={{ color: "var(--amber)", fontSize: 13 }}>★★★★★</span>
              <span style={{ fontSize: 12, color: "var(--dim)" }}>4.9 · 23 trabajos completados</span>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-5">
          {["✓ Inst. residencial", "✓ Cableado", "✓ Tableros eléctricos"].map((s) => (
            <span key={s} className="rounded-lg" style={{ background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.15)", color: "rgba(245,158,11,0.9)", padding: "6px 12px", fontSize: 12 }}>{s}</span>
          ))}
          <span className="rounded-lg" style={{ background: "rgba(239,68,68,0.06)", border: "1px solid rgba(239,68,68,0.12)", color: "rgba(239,68,68,0.7)", padding: "6px 12px", fontSize: 12 }}>✗ Inst. trifásica</span>
        </div>

        <div className="flex items-center justify-between mb-5" style={{ borderTop: "1px solid var(--border)", borderBottom: "1px solid var(--border)", padding: "16px 0" }}>
          <div>
            <p style={{ fontSize: 13, color: "var(--muted)" }}>Tarifa diaria</p>
            <p style={{ fontSize: 11, color: "var(--dim)" }}>Disponible lun–vie</p>
          </div>
          <p><span style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: 24, color: "var(--amber)" }}>Q380</span><span style={{ fontSize: 12, color: "var(--dim)" }}>/día</span></p>
        </div>

        <div className="flex gap-2.5 mb-4">
          <button className="flex-[1.5] rounded-[10px] py-3 text-sm font-bold text-white" style={{ background: "var(--green)" }}>✓ Aceptar trabajador</button>
          <button className="flex-1 rounded-[10px] py-3 text-sm" style={{ background: "rgba(240,238,232,0.06)", border: "1px solid var(--border)", color: "var(--muted)" }}>Solicitar otro</button>
        </div>

        <div className="rounded-[10px]" style={{ background: "rgba(99,102,241,0.08)", border: "1px solid rgba(99,102,241,0.15)", padding: "10px 14px" }}>
          <p style={{ fontSize: 11, color: "rgba(200,200,255,0.6)" }}>✦ Perfil generado por entrevista de voz con IA · Referencias verificadas (3/3 positivas) · Confianza: 94%</p>
        </div>
      </div>
    </div>
  );
}

function Hero() {
  const avatars = [
    { bg: "linear-gradient(135deg,#10B981,#059669)", init: "CM" },
    { bg: "linear-gradient(135deg,#8B5CF6,#6D28D9)", init: "RA" },
    { bg: "linear-gradient(135deg,#F97316,#EA580C)", init: "LP" },
    { bg: "linear-gradient(135deg,#3B82F6,#2563EB)", init: "JV" },
  ];

  return (
    <section style={{ background: "var(--bg)", paddingTop: 160, paddingBottom: 0 }}>
      <div className="mx-auto grid grid-cols-1 lg:grid-cols-[1.1fr_0.9fr] gap-12 lg:gap-20 px-6 lg:px-14" style={{ maxWidth: 1300 }}>
        <div>
          <div className="animate-fade-in-up delay-100 flex items-center gap-2 rounded-full w-fit mb-6" style={{ background: "rgba(245,158,11,0.1)", border: "1px solid rgba(245,158,11,0.2)", padding: "6px 14px" }}>
            <PulseDot />
            <span style={{ color: "var(--amber)", fontSize: 12, fontWeight: 600, letterSpacing: 0.5 }}>PRIMER MARKETPLACE DE CONSTRUCCIÓN CON IA EN GUATEMALA</span>
          </div>

          <h1 className="animate-fade-in-up delay-200 mb-6" style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: "clamp(36px, 5vw, 62px)", letterSpacing: -2.5, lineHeight: 1.05, color: "var(--text)" }}>
            Contrata al trabajador{" "}
            <em className="not-italic relative inline-block" style={{ color: "var(--amber)" }}>
              correcto
              <span className="absolute left-0 right-0" style={{ bottom: -4, height: 3, background: "var(--amber)", opacity: 0.4, borderRadius: 2 }} />
            </em>{" "}
            en menos de 48 horas
          </h1>

          <p className="animate-fade-in-up delay-300 mb-8" style={{ fontFamily: "'DM Sans',sans-serif", fontSize: 18, fontWeight: 300, color: "var(--muted)", lineHeight: 1.6, maxWidth: 540 }}>
            Conectamos empresas constructoras con trabajadores verificados por IA. Agentes de voz que entrevistan, extraen habilidades y verifican referencias — <strong style={{ color: "var(--text)", fontWeight: 500 }}>sin que el trabajador necesite smartphone.</strong>
          </p>

          <div className="animate-fade-in-up delay-400 flex flex-wrap gap-3 mb-8">
            <Link href="/register" className="inline-flex items-center rounded-[10px] font-bold hover:!bg-[var(--amber2)]" style={{ background: "var(--amber)", color: "#060E17", padding: "16px 36px", fontSize: 16 }}>
              Registrar mi empresa&nbsp;→
            </Link>
            <a href="#como-funciona" className="inline-flex items-center rounded-[10px] hover:!border-[rgba(240,238,232,0.3)]" style={{ border: "1px solid var(--border)", color: "var(--text)", padding: "16px 32px", fontSize: 15, fontWeight: 500 }}>
              ▶ Ver cómo funciona
            </a>
          </div>

          <div className="animate-fade-in-up delay-500 flex items-center gap-3">
            <div className="flex">
              {avatars.map((a, i) => (
                <div key={i} className="flex items-center justify-center rounded-full text-white" style={{ width: 36, height: 36, background: a.bg, marginLeft: i === 0 ? 0 : -10, border: "2px solid var(--bg)", fontSize: 11, fontWeight: 700, zIndex: 4 - i, position: "relative" }}>
                  {a.init}
                </div>
              ))}
              <div className="flex items-center justify-center rounded-full" style={{ width: 36, height: 36, background: "var(--bg3)", border: "1px solid var(--border)", marginLeft: -10, fontSize: 10, color: "var(--muted)", fontWeight: 600, position: "relative" }}>+40</div>
            </div>
            <p style={{ fontSize: 13, color: "var(--muted)" }}>
              Más de <span style={{ color: "var(--amber)", fontWeight: 600 }}>40 empresas</span> ya confían en CHAN-C
            </p>
          </div>
        </div>

        <HeroCard />
      </div>
    </section>
  );
}

/* ═══════════════════════════════════ LOGOS ═══════════════════════════════════ */

function LogosBar() {
  return (
    <section style={{ background: "var(--bg2)", borderTop: "1px solid var(--border)", borderBottom: "1px solid var(--border)", padding: "48px 24px", marginTop: 80 }}>
      <div className="mx-auto flex flex-col sm:flex-row items-center gap-6 sm:gap-12 flex-wrap justify-center" style={{ maxWidth: 1300 }}>
        <span className="text-xs uppercase" style={{ color: "var(--dim)", letterSpacing: 1 }}>Confiado por</span>
        {["Constructora XYZ", "Arq. & Asociados", "ProBuild GT", "Inmobiliaria Capital", "Diseños Urbanos"].map((n) => (
          <span key={n} style={{ fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 15, color: "var(--dim)" }}>{n}</span>
        ))}
      </div>
    </section>
  );
}

/* ═══════════════════════════════════ NUMBERS ═══════════════════════════════════ */

function Numbers() {
  const data = [
    { num: "500", suffix: "+", label: "Trabajadores verificados por IA en Guatemala City" },
    { num: "48", suffix: "h", label: "Tiempo promedio para recibir tu primer match" },
    { num: "4.9", suffix: "★", label: "Calificación promedio de trabajadores en la red" },
    { num: "0", suffix: "%", label: "Trabajadores sin verificar. Todos pasan por IA" },
  ];

  return (
    <section className="px-6 lg:px-14" style={{ paddingTop: 100 }}>
      <div className="mx-auto grid grid-cols-2 lg:grid-cols-4 overflow-hidden rounded-2xl" style={{ maxWidth: 1300, border: "1px solid var(--border)", gap: 1, background: "var(--border)" }}>
        {data.map((d) => (
          <div key={d.num} style={{ background: "var(--bg2)", padding: "40px 36px" }}>
            <p style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: "clamp(36px, 4vw, 52px)", letterSpacing: -2, color: "var(--text)" }}>
              {d.num}<span style={{ color: "var(--amber)" }}>{d.suffix}</span>
            </p>
            <p style={{ fontSize: 14, color: "var(--muted)", lineHeight: 1.5, marginTop: 8 }}>{d.label}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ═══════════════════════════════════ STEPS ═══════════════════════════════════ */

function Steps() {
  const steps = [
    { n: "01", icon: "📋", title: "Publica tu trabajo", desc: "Describe el oficio que necesitas, la zona, las fechas y el presupuesto. Menos de 3 minutos.", pills: ["Electricista", "Plomero", "Albañil", "+8 oficios"] },
    { n: "02", icon: "🤖", title: "La IA hace el trabajo", desc: "Nuestro agente de voz llama al trabajador en español, extrae sus habilidades y verifica sus referencias automáticamente.", pills: ["Entrevista por voz", "Referencias", "Puntuación IA"] },
    { n: "03", icon: "🤝", title: "Tú decides y conectas", desc: "Recibes el perfil completo verificado. Si aceptas, obtienes el contacto directo. Solo pagas cuando contratas.", pills: ["Perfil verificado", "Contacto directo", "Sin riesgo"] },
  ];

  return (
    <section id="como-funciona" className="px-6 lg:px-14" style={{ paddingTop: 100 }}>
      <div className="mx-auto" style={{ maxWidth: 1300 }}>
        <SectionLabel>PROCESO</SectionLabel>
        <h2 className="mb-3" style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: "clamp(32px, 4vw, 48px)", letterSpacing: -2, color: "var(--text)", lineHeight: 1.1 }}>
          Tres pasos.<br />Un trabajador verificado.
        </h2>
        <p className="mb-12" style={{ fontSize: 16, color: "var(--muted)", maxWidth: 460 }}>Sin llamadas en frío. Sin referencias dudosas. Sin perder tiempo.</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {steps.map((s) => (
            <div key={s.n} className="relative overflow-hidden rounded-2xl hover:!border-[rgba(245,158,11,0.3)]" style={{ background: "var(--bg2)", border: "1px solid var(--border)", padding: 36 }}>
              <span className="absolute select-none pointer-events-none" style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: 120, color: "rgba(245,158,11,0.04)", top: -20, right: -10 }}>{s.n}</span>
              <div className="flex items-center justify-center rounded-2xl mb-6" style={{ width: 56, height: 56, background: "rgba(245,158,11,0.1)", border: "1px solid rgba(245,158,11,0.15)", fontSize: 26 }}>{s.icon}</div>
              <h3 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 21, letterSpacing: -0.5, color: "var(--text)", marginBottom: 12 }}>{s.title}</h3>
              <p style={{ fontSize: 14, color: "var(--muted)", lineHeight: 1.7, marginBottom: 20 }}>{s.desc}</p>
              <div className="flex flex-wrap gap-2">
                {s.pills.map((p) => (
                  <span key={p} className="rounded-full" style={{ background: "var(--bg3)", border: "1px solid var(--border)", color: "var(--dim)", padding: "4px 10px", fontSize: 11 }}>{p}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════ AI SECTION ═══════════════════════════════════ */

function AIChat() {
  return (
    <div className="rounded-2xl" style={{ background: "var(--bg3)", border: "1px solid var(--border)", padding: 32 }}>
      <p className="mb-5 uppercase" style={{ fontSize: 11, color: "var(--dim)", letterSpacing: 1 }}>CONVERSACIÓN EN TIEMPO REAL</p>
      <div className="space-y-4 mb-5">
        <div className="flex gap-2.5">
          <div className="shrink-0 flex items-center justify-center rounded-full text-xs font-bold" style={{ width: 32, height: 32, background: "rgba(245,158,11,0.15)", color: "var(--amber)" }}>AI</div>
          <div>
            <div className="rounded-xl" style={{ background: "var(--bg2)", border: "1px solid var(--border)", borderTopLeftRadius: 4, padding: "10px 14px", maxWidth: 280 }}>
              <p style={{ fontSize: 13, color: "var(--text)", lineHeight: 1.5 }}>Hola Pedro, soy del equipo de CHAN-C. ¿Tienes unos minutos para una entrevista rápida sobre tus habilidades?</p>
            </div>
            <p style={{ fontSize: 10, color: "var(--dim)", marginTop: 4 }}>Agente IA · hace 2 min</p>
          </div>
        </div>
        <div className="flex gap-2.5 flex-row-reverse">
          <div className="shrink-0 flex items-center justify-center rounded-full text-xs font-bold" style={{ width: 32, height: 32, background: "rgba(16,185,129,0.15)", color: "var(--green)" }}>PR</div>
          <div className="flex flex-col items-end">
            <div className="rounded-xl" style={{ background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.15)", borderTopRightRadius: 4, padding: "10px 14px", maxWidth: 280 }}>
              <p style={{ fontSize: 13, color: "var(--text)", lineHeight: 1.5 }}>Sí, con gusto. Tengo 12 años de experiencia en electricidad residencial.</p>
            </div>
            <p style={{ fontSize: 10, color: "var(--dim)", marginTop: 4 }}>Pedro R. · hace 1 min</p>
          </div>
        </div>
        <div className="flex gap-2.5">
          <div className="shrink-0 flex items-center justify-center rounded-full text-xs font-bold" style={{ width: 32, height: 32, background: "rgba(245,158,11,0.15)", color: "var(--amber)" }}>AI</div>
          <div className="rounded-xl" style={{ background: "var(--bg2)", border: "1px solid var(--border)", borderTopLeftRadius: 4, padding: "10px 14px", maxWidth: 280 }}>
            <p style={{ fontSize: 13, color: "var(--text)", lineHeight: 1.5 }}>Perfecto. ¿Trabajas con instalaciones trifásicas industriales?</p>
          </div>
        </div>
      </div>

      <div className="rounded-xl" style={{ background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.2)", padding: 16 }}>
        <p className="mb-3 uppercase" style={{ fontSize: 11, color: "var(--green)", letterSpacing: 1, fontWeight: 600 }}>✦ Datos extraídos por IA</p>
        {[
          ["Oficio", "Electricista Senior", undefined],
          ["Experiencia", "12 años", undefined],
          ["Tarifa", "Q380/día", undefined],
          ["Referencias", "3/3 positivas ✓", "var(--green)"],
          ["Confianza IA", "94%", "var(--amber)"],
        ].map(([k, v, c], i, a) => (
          <div key={k} className="flex justify-between py-2" style={{ fontSize: 12, borderBottom: i < a.length - 1 ? "1px solid rgba(16,185,129,0.08)" : "none" }}>
            <span style={{ color: "var(--dim)" }}>{k}</span>
            <span style={{ color: c || "var(--text)", fontWeight: 500 }}>{v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function AISection() {
  const features = [
    { icon: "🎙️", title: "Entrevistas de voz en español", desc: "Agentes de IA llaman a cada trabajador, hacen 14 preguntas y extraen sus habilidades reales en una llamada de 8 minutos." },
    { icon: "📱", title: "SMS y WhatsApp — sin smartphone", desc: "Los trabajadores responden por mensaje. No necesitan app, ni internet, ni saber escribir bien." },
    { icon: "🔍", title: "Referencias verificadas automáticamente", desc: "El agente llama a cada referencia, extrae el resultado y lo incluye en el perfil con un puntaje de confianza." },
    { icon: "🔒", title: "Contacto protegido — nunca listas", desc: "Solo recibes el contacto del trabajador que aceptaste. Nunca una lista para copiar." },
  ];

  return (
    <section style={{ background: "var(--bg2)", borderTop: "1px solid var(--border)", borderBottom: "1px solid var(--border)", marginTop: 100 }}>
      <div className="mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-24 px-6 lg:px-14 py-24" style={{ maxWidth: 1300 }}>
        <div>
          <SectionLabel>TECNOLOGÍA</SectionLabel>
          <h2 className="mb-3" style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: "clamp(30px, 3.5vw, 42px)", color: "var(--text)", lineHeight: 1.15 }}>
            IA que trabaja<br />mientras tú construyes
          </h2>
          <p className="mb-8" style={{ fontSize: 15, color: "var(--muted)", maxWidth: 420 }}>El primer marketplace en Guatemala con agentes de voz que entrevistan y verifican — en español, K&apos;iche y Mam.</p>
          <div className="space-y-1">
            {features.map((f) => (
              <div key={f.title} className="flex gap-4 p-5 rounded-[14px] hover:!bg-[var(--bg3)]" style={{ border: "1px solid transparent" }}>
                <div className="shrink-0 flex items-center justify-center rounded-xl" style={{ width: 44, height: 44, background: "rgba(245,158,11,0.1)", border: "1px solid rgba(245,158,11,0.15)", fontSize: 20 }}>{f.icon}</div>
                <div>
                  <h4 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 15, color: "var(--text)", marginBottom: 4 }}>{f.title}</h4>
                  <p style={{ fontSize: 13, color: "var(--muted)", lineHeight: 1.6 }}>{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        <AIChat />
      </div>
    </section>
  );
}

/* ═══════════════════════════════════ SMS DEMO ═══════════════════════════════════ */

function PhoneFrame() {
  return (
    <div className="mx-auto rounded-[32px]" style={{ background: "var(--bg2)", border: "2px solid var(--border)", padding: 24, width: 280 }}>
      <div className="mx-auto rounded mb-5" style={{ width: 80, height: 8, background: "var(--bg3)" }} />
      <div className="flex items-center gap-3 mb-5">
        <div className="flex items-center justify-center rounded-[10px]" style={{ width: 36, height: 36, background: "var(--amber)", fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: 12, color: "#060E17" }}>CC</div>
        <div>
          <p style={{ fontSize: 14, fontWeight: 600, color: "var(--text)" }}>CHAN-C</p>
          <p style={{ fontSize: 11, color: "var(--green)" }}>● En línea</p>
        </div>
      </div>
      <div className="space-y-3 mb-4">
        <div className="rounded-[14px]" style={{ background: "var(--bg3)", border: "1px solid var(--border)", borderBottomLeftRadius: 4, padding: "10px 12px", maxWidth: 220 }}>
          <p style={{ fontSize: 13, color: "var(--text)", lineHeight: 1.45 }}>Hola Juan. Trabajo de plomería en Zona 10. Lun 7 - Vie 11. Q320/día. ¿Te interesa?</p>
          <p style={{ fontSize: 10, color: "var(--dim)", marginTop: 4 }}>10:24 AM</p>
        </div>
        <div className="ml-auto rounded-[14px]" style={{ background: "rgba(245,158,11,0.15)", border: "1px solid rgba(245,158,11,0.25)", borderBottomRightRadius: 4, padding: "10px 12px", maxWidth: 220, width: "fit-content" }}>
          <p style={{ fontSize: 13, color: "var(--amber)", fontWeight: 600 }}>SI</p>
          <p className="text-right" style={{ fontSize: 10, color: "var(--dim)", marginTop: 4 }}>10:25 AM</p>
        </div>
        <div className="rounded-[14px]" style={{ background: "var(--bg3)", border: "1px solid var(--border)", borderBottomLeftRadius: 4, padding: "10px 12px", maxWidth: 220 }}>
          <p style={{ fontSize: 13, color: "var(--text)", lineHeight: 1.45 }}>Gracias. Te llamamos para confirmar detalles. 📞</p>
          <p style={{ fontSize: 10, color: "var(--dim)", marginTop: 4 }}>10:25 AM</p>
        </div>
      </div>
      <div className="flex gap-1.5">
        {[
          { label: "SI", border: "rgba(16,185,129,0.3)", color: "var(--green)" },
          { label: "NO", border: "rgba(239,68,68,0.2)", color: "rgba(239,68,68,0.7)" },
          { label: "CONTRA", border: "rgba(245,158,11,0.3)", color: "rgba(245,158,11,0.8)" },
        ].map((b) => (
          <div key={b.label} className="flex-1 text-center rounded-lg py-2" style={{ background: "var(--bg3)", border: `1px solid ${b.border}`, color: b.color, fontSize: 12, fontWeight: 600 }}>{b.label}</div>
        ))}
      </div>
    </div>
  );
}

function SMSDemo() {
  return (
    <section className="px-6 lg:px-14" style={{ paddingTop: 100 }}>
      <div className="mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-24 items-center" style={{ maxWidth: 1300 }}>
        <div className="order-2 lg:order-1">
          <SectionLabel>PARA TRABAJADORES</SectionLabel>
          <h2 className="mb-3" style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: "clamp(30px, 3.5vw, 42px)", color: "var(--text)", lineHeight: 1.15 }}>
            Sin app.<br />Solo un mensaje.
          </h2>
          <p className="mb-8" style={{ fontSize: 15, color: "var(--muted)", maxWidth: 420 }}>Los trabajadores solo necesitan un teléfono básico. Textan &apos;TRABAJAR&apos; y reciben una llamada para registrarse. Sin internet, sin descargas.</p>
          <div className="space-y-3">
            {[
              { icon: "💬", title: "Textan TRABAJAR", desc: "Al número de CHAN-C. Funciona con cualquier teléfono básico." },
              { icon: "📞", title: "Reciben llamada de IA", desc: "Entrevista de 8 minutos en español. Amable y clara." },
              { icon: "✅", title: "Perfil verificado y activo", desc: "En menos de 24 horas reciben SMS de confirmación." },
            ].map((f) => (
              <div key={f.title} className="flex gap-3.5 rounded-[14px] p-4" style={{ background: "var(--bg2)", border: "1px solid var(--border)" }}>
                <div className="shrink-0 flex items-center justify-center rounded-[10px]" style={{ width: 40, height: 40, background: "rgba(245,158,11,0.1)", border: "1px solid rgba(245,158,11,0.15)", fontSize: 18 }}>{f.icon}</div>
                <div>
                  <h4 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 14, color: "var(--text)", marginBottom: 2 }}>{f.title}</h4>
                  <p style={{ fontSize: 13, color: "var(--muted)", lineHeight: 1.5 }}>{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="order-1 lg:order-2">
          <PhoneFrame />
        </div>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════ TRUST ═══════════════════════════════════ */

function Trust() {
  const cards = [
    { icon: "🏗️", title: "Solo construcción", desc: "Electricistas, plomeros, albañiles, carpinteros. Especialistas en el sector, no generalistas." },
    { icon: "🪪", title: "DPI verificado", desc: "Cada trabajador pasa por verificación de identidad, entrevista de habilidades y referencias laborales." },
    { icon: "🗣️", title: "Español, K'iche, Mam", desc: "Accesible para todos los trabajadores de Guatemala, incluyendo comunidades indígenas." },
    { icon: "💰", title: "Solo pagas al contratar", desc: "Sin suscripción obligatoria. Sin costo de búsqueda. Solo una comisión cuando el trabajo inicia." },
  ];

  return (
    <section className="px-6 lg:px-14" style={{ paddingTop: 100 }}>
      <div className="mx-auto" style={{ maxWidth: 1300 }}>
        <SectionLabel>POR QUÉ CHAN-C</SectionLabel>
        <h2 className="mb-14" style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: "clamp(32px, 4vw, 48px)", color: "var(--text)", letterSpacing: -2 }}>Construido para Guatemala</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {cards.map((c) => (
            <div key={c.title} className="rounded-2xl hover:!border-[rgba(245,158,11,0.25)] hover:-translate-y-1" style={{ background: "var(--bg2)", border: "1px solid var(--border)", padding: 32 }}>
              <div className="text-3xl mb-4">{c.icon}</div>
              <h3 style={{ fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 17, color: "var(--text)", marginBottom: 8 }}>{c.title}</h3>
              <p style={{ fontSize: 13, color: "var(--muted)", lineHeight: 1.6 }}>{c.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════ TESTIMONIAL ═══════════════════════════════════ */

function Testimonial() {
  return (
    <section style={{ background: "var(--bg2)", borderTop: "1px solid var(--border)", marginTop: 100 }}>
      <div className="mx-auto px-6 lg:px-14 py-24" style={{ maxWidth: 1300 }}>
        <SectionLabel>TESTIMONIOS</SectionLabel>
        <div className="relative">
          <span className="absolute select-none pointer-events-none" style={{ fontFamily: "Georgia,serif", fontSize: 80, color: "var(--amber)", opacity: 0.3, top: -30, left: -10 }}>&ldquo;</span>
          <blockquote className="pl-2 mb-8" style={{ fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: "clamp(24px, 3vw, 36px)", letterSpacing: -1, lineHeight: 1.2, color: "var(--text)", maxWidth: 800 }}>
            CHAN-C nos ahorró semanas de búsqueda. El electricista llegó{" "}
            <em className="not-italic" style={{ color: "var(--amber)" }}>verificado, puntual y exactamente con las habilidades que necesitábamos.</em>
          </blockquote>
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center rounded-xl text-white" style={{ width: 48, height: 48, background: "linear-gradient(135deg,#3C3489,#534AB7)", fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: 16 }}>CM</div>
            <div>
              <p style={{ fontWeight: 600, fontSize: 15, color: "var(--text)" }}>Carlos Morales</p>
              <p style={{ fontSize: 13, color: "var(--muted)" }}>Director de Obra · Constructora Moderna Guatemala</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════ CTA ═══════════════════════════════════ */

function CTASection() {
  return (
    <section className="relative overflow-hidden text-center" style={{ background: "var(--amber)", padding: "120px 24px" }}>
      <div className="absolute inset-0 pointer-events-none" style={{ backgroundImage: "linear-gradient(rgba(6,14,23,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(6,14,23,0.06) 1px, transparent 1px)", backgroundSize: "40px 40px" }} />
      <div className="relative mx-auto" style={{ maxWidth: 700 }}>
        <h2 className="mb-4" style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: "clamp(36px, 5vw, 60px)", color: "#060E17", letterSpacing: -2.5, lineHeight: 1 }}>
          ¿Listo para contratar<br />de forma inteligente?
        </h2>
        <p className="mb-8" style={{ fontSize: 18, fontWeight: 300, color: "rgba(6,14,23,0.65)" }}>Registra tu empresa hoy. Tu primer match verificado en menos de 48 horas.</p>
        <div className="flex flex-wrap justify-center gap-3 mb-6">
          <Link href="/register" className="inline-flex items-center rounded-xl font-bold hover:!bg-[#0C1A28]" style={{ background: "#060E17", color: "var(--amber)", padding: "18px 48px", fontSize: 17 }}>
            Registrar mi empresa gratis&nbsp;→
          </Link>
          <a href="#" className="inline-flex items-center rounded-xl font-semibold" style={{ border: "2px solid rgba(6,14,23,0.25)", color: "#060E17", padding: "18px 40px", fontSize: 16 }}>
            Hablar con el equipo
          </a>
        </div>
        <p style={{ fontSize: 13, color: "rgba(6,14,23,0.45)" }}>Sin tarjeta de crédito · Sin contrato · Solo resultados</p>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════ FOOTER ═══════════════════════════════════ */

function LandingFooter() {
  return (
    <footer style={{ background: "#030A12", borderTop: "1px solid var(--border)", padding: "60px 24px" }}>
      <div className="mx-auto grid grid-cols-2 lg:grid-cols-[2fr_1fr_1fr_1fr] gap-10 lg:gap-16" style={{ maxWidth: 1300 }}>
        <div className="col-span-2 lg:col-span-1">
          <p className="mb-3" style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: 20, color: "var(--text)" }}>CHAN<span style={{ color: "var(--amber)" }}>-C</span></p>
          <p className="mb-4" style={{ fontSize: 13, color: "var(--muted)", maxWidth: 260, lineHeight: 1.6 }}>El primer marketplace de construcción con IA en Guatemala. Verificamos trabajadores para que tú construyas con confianza.</p>
          <span className="inline-flex items-center gap-1 rounded-md" style={{ background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.15)", color: "rgba(245,158,11,0.7)", padding: "4px 10px", fontSize: 11 }}>🇬🇹 Hecho en Guatemala</span>
        </div>
        {[
          { title: "PLATAFORMA", links: ["Cómo funciona", "Para empresas", "Para trabajadores", "Precios", "Registrarse"] },
          { title: "OFICIOS", links: ["Electricistas", "Plomeros", "Albañiles", "Carpinteros", "Ver todos"] },
          { title: "EMPRESA", links: ["Sobre nosotros", "Contacto", "Privacidad", "Términos"] },
        ].map((col) => (
          <div key={col.title}>
            <p className="mb-4 uppercase" style={{ fontSize: 13, fontWeight: 700, color: "var(--dim)", letterSpacing: 1 }}>{col.title}</p>
            <div className="space-y-2.5">
              {col.links.map((l) => (
                <a key={l} href="#" className="block hover:!text-[var(--text)]" style={{ fontSize: 13, color: "var(--muted)" }}>{l}</a>
              ))}
            </div>
          </div>
        ))}
      </div>
      <div className="mx-auto flex flex-col sm:flex-row justify-between items-center gap-2 mt-10 pt-6" style={{ maxWidth: 1300, borderTop: "1px solid var(--border)" }}>
        <span style={{ fontSize: 12, color: "var(--dim)" }}>© 2025 CHAN-C · Guatemala City</span>
        <span style={{ fontSize: 12, color: "var(--dim)" }}>Construido con IA · Para Guatemala</span>
      </div>
    </footer>
  );
}

/* ═══════════════════════════════════ PAGE ═══════════════════════════════════ */

export default function LandingPage() {
  return (
    <div className="landing" style={{ background: "var(--bg)" }}>
      <Nav />
      <Hero />
      <LogosBar />
      <Numbers />
      <Steps />
      <AISection />
      <SMSDemo />
      <Trust />
      <Testimonial />
      <CTASection />
      <LandingFooter />
    </div>
  );
}
