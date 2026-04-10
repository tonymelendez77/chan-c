"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Card from "@/components/ui/Card";
import JobForm, { type JobFormData } from "@/components/jobs/JobForm";
import api from "@/lib/api";
import { getCurrentUser } from "@/lib/auth";

export default function NewJobPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (data: JobFormData) => {
    setLoading(true);
    try {
      const user = getCurrentUser();
      await api.post("/api/jobs", {
        ...data,
        daily_rate: Number(data.daily_rate),
        headcount: Number(data.headcount),
        company_id: user?.user_id,
        created_by: user?.user_id,
        status: "open",
      });
      router.push("/jobs");
    } catch {
      alert("Error al publicar trabajo");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Publicar nuevo trabajo</h1>
      <Card>
        <JobForm onSubmit={handleSubmit} loading={loading} />
      </Card>
    </div>
  );
}
