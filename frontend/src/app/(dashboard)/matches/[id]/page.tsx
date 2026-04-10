"use client";

import { useEffect, useState } from "react";
import { use } from "react";
import Link from "next/link";
import Card from "@/components/ui/Card";
import { MatchStatusBadge } from "@/components/ui/Badge";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import EmptyState from "@/components/ui/EmptyState";
import WorkerSummary from "@/components/matches/WorkerSummary";
import CounterOfferCard from "@/components/matches/CounterOfferCard";
import { ArrowLeft } from "lucide-react";
import api from "@/lib/api";
import type { Match, MatchStatus } from "@/lib/types";
import { formatCurrency, formatDate } from "@/lib/utils";

const STATUS_LABELS: Record<MatchStatus, string> = {
  pending_company: "Pendiente empresa", pending_worker: "Esperando trabajador",
  pending_ai_call: "Llamada pendiente", call_in_progress: "Llamada en curso",
  pending_review: "En revisión", pending_company_decision: "Tu decisión",
  accepted: "Aceptado", rejected_company: "Rechazado",
  rejected_worker: "Declinado", cancelled: "Cancelado",
};

export default function MatchDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [match, setMatch] = useState<Match | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get(`/api/matches/${id}`);
        setMatch(res.data);
      } catch { /* handled */ }
      finally { setLoading(false); }
    }
    load();
  }, [id]);

  const updateStatus = async (status: string) => {
    setActionLoading(true);
    try {
      const res = await api.patch(`/api/matches/${id}/status`, { status });
      setMatch(res.data);
    } catch { alert("Error al actualizar"); }
    finally { setActionLoading(false); }
  };

  if (loading) return <LoadingSpinner />;
  if (!match) return <EmptyState title="Match no encontrado" description="Este match no existe." />;

  return (
    <div className="space-y-6 max-w-3xl">
      <Link href="/matches" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700">
        <ArrowLeft className="h-4 w-4" /> Volver a matches
      </Link>

      <Card>
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900">
              {match.worker_name || "Trabajador"}
            </h1>
            <p className="text-slate-500">{match.job_title || "Trabajo"}</p>
          </div>
          <MatchStatusBadge status={match.status} label={STATUS_LABELS[match.status]} />
        </div>

        <div className="grid grid-cols-2 gap-4 py-4 border-t border-slate-100 text-sm">
          <div>
            <span className="text-slate-500">Oferta:</span>{" "}
            <span className="font-medium">{formatCurrency(match.offered_rate)}/día</span>
          </div>
          {match.final_rate && (
            <div>
              <span className="text-slate-500">Tarifa final:</span>{" "}
              <span className="font-medium">{formatCurrency(match.final_rate)}/día</span>
            </div>
          )}
          <div>
            <span className="text-slate-500">Creado:</span>{" "}
            <span>{formatDate(match.created_at)}</span>
          </div>
          {match.worker_replied_at && (
            <div>
              <span className="text-slate-500">Respuesta:</span>{" "}
              <span>{formatDate(match.worker_replied_at)}</span>
            </div>
          )}
        </div>
      </Card>

      {/* Pending company decision with AI summary */}
      {match.status === "pending_company_decision" && (
        <WorkerSummary
          workerName={match.worker_name || "Trabajador"}
          canCover={["Instalación residencial", "Cableado básico"]}
          cannotCover={["Instalaciones trifásicas"]}
          availability="Lunes a viernes, 7am-5pm"
          onAccept={() => updateStatus("accepted")}
          onReject={() => updateStatus("rejected_company")}
          onRequestOther={() => updateStatus("cancelled")}
          loading={actionLoading}
        />
      )}

      {/* Counteroffer pending */}
      {match.worker_reply === "contra" && match.status === "pending_company_decision" && (
        <CounterOfferCard
          workerName={match.worker_name || "Trabajador"}
          proposedRate={400}
          originalRate={match.offered_rate}
          proposedDates="Miércoles a viernes"
          conditions="Necesita equipo de seguridad proporcionado"
          onAccept={() => updateStatus("accepted")}
          onReject={() => updateStatus("rejected_company")}
          loading={actionLoading}
        />
      )}
    </div>
  );
}
