"use client";

import { useEffect, useState } from "react";
import { use } from "react";
import Link from "next/link";
import Card from "@/components/ui/Card";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import EmptyState from "@/components/ui/EmptyState";
import WorkerProfileCard from "@/components/workers/WorkerProfileCard";
import { ArrowLeft } from "lucide-react";
import api from "@/lib/api";
import type { Worker } from "@/lib/types";

export default function WorkerDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [worker, setWorker] = useState<Worker | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get(`/api/workers/${id}`);
        setWorker(res.data);
      } catch { /* handled */ }
      finally { setLoading(false); }
    }
    load();
  }, [id]);

  if (loading) return <LoadingSpinner />;
  if (!worker) return <EmptyState title="Trabajador no encontrado" description="Este perfil no existe." />;

  return (
    <div className="space-y-6 max-w-2xl">
      <Link href="/matches" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700">
        <ArrowLeft className="h-4 w-4" /> Volver
      </Link>

      {worker.paused && (
        <Card className="!border-amber-300 !bg-amber-50">
          <p className="text-sm text-amber-700 font-medium">Este trabajador no está disponible actualmente. Puedes solicitar otro trabajador.</p>
        </Card>
      )}

      <WorkerProfileCard worker={worker} />

      {worker.profile?.bio && (
        <Card>
          <h3 className="font-semibold text-slate-900 mb-2">Acerca del trabajador</h3>
          <p className="text-sm text-slate-600 whitespace-pre-line">{worker.profile.bio}</p>
        </Card>
      )}

      {worker.trades && worker.trades.length > 0 && (
        <Card>
          <h3 className="font-semibold text-slate-900 mb-3">Habilidades</h3>
          {worker.trades.map((t) => {
            const toolsBadge = t.tools_status === "own_tools" ? { cls: "bg-emerald-50 text-emerald-700 border-emerald-200", label: "🔧 Tiene sus herramientas" }
              : t.tools_status === "partial_tools" ? { cls: "bg-amber-50 text-amber-700 border-amber-200", label: "🔨 Tiene algunas herramientas" }
              : t.tools_status === "needs_tools" ? { cls: "bg-blue-50 text-blue-700 border-blue-200", label: "📦 Necesita herramientas" }
              : t.tools_status === "depends_on_job" ? { cls: "bg-slate-50 text-slate-600 border-slate-200", label: "🤔 Depende del trabajo" }
              : null;
            return (
              <div key={t.id} className="mb-3 last:mb-0">
                {t.can_cover && t.can_cover.length > 0 && (
                  <div className="mb-1">
                    <span className="text-sm font-medium text-emerald-700">Puede cubrir: </span>
                    <span className="text-sm text-slate-600">{t.can_cover.join(", ")}</span>
                  </div>
                )}
                {t.cannot_cover && t.cannot_cover.length > 0 && (
                  <div>
                    <span className="text-sm font-medium text-red-700">No puede cubrir: </span>
                    <span className="text-sm text-slate-600">{t.cannot_cover.join(", ")}</span>
                  </div>
                )}
                {toolsBadge && (
                  <div className="mt-2">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${toolsBadge.cls}`}>{toolsBadge.label}</span>
                    {t.tools_notes && <p className="text-xs text-slate-500 mt-1">{t.tools_notes}</p>}
                  </div>
                )}
              </div>
            );
          })}
        </Card>
      )}
    </div>
  );
}
