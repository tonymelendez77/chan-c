"use client";

import { useEffect, useState } from "react";
import { use } from "react";
import Link from "next/link";
import Card from "@/components/ui/Card";
import { JobStatusBadge } from "@/components/ui/Badge";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import MatchCard from "@/components/matches/MatchCard";
import EmptyState from "@/components/ui/EmptyState";
import { MapPin, Calendar, DollarSign, Users, ArrowLeft } from "lucide-react";
import api from "@/lib/api";
import { TRADE_LABELS, SKILL_LABELS, type Job, type Match, type JobStatus } from "@/lib/types";
import { formatDate, formatCurrency } from "@/lib/utils";

const STATUS_LABELS: Record<JobStatus, string> = {
  draft: "Borrador", open: "Abierto", matching: "Buscando match",
  filled: "Asignado", completed: "Completado", cancelled: "Cancelado",
};

export default function JobDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [job, setJob] = useState<Job | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [jobRes, matchesRes] = await Promise.all([
          api.get(`/api/jobs/${id}`),
          api.get(`/api/matches?job_id=${id}`),
        ]);
        setJob(jobRes.data);
        setMatches(matchesRes.data);
      } catch { /* handled */ }
      finally { setLoading(false); }
    }
    load();
  }, [id]);

  if (loading) return <LoadingSpinner />;
  if (!job) return <EmptyState title="Trabajo no encontrado" description="Este trabajo no existe o fue eliminado." />;

  return (
    <div className="space-y-6">
      <Link href="/jobs" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700">
        <ArrowLeft className="h-4 w-4" /> Volver a trabajos
      </Link>

      <Card>
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">{job.title}</h1>
            <p className="text-slate-500 mt-1">{TRADE_LABELS[job.trade_required]} · {SKILL_LABELS[job.skill_level_required]}</p>
          </div>
          <JobStatusBadge status={job.status} label={STATUS_LABELS[job.status]} />
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-4 border-t border-slate-100">
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <MapPin className="h-4 w-4 text-slate-400" />
            <span>Zona {job.zone}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <Calendar className="h-4 w-4 text-slate-400" />
            <span>{formatDate(job.start_date)} — {formatDate(job.end_date)}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <DollarSign className="h-4 w-4 text-slate-400" />
            <span>{formatCurrency(job.daily_rate)}/día</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <Users className="h-4 w-4 text-slate-400" />
            <span>{job.headcount} trabajador{job.headcount > 1 ? "es" : ""}</span>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-100">
          <h3 className="text-sm font-medium text-slate-700 mb-2">Descripción</h3>
          <p className="text-sm text-slate-600 whitespace-pre-line">{job.description}</p>
        </div>

        {job.special_requirements && (
          <div className="pt-4 border-t border-slate-100">
            <h3 className="text-sm font-medium text-slate-700 mb-2">Requisitos especiales</h3>
            <p className="text-sm text-slate-600">{job.special_requirements}</p>
          </div>
        )}
      </Card>

      {/* Matches */}
      <div>
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Matches ({matches.length})</h2>
        {matches.length > 0 ? (
          <div className="space-y-3">
            {matches.map((m) => <MatchCard key={m.id} match={m} />)}
          </div>
        ) : (
          <EmptyState
            title="Aún no hay matches"
            description="Nuestro equipo está buscando al trabajador ideal para este proyecto."
          />
        )}
      </div>
    </div>
  );
}
