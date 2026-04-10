import Card from "@/components/ui/Card";
import EmptyState from "@/components/ui/EmptyState";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Configuración</h1>
      <Card>
        <EmptyState
          title="Configuración próximamente"
          description="Aquí podrás actualizar los datos de tu empresa, cambiar tu contraseña y gestionar notificaciones."
        />
      </Card>
    </div>
  );
}
