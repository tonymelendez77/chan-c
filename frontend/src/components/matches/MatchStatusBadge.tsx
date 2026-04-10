import { MatchStatusBadge as BaseBadge } from "@/components/ui/Badge";
import type { MatchStatus } from "@/lib/types";

const LABELS: Record<MatchStatus, string> = {
  pending_company: "Pendiente empresa", pending_worker: "Esperando trabajador",
  pending_ai_call: "Llamada pendiente", call_in_progress: "Llamada en curso",
  pending_review: "En revisión", pending_company_decision: "Tu decisión",
  accepted: "Aceptado", rejected_company: "Rechazado",
  rejected_worker: "Declinado", cancelled: "Cancelado",
};

export default function MatchStatusBadgeWrapper({ status }: { status: MatchStatus }) {
  return <BaseBadge status={status} label={LABELS[status]} />;
}
