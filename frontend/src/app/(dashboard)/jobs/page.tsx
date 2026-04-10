"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Button from "@/components/ui/Button";
import EmptyState from "@/components/ui/EmptyState";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import JobCard from "@/components/jobs/JobCard";
import api from "@/lib/api";
import type { Job, JobStatus } from "@/lib/types";

const FILTERS: { value: JobStatus | "all"; label: string }[] = [
  { value: "all", label: "Todos" },
  { value: "open", label: "Abiertos" },
  { value: "matching", label: "Buscando match" },
  { value: "filled", label: "Asignados" },
  { value: "completed", label: "Completados" },
  { value: "cancelled", label: "Cancelados" },
];

export default function JobsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    async function load() {
      try {
        const params = filter !== "all" ? `?status=${filter}` : "";
        const res = await api.get(`/api/jobs${params}`);
        setJobs(res.data);
      } catch { /* handled by interceptor */ }
      finally { setLoading(false); }
    }
    load();
  }, [filter]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Mis trabajos</h1>
        <Link href="/jobs/new">
          <Button>Nuevo trabajo</Button>
        </Link>
      </div>

      <div className="flex gap-2 flex-wrap">
        {FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => { setFilter(f.value); setLoading(true); }}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              filter === f.value
                ? "bg-amber-100 text-amber-700"
                : "bg-white text-slate-600 hover:bg-slate-50 border border-slate-200"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : jobs.length > 0 ? (
        <div className="space-y-3">
          {jobs.map((j) => <JobCard key={j.id} job={j} />)}
        </div>
      ) : (
        <EmptyState
          title="No hay trabajos"
          description="Publica tu primer trabajo para empezar a recibir matches."
          actionLabel="Publicar trabajo"
          onAction={() => router.push("/jobs/new")}
        />
      )}
    </div>
  );
}
