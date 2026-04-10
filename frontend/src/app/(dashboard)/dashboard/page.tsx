"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import EmptyState from "@/components/ui/EmptyState";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import JobCard from "@/components/jobs/JobCard";
import MatchCard from "@/components/matches/MatchCard";
import { Briefcase, Users, CheckCircle, Star, AlertTriangle } from "lucide-react";
import api from "@/lib/api";
import type { DashboardStats, Job, Match } from "@/lib/types";

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [statsRes, jobsRes, matchesRes] = await Promise.all([
          api.get("/api/dashboard/stats"),
          api.get("/api/jobs?status=open"),
          api.get("/api/matches"),
        ]);
        setStats(statsRes.data);
        setJobs(jobsRes.data.slice(0, 3));
        setMatches(matchesRes.data.slice(0, 5));
      } catch {
        // Token invalid — redirect handled by interceptor
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <LoadingSpinner message="Cargando panel..." />;

  const pendingDecisions = matches.filter(
    (m) => m.status === "pending_company_decision"
  ).length;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Panel de control</h1>
        <Link href="/jobs/new">
          <Button>Publicar nuevo trabajo</Button>
        </Link>
      </div>

      {pendingDecisions > 0 && (
        <div className="flex items-center gap-3 bg-amber-50 border border-amber-200 rounded-lg px-4 py-3">
          <AlertTriangle className="h-5 w-5 text-amber-600 shrink-0" />
          <p className="text-sm text-amber-800">
            Tienes <strong>{pendingDecisions}</strong> decisión{pendingDecisions > 1 ? "es" : ""} pendiente{pendingDecisions > 1 ? "s" : ""}.{" "}
            <Link href="/matches" className="underline font-medium">Ver matches</Link>
          </p>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Trabajos activos", value: stats?.open_jobs ?? 0, icon: Briefcase, color: "text-blue-600 bg-blue-100" },
          { label: "Matches pendientes", value: stats?.pending_matches ?? 0, icon: Users, color: "text-amber-600 bg-amber-100" },
          { label: "Completados este mes", value: stats?.completed_jobs_this_month ?? 0, icon: CheckCircle, color: "text-emerald-600 bg-emerald-100" },
          { label: "Trabajadores calificados", value: stats?.vetted_workers ?? 0, icon: Star, color: "text-purple-600 bg-purple-100" },
        ].map((stat) => (
          <Card key={stat.label}>
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${stat.color}`}>
                <stat.icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{stat.value}</p>
                <p className="text-xs text-slate-500">{stat.label}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Recent matches */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-900">Matches recientes</h2>
          <Link href="/matches" className="text-sm text-amber-600 hover:text-amber-700 font-medium">
            Ver todos
          </Link>
        </div>
        {matches.length > 0 ? (
          <div className="space-y-3">
            {matches.map((m) => <MatchCard key={m.id} match={m} />)}
          </div>
        ) : (
          <EmptyState
            title="Aún no tienes matches"
            description="Publica un trabajo y nuestro equipo encontrará al trabajador ideal."
            actionLabel="Publicar trabajo"
            onAction={() => router.push("/jobs/new")}
          />
        )}
      </div>

      {/* Recent jobs */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-900">Trabajos recientes</h2>
          <Link href="/jobs" className="text-sm text-amber-600 hover:text-amber-700 font-medium">
            Ver todos
          </Link>
        </div>
        {jobs.length > 0 ? (
          <div className="space-y-3">
            {jobs.map((j) => <JobCard key={j.id} job={j} />)}
          </div>
        ) : (
          <EmptyState
            title="Aún no has publicado trabajos"
            description="Publica tu primer trabajo para empezar a recibir matches."
            actionLabel="Publicar trabajo"
            onAction={() => router.push("/jobs/new")}
          />
        )}
      </div>
    </div>
  );
}
