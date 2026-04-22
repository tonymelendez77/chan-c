"use client";

import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";
import Button from "@/components/ui/Button";
import { TRADE_LABELS, SKILL_LABELS, type Trade, type SkillLevelRequired } from "@/lib/types";

const schema = z.object({
  title: z.string().min(1, "Requerido"),
  trade_required: z.string().min(1, "Selecciona un oficio"),
  skill_level_required: z.string().min(1, "Selecciona un nivel"),
  zone: z.string().min(1, "Requerido"),
  start_date: z.string().min(1, "Requerido"),
  end_date: z.string().min(1, "Requerido"),
  daily_rate: z.string().min(1, "Mínimo Q1"),
  headcount: z.string().min(1, "Mínimo 1"),
  description: z.string().min(10, "Mínimo 10 caracteres"),
  special_requirements: z.string().optional(),
});

export type JobFormData = z.infer<typeof schema>;

interface JobFormProps {
  onSubmit: (data: JobFormData) => void;
  loading?: boolean;
}

const tradeOptions = Object.entries(TRADE_LABELS).map(([value, label]) => ({ value, label }));
const skillOptions = Object.entries(SKILL_LABELS).map(([value, label]) => ({ value, label }));

export default function JobForm({ onSubmit, loading }: JobFormProps) {
  const { register, handleSubmit, control, formState: { errors } } = useForm<JobFormData>({
    resolver: zodResolver(schema),
    defaultValues: { headcount: "1" },
  });

  // Live commission preview
  const watched = useWatch({ control });
  const rate = Number(watched.daily_rate || 0);
  const headcount = Number(watched.headcount || 0);
  let days = 0;
  if (watched.start_date && watched.end_date) {
    const start = new Date(watched.start_date);
    const end = new Date(watched.end_date);
    if (!isNaN(start.getTime()) && !isNaN(end.getTime()) && end >= start) {
      days = Math.floor((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1;
    }
  }
  const jobValue = rate * days * headcount;
  const commission = jobValue * 0.10;
  const showPreview = rate > 0 && days > 0 && headcount > 0;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <Input label="Título del trabajo" placeholder="Ej: Electricista para obra en Zona 10" error={errors.title?.message} {...register("title")} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Select label="Oficio requerido" options={tradeOptions} placeholder="Seleccionar..." error={errors.trade_required?.message} {...register("trade_required")} />
        <Select label="Nivel de experiencia" options={skillOptions} placeholder="Seleccionar..." error={errors.skill_level_required?.message} {...register("skill_level_required")} />
      </div>

      <Input label="Zona en Ciudad de Guatemala" placeholder="Ej: 10" error={errors.zone?.message} {...register("zone")} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input label="Fecha de inicio" type="date" error={errors.start_date?.message} {...register("start_date")} />
        <Input label="Fecha de fin" type="date" error={errors.end_date?.message} {...register("end_date")} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input label="Tarifa diaria (Q)" type="number" placeholder="350" error={errors.daily_rate?.message} {...register("daily_rate")} />
        <Input label="Trabajadores necesarios" type="number" placeholder="1" error={errors.headcount?.message} {...register("headcount")} />
      </div>

      {showPreview && (
        <div className="rounded-lg bg-amber-50 border border-amber-200 p-4">
          <p className="text-sm font-semibold text-amber-900 mb-2">💰 Estimado de comisión</p>
          <p className="text-sm text-amber-800 font-mono">
            Q{rate}/día × {days} día{days !== 1 ? "s" : ""} × {headcount} trabajador{headcount !== 1 ? "es" : ""}
            {" = "}
            <span className="font-semibold">Q{jobValue.toLocaleString("es-GT")} valor del trabajo</span>
          </p>
          <p className="text-sm text-amber-900 font-mono mt-1">
            Comisión CHAN-C (10%): <span className="font-bold">Q{commission.toLocaleString("es-GT", { maximumFractionDigits: 2 })}</span>
          </p>
          <p className="text-xs text-amber-700 mt-2">Solo se cobra al confirmar el match.</p>
        </div>
      )}

      <div className="space-y-1">
        <label className="block text-sm font-medium text-slate-700">Descripción del trabajo</label>
        <textarea
          className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-500 focus:ring-1 focus:ring-amber-500 outline-none transition-colors min-h-[100px]"
          placeholder="Describe el trabajo, ubicación exacta, horarios..."
          {...register("description")}
        />
        {errors.description && <p className="text-sm text-red-600">{errors.description.message}</p>}
      </div>

      <div className="space-y-1">
        <label className="block text-sm font-medium text-slate-700">Requisitos especiales (opcional)</label>
        <textarea
          className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:border-amber-500 focus:ring-1 focus:ring-amber-500 outline-none transition-colors min-h-[80px]"
          placeholder="Herramientas, certificaciones, uniforme..."
          {...register("special_requirements")}
        />
      </div>

      <div className="flex justify-end">
        <Button type="submit" loading={loading} size="lg">
          Publicar trabajo
        </Button>
      </div>
    </form>
  );
}
