"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Header from "@/components/layout/Header";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";
import Button from "@/components/ui/Button";
import { CheckCircle } from "lucide-react";

const schema = z.object({
  name: z.string().min(1, "Requerido"),
  contact_name: z.string().min(1, "Requerido"),
  email: z.string().email("Email inválido"),
  password: z.string().min(8, "Mínimo 8 caracteres"),
  password_confirm: z.string(),
  phone: z.string().regex(/^\d{8}$/, "Debe ser 8 dígitos"),
  company_type: z.string().min(1, "Selecciona un tipo"),
  tax_id: z.string().optional(),
  zone: z.string().min(1, "Requerido"),
  terms: z.literal(true, { error: "Debes aceptar los términos" }),
}).refine((d) => d.password === d.password_confirm, {
  message: "Las contraseñas no coinciden",
  path: ["password_confirm"],
});

type RegisterForm = z.infer<typeof schema>;

const COMPANY_TYPES = [
  { value: "construction", label: "Construcción" },
  { value: "architecture", label: "Arquitectura" },
  { value: "property_management", label: "Administración de propiedades" },
  { value: "other", label: "Otro" },
];

export default function RegisterPage() {
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm<RegisterForm>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async () => {
    setLoading(true);
    // Simulate API call — company registration needs admin approval
    await new Promise((r) => setTimeout(r, 1000));
    setSubmitted(true);
    setLoading(false);
  };

  if (submitted) {
    return (
      <>
        <Header />
        <div className="flex-1 flex items-center justify-center py-12 px-4">
          <div className="text-center max-w-md">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 mb-6">
              <CheckCircle className="h-8 w-8" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-3">Solicitud recibida</h2>
            <p className="text-slate-600 mb-6">
              Nuestro equipo revisará tu cuenta en las próximas 24 horas.
              Te notificaremos por email.
            </p>
            <Link
              href="/login"
              className="text-amber-600 hover:text-amber-700 font-medium"
            >
              Ir a iniciar sesión
            </Link>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="flex-1 flex items-center justify-center py-12 px-4">
        <div className="w-full max-w-lg">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-slate-900">Registrar empresa</h1>
            <p className="text-sm text-slate-500 mt-1">
              Crea tu cuenta para empezar a publicar trabajos
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-slate-100 p-6">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <Input label="Nombre de la empresa" error={errors.name?.message} {...register("name")} />
              <Input label="Persona de contacto" error={errors.contact_name?.message} {...register("contact_name")} />
              <Input label="Correo electrónico" type="email" error={errors.email?.message} {...register("email")} />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input label="Contraseña" type="password" error={errors.password?.message} {...register("password")} />
                <Input label="Confirmar contraseña" type="password" error={errors.password_confirm?.message} {...register("password_confirm")} />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input label="Teléfono (8 dígitos)" placeholder="55551234" error={errors.phone?.message} {...register("phone")} />
                <Select label="Tipo de empresa" options={COMPANY_TYPES} placeholder="Seleccionar..." error={errors.company_type?.message} {...register("company_type")} />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input label="NIT (opcional)" placeholder="123456-7" {...register("tax_id")} />
                <Input label="Zona en Guatemala" placeholder="Ej: 10" error={errors.zone?.message} {...register("zone")} />
              </div>

              <div className="flex items-start gap-2">
                <input type="checkbox" id="terms" className="mt-1 rounded border-slate-300 text-amber-500 focus:ring-amber-500" {...register("terms")} />
                <label htmlFor="terms" className="text-sm text-slate-600">
                  Acepto los términos y condiciones de CHAN-C
                </label>
              </div>
              {errors.terms && <p className="text-sm text-red-600">{errors.terms.message}</p>}

              <Button type="submit" loading={loading} className="w-full">
                Registrar empresa
              </Button>
            </form>

            <p className="text-sm text-center text-slate-500 mt-4">
              ¿Ya tienes cuenta?{" "}
              <Link href="/login" className="text-amber-600 hover:text-amber-700 font-medium">
                Iniciar sesión
              </Link>
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
