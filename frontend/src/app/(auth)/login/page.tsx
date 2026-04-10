"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Header from "@/components/layout/Header";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import api from "@/lib/api";
import { saveToken } from "@/lib/auth";
import type { TokenResponse } from "@/lib/types";

const schema = z.object({
  email: z.string().email("Email inválido"),
  password: z.string().min(1, "Requerido"),
});

type LoginForm = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: LoginForm) => {
    setError("");
    setLoading(true);
    try {
      const res = await api.post<TokenResponse>("/api/auth/login", data);
      saveToken(res.data.access_token);
      router.push("/dashboard");
    } catch {
      setError("Email o contraseña incorrectos");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Header />
      <div className="flex-1 flex items-center justify-center py-12 px-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-slate-900">Iniciar sesión</h1>
            <p className="text-sm text-slate-500 mt-1">Accede al panel de tu empresa</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-slate-100 p-6">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <Input
                label="Correo electrónico"
                type="email"
                placeholder="tu@empresa.gt"
                error={errors.email?.message}
                {...register("email")}
              />
              <Input
                label="Contraseña"
                type="password"
                placeholder="••••••••"
                error={errors.password?.message}
                {...register("password")}
              />

              {error && (
                <div className="bg-red-50 text-red-700 text-sm px-3 py-2 rounded-lg">
                  {error}
                </div>
              )}

              <Button type="submit" loading={loading} className="w-full">
                Entrar
              </Button>
            </form>

            <p className="text-sm text-center text-slate-500 mt-4">
              ¿No tienes cuenta?{" "}
              <Link href="/register" className="text-amber-600 hover:text-amber-700 font-medium">
                Registrarse
              </Link>
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
