"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { isAuthenticated, getCurrentUser } from "@/lib/auth";
import {
  LayoutDashboard, GitPullRequest, Briefcase, MessageSquare,
  Users, UserPlus, Clock, Building2, ShieldCheck,
  Brain, PhoneCall, CreditCard,
} from "lucide-react";

const NAV = [
  { section: "OVERVIEW", items: [
    { href: "/admin", label: "Dashboard", icon: LayoutDashboard },
  ]},
  { section: "OPERACIONES", items: [
    { href: "/admin/matches", label: "Matches", icon: GitPullRequest, badge: true },
    { href: "/admin/jobs", label: "Trabajos", icon: Briefcase },
    { href: "/admin/sms", label: "SMS Logs", icon: MessageSquare },
  ]},
  { section: "TRABAJADORES", items: [
    { href: "/admin/workers", label: "Pool activo", icon: Users },
    { href: "/admin/recruitment", label: "Reclutamiento", icon: UserPlus, badge: true },
    { href: "/admin/workers/pending", label: "Pendientes aprobación", icon: Clock, badgeRed: true },
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
      </aside>

      {/* Main */}
      <main className="flex-1 ml-60" style={{ padding: "32px 40px", minHeight: "100vh" }}>
        {children}
      </main>
    </div>
  );
}
