import { JobStatusBadge as BaseBadge } from "@/components/ui/Badge";
import type { JobStatus } from "@/lib/types";

const LABELS: Record<JobStatus, string> = {
  draft: "Borrador", open: "Abierto", matching: "Buscando match",
  filled: "Asignado", completed: "Completado", cancelled: "Cancelado",
};

export default function JobStatusBadgeWrapper({ status }: { status: JobStatus }) {
  return <BaseBadge status={status} label={LABELS[status]} />;
}
