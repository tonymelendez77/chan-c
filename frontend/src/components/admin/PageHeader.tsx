"use client";

import { ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  backHref?: string;
  children?: React.ReactNode;
}

export default function PageHeader({ title, subtitle, backHref, children }: PageHeaderProps) {
  const router = useRouter();
  return (
    <div className="flex items-start justify-between mb-8">
      <div>
        {backHref && (
          <button onClick={() => router.push(backHref)} className="flex items-center gap-1 text-sm mb-2" style={{ color: "var(--admin-muted)" }}>
            <ArrowLeft className="h-3.5 w-3.5" /> Volver
          </button>
        )}
        <h1 style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: 600, fontSize: 24, color: "var(--admin-text)" }}>{title}</h1>
        {subtitle && <p className="mt-1" style={{ fontSize: 14, color: "var(--admin-muted)" }}>{subtitle}</p>}
      </div>
      {children && <div className="flex items-center gap-2">{children}</div>}
    </div>
  );
}
