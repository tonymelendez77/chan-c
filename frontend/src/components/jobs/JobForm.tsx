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
  tools_provided: z.boolean().optional(),
  tools_notes: z.string().optional(),
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
    defaultValues: { headcount: "1", tools_provided: false },
  });

  // Live commission preview
  const watched = useWatch({ control });
  const toolsProvided = !!watched.tools_provided;
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
          placeholder="Certificaciones, uniforme, documentación..."
          {...register("special_requirements")}
        />
      </div>

      {/* Tools section */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">Herramientas y equipo</label>
        <div className={`rounded-lg p-4 border ${toolsProvided ? "bg-emerald-50 border-emerald-200" : "bg-slate-50 border-slate-200"}`}>
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-900">
                {toolsProvided ? "✅ La empresa provee las herramientas" : "📦 El trabajador debe traer sus herramientas"}
              </p>
              <p className="text-xs text-slate-500 mt-0.5">
                {toolsProvided ? "Indicaremos al trabajador que no necesita traer nada" : "Asegúrate de contratar trabajadores con sus propias herramientas"}
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer ml-4">
              <input type="checkbox" className="sr-only peer" {...register("tools_provided")} />
              <div className="w-11 h-6 bg-slate-300 peer-checked:bg-emerald-500 rounded-full peer-focus:ring-2 peer-focus:ring-emerald-300 transition-colors after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-transform peer-checked:after:translate-x-5" />
            </label>
          </div>

          {toolsProvided ? (
            <div className="mt-3">
              <label className="block text-xs font-medium text-slate-600 mb-1">¿Qué herramientas proveerá la empresa?</label>
              <textarea
                rows={2}
                placeholder="Ej: Casco, arnés, taladro industrial, sierra circular"
                className="w-full rounded-lg border border-emerald-200 bg-white px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none resize-none"
                {...register("tools_notes")}
              />
            </div>
          ) : (
            <div className="mt-3 rounded bg-amber-50 border border-amber-200 px-3 py-2">
              <p className="text-xs text-amber-700">💡 Solo se mostrarán trabajadores que tengan sus propias herramientas o que indiquen que pueden trabajar sin ellas.</p>
            </div>
          )}
        </div>
      </div>

      <div className="flex justify-end">
        <Button type="submit" loading={loading} size="lg">
          Publicar trabajo
        </Button>
      </div>
    </form>
  );
}
