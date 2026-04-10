type BadgeColor = "amber" | "green" | "red" | "blue" | "purple" | "gray";

const COLORS: Record<BadgeColor, { bg: string; border: string; text: string }> = {
  amber: { bg: "var(--admin-amber-bg)", border: "var(--admin-amber-border)", text: "var(--admin-amber)" },
  green: { bg: "var(--admin-green-bg)", border: "var(--admin-green-border)", text: "var(--admin-green)" },
  red: { bg: "var(--admin-red-bg)", border: "var(--admin-red-border)", text: "var(--admin-red)" },
  blue: { bg: "var(--admin-blue-bg)", border: "var(--admin-blue-border)", text: "var(--admin-blue)" },
  purple: { bg: "var(--admin-purple-bg)", border: "var(--admin-purple-border)", text: "var(--admin-purple)" },
  gray: { bg: "#F5F5F4", border: "#D6D3D1", text: "#78716C" },
};

// Match status → color mapping
const MATCH_STATUS_COLOR: Record<string, BadgeColor> = {
  pending_company: "amber", pending_worker: "blue", pending_ai_call: "purple",
  call_in_progress: "purple", pending_review: "red", pending_company_decision: "amber",
  accepted: "green", rejected_company: "gray", rejected_worker: "gray", cancelled: "gray",
};
const MATCH_STATUS_LABEL: Record<string, string> = {
  pending_company: "Esp. empresa", pending_worker: "SMS enviado", pending_ai_call: "Llamada IA",
  call_in_progress: "En llamada", pending_review: "Revisar", pending_company_decision: "Esp. decisión",
  accepted: "Aceptado", rejected_company: "Rechazado", rejected_worker: "Declinado", cancelled: "Cancelado",
};

const CALL_STATUS_COLOR: Record<string, BadgeColor> = {
  initiated: "gray", in_progress: "purple", completed: "green", failed: "red", no_answer: "amber",
};
const CALL_STATUS_LABEL: Record<string, string> = {
  initiated: "Iniciada", in_progress: "En curso", completed: "Completada", failed: "Fallida", no_answer: "Sin respuesta",
};

const CALL_TYPE_COLOR: Record<string, BadgeColor> = {
  job_offer: "blue", counteroffer: "amber", intake: "green", reference_check: "purple", post_job_rating: "gray",
};
const CALL_TYPE_LABEL: Record<string, string> = {
  job_offer: "Oferta", counteroffer: "Contrapropuesta", intake: "Intake", reference_check: "Referencia", post_job_rating: "Rating",
};

const PAYMENT_STATUS_COLOR: Record<string, BadgeColor> = {
  pending: "amber", invoiced: "blue", paid: "green", overdue: "red",
};
const PAYMENT_STATUS_LABEL: Record<string, string> = {
  pending: "Pendiente", invoiced: "Facturada", paid: "Pagada", overdue: "Vencida",
};

interface StatusBadgeProps {
  status: string;
  type?: "match" | "call" | "callType" | "payment" | "custom";
  label?: string;
  color?: BadgeColor;
  pulse?: boolean;
}

export default function StatusBadge({ status, type = "custom", label, color, pulse }: StatusBadgeProps) {
  let c: BadgeColor = color || "gray";
  let l = label || status;

  if (type === "match") { c = MATCH_STATUS_COLOR[status] || "gray"; l = MATCH_STATUS_LABEL[status] || status; }
  if (type === "call") { c = CALL_STATUS_COLOR[status] || "gray"; l = CALL_STATUS_LABEL[status] || status; }
  if (type === "callType") { c = CALL_TYPE_COLOR[status] || "gray"; l = CALL_TYPE_LABEL[status] || status; }
  if (type === "payment") { c = PAYMENT_STATUS_COLOR[status] || "gray"; l = PAYMENT_STATUS_LABEL[status] || status; }

  const colors = COLORS[c];
  const shouldPulse = pulse || (type === "call" && status === "in_progress") || (type === "match" && status === "call_in_progress");

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full" style={{ background: colors.bg, border: `1px solid ${colors.border}`, color: colors.text, padding: "3px 10px", fontSize: 12, fontWeight: 500 }}>
      {shouldPulse && <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: colors.text }} />}
      {l}
    </span>
  );
}
