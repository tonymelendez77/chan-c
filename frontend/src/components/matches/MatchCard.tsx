import Link from "next/link";
import Card from "@/components/ui/Card";
import { MatchStatusBadge } from "@/components/ui/Badge";
import type { Match, MatchStatus } from "@/lib/types";
import { formatCurrency } from "@/lib/utils";

const STATUS_LABELS: Record<MatchStatus, string> = {
  pending_company: "Pendiente empresa", pending_worker: "Esperando trabajador",
  pending_ai_call: "Llamada pendiente", call_in_progress: "Llamada en curso",
  pending_review: "En revisión", pending_company_decision: "Tu decisión",
  accepted: "Aceptado", rejected_company: "Rechazado",
  rejected_worker: "Declinado", cancelled: "Cancelado",
};

export default function MatchCard({ match }: { match: Match }) {
  const needsAction = match.status === "pending_company_decision";

  return (
    <Link href={`/matches/${match.id}`}>
      <Card className={`hover:shadow-md transition-shadow cursor-pointer ${needsAction ? "ring-2 ring-amber-300" : ""}`}>
        <div className="flex items-start justify-between mb-2">
          <div>
            <h3 className="font-semibold text-slate-900">
              {match.worker_name || "Trabajador"}
            </h3>
            <p className="text-sm text-slate-500">{match.job_title || "Trabajo"}</p>
          </div>
          <MatchStatusBadge status={match.status} label={STATUS_LABELS[match.status]} />
        </div>
        <div className="flex gap-4 text-sm text-slate-600">
          <span>Oferta: {formatCurrency(match.offered_rate)}/día</span>
          {match.final_rate && <span>Final: {formatCurrency(match.final_rate)}/día</span>}
        </div>
      </Card>
    </Link>
  );
}
