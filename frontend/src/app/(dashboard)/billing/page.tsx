import Card from "@/components/ui/Card";
import EmptyState from "@/components/ui/EmptyState";

export default function BillingPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Facturación</h1>
      <Card>
        <EmptyState
          title="Facturación próximamente"
          description="Esta sección estará disponible pronto. Por ahora, contacta a nuestro equipo para consultas de facturación."
        />
      </Card>
    </div>
  );
}
