import Link from "next/link";
import Card from "@/components/ui/Card";
import { JobStatusBadge } from "@/components/ui/Badge";
import { MapPin, Calendar, Users } from "lucide-react";
import { TRADE_LABELS, type Job, type JobStatus } from "@/lib/types";
import { formatDate, formatCurrency } from "@/lib/utils";

const STATUS_LABELS: Record<JobStatus, string> = {
  draft: "Borrador", open: "Abierto", matching: "Buscando match",
  filled: "Asignado", completed: "Completado", cancelled: "Cancelado",
};

export default function JobCard({ job }: { job: Job }) {
  return (
    <Link href={`/jobs/${job.id}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="font-semibold text-slate-900">{job.title}</h3>
            <p className="text-sm text-slate-500">{TRADE_LABELS[job.trade_required]}</p>
          </div>
          <JobStatusBadge status={job.status} label={STATUS_LABELS[job.status]} />
        </div>
        <div className="flex flex-wrap gap-4 text-sm text-slate-600">
          <span className="flex items-center gap-1">
            <MapPin className="h-3.5 w-3.5" /> Zona {job.zone}
          </span>
          <span className="flex items-center gap-1">
            <Calendar className="h-3.5 w-3.5" /> {formatDate(job.start_date)}
          </span>
          <span>{formatCurrency(job.daily_rate)}/día</span>
          {job.match_count !== undefined && (
            <span className="flex items-center gap-1">
              <Users className="h-3.5 w-3.5" /> {job.match_count} match{job.match_count !== 1 ? "es" : ""}
            </span>
          )}
        </div>
      </Card>
    </Link>
  );
}
