"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { isAuthenticated, getCurrentUser } from "@/lib/auth";
import {
  LayoutDashboard, GitPullRequest, Briefcase, MessageSquare,
  Users, UserPlus, Clock, Building2, ShieldCheck,
  Brain, PhoneCall, CreditCard, PenLine, MessageCircle,
} from "lucide-react";

const NAV = [
  { section: "OVERVIEW", items: [
    { href: "/admin", label: "Dashboard", icon: LayoutDashboard },
  ]},
  { section: "OPERACIONES", items: [
    { href: "/admin/matches", label: "Matches", icon: GitPullRequest, badge: true },
    { href: "/admin/jobs", label: "Trabajos", icon: Briefcase },
    { href: "/admin/whatsapp", label: "WhatsApp", icon: MessageCircle, badge: true },
    { href: "/admin/sms", label: "SMS Logs", icon: MessageSquare },
  ]},
  { section: "TRABAJADORES", items: [
    { href: "/admin/workers", label: "Pool activo", icon: Users },
    { href: "/admin/recruitment", label: "Reclutamiento", icon: UserPlus, badge: true },
    { href: "/admin/workers/pending", label: "Pendientes aprobación", icon: Clock, badgeRed: true },
    { href: "/admin/workers/manual", label: "Registro manual", icon: PenLine },
  ]},
  { section: "EMPRESAS", items: [
    { href: "/admin/companies", label: "Empresas activas", icon: Building2 },
    { href: "/admin/companies/pending", label: "Pendientes aprobación", icon: ShieldCheck, badgeRed: true },
  ]},
  { section: "IA & LLAMADAS", items: [
    { href: "/admin/ai", label: "Pipeline de IA", icon: Brain },
    { href: "/admin/ai/calls", label: "Llamadas", icon: PhoneCall },
  ]},
  { section: "FINANZAS", items: [
    { href: "/admin/billing", label: "Comisiones", icon: CreditCard },
  ]},
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [manualMode, setManualMode] = useState(false);

  useEffect(() => {
    setManualMode(localStorage.getItem("chanc_manual_mode") === "true");
  }, []);

  const toggleManualMode = () => {
    const next = !manualMode;
    setManualMode(next);
    localStorage.setItem("chanc_manual_mode", String(next));
  };

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    const user = getCurrentUser();
    if (user?.role !== "admin") { router.push("/login"); }
  }, [router]);

  const isActive = (href: string) => {
    if (href === "/admin") return pathname === "/admin";
    return pathname.startsWith(href);
  };

  return (
    <div className="admin-shell flex min-h-screen" style={{ background: "var(--admin-bg)" }}>
      {/* Sidebar */}
      <aside className="fixed top-0 left-0 bottom-0 w-60 overflow-y-auto" style={{ background: "var(--admin-surface)", borderRight: "1px solid var(--admin-border)" }}>
        <div className="px-5 py-5 flex items-center gap-2" style={{ borderBottom: "1px solid var(--admin-border)" }}>
          <span style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: 600, fontSize: 18, color: "var(--admin-text)" }}>
            CHAN<span style={{ color: "var(--admin-amber)" }}>-C</span>
          </span>
          <span className="rounded px-1.5 py-0.5" style={{ background: "var(--admin-purple-bg)", border: "1px solid var(--admin-purple-border)", color: "var(--admin-purple)", fontSize: 10, fontWeight: 600 }}>Admin</span>
        </div>

        <nav className="px-3 py-4">
          {NAV.map((group) => (
            <div key={group.section} className="mb-5">
              <p className="px-3 mb-2 uppercase" style={{ fontSize: 10, fontWeight: 600, letterSpacing: "1px", color: "var(--admin-dim)" }}>{group.section}</p>
              {group.items.map((item) => {
                const active = isActive(item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="flex items-center gap-2.5 px-3 py-2 rounded-lg mb-0.5"
                    style={{
                      fontSize: 13,
                      fontFamily: "'DM Sans',sans-serif",
                      color: active ? "var(--admin-amber)" : "var(--admin-muted)",
                      background: active ? "var(--admin-amber-bg)" : "transparent",
                      borderLeft: active ? "3px solid var(--admin-amber)" : "3px solid transparent",
                      fontWeight: active ? 500 : 400,
                    }}
                  >
                    <item.icon style={{ width: 16, height: 16 }} />
                    <span className="flex-1">{item.label}</span>
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>

        {/* Manual Mode toggle */}
        <div className="px-4 py-4 mt-auto" style={{ borderTop: "1px solid var(--admin-border)" }}>
          <button onClick={toggleManualMode} className="flex items-center gap-2 w-full rounded-lg px-3 py-2" style={{ background: manualMode ? "var(--admin-amber-bg)" : "transparent", border: `1px solid ${manualMode ? "var(--admin-amber-border)" : "var(--admin-border)"}` }}>
            {manualMode && <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: "var(--admin-amber)" }} />}
            <span style={{ fontSize: 12, fontWeight: 500, color: manualMode ? "var(--admin-amber)" : "var(--admin-dim)" }}>
              Modo manual {manualMode ? "ON" : "OFF"}
            </span>
          </button>
          {manualMode && <p style={{ fontSize: 10, color: "var(--admin-dim)", marginTop: 4, paddingLeft: 12 }}>Pipeline de IA pausado</p>}
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 ml-60" style={{ padding: "32px 40px", minHeight: "100vh" }}>
        {children}
      </main>
    </div>
  );
}
