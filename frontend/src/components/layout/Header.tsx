"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { Menu, X, LogOut, User } from "lucide-react";
import { removeToken, isAuthenticated, getCurrentUser } from "@/lib/auth";
import Button from "@/components/ui/Button";

export default function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);
  const authed = isAuthenticated();

  const handleLogout = () => {
    removeToken();
    router.push("/login");
  };

  return (
    <header className="bg-[#1C2B3A] text-white sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          <Link href={authed ? "/dashboard" : "/"} className="flex items-center gap-2">
            <span className="text-xl font-bold tracking-tight">
              CHAN<span className="text-amber-400">-C</span>
            </span>
          </Link>

          {authed && (
            <nav className="hidden md:flex items-center gap-6">
              {[
                { href: "/dashboard", label: "Panel" },
                { href: "/jobs", label: "Trabajos" },
                { href: "/matches", label: "Matches" },
              ].map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`text-sm font-medium transition-colors ${
                    pathname.startsWith(link.href)
                      ? "text-amber-400"
                      : "text-slate-300 hover:text-white"
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </nav>
          )}

          <div className="flex items-center gap-3">
            {authed ? (
              <>
                <button
                  onClick={handleLogout}
                  className="hidden md:flex items-center gap-1.5 text-sm text-slate-300 hover:text-white transition-colors"
                >
                  <LogOut className="h-4 w-4" />
                  Salir
                </button>
                <button
                  className="md:hidden text-slate-300"
                  onClick={() => setMobileOpen(!mobileOpen)}
                >
                  {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                </button>
              </>
            ) : (
              <div className="flex items-center gap-2">
                <Link href="/login">
                  <Button variant="ghost" size="sm" className="text-slate-300 hover:text-white hover:bg-white/10">
                    Entrar
                  </Button>
                </Link>
                <Link href="/register">
                  <Button size="sm">Registrarse</Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {mobileOpen && authed && (
        <div className="md:hidden border-t border-slate-700 px-4 py-3 space-y-2">
          {[
            { href: "/dashboard", label: "Panel" },
            { href: "/jobs", label: "Trabajos" },
            { href: "/matches", label: "Matches" },
          ].map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="block py-2 text-sm text-slate-300 hover:text-white"
              onClick={() => setMobileOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          <button
            onClick={handleLogout}
            className="block py-2 text-sm text-slate-300 hover:text-white"
          >
            Cerrar sesión
          </button>
        </div>
      )}
    </header>
  );
}
