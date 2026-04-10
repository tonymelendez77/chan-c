import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { formatCurrency } from "@/lib/utils";
import { DollarSign, Calendar, FileText } from "lucide-react";

interface CounterOfferCardProps {
  workerName: string;
  proposedRate?: number;
  originalRate: number;
  proposedDates?: string;
  conditions?: string;
  onAccept: () => void;
  onReject: () => void;
  loading?: boolean;
}

export default function CounterOfferCard({
  workerName, proposedRate, originalRate,
  proposedDates, conditions, onAccept, onReject, loading,
}: CounterOfferCardProps) {
  return (
    <Card className="border-purple-200 bg-purple-50/30">
      <h4 className="font-semibold text-slate-900 mb-4">
        {workerName} propone una contrapropuesta
      </h4>

      {proposedRate && (
        <div className="mb-3 flex items-start gap-2">
          <DollarSign className="h-4 w-4 text-purple-600 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-slate-900">
              Precio: {formatCurrency(proposedRate)}/día
            </p>
            <p className="text-xs text-slate-500">
              (ofreciste {formatCurrency(originalRate)}/día)
            </p>
          </div>
        </div>
      )}

      {proposedDates && (
        <div className="mb-3 flex items-start gap-2">
          <Calendar className="h-4 w-4 text-purple-600 mt-0.5" />
          <p className="text-sm text-slate-700">Fechas: {proposedDates}</p>
        </div>
      )}

      {conditions && (
        <div className="mb-4 flex items-start gap-2">
          <FileText className="h-4 w-4 text-purple-600 mt-0.5" />
          <p className="text-sm text-slate-700">Condiciones: {conditions}</p>
        </div>
      )}

      <div className="flex gap-2 pt-2 border-t border-purple-200">
        <Button onClick={onAccept} loading={loading}>Aceptar propuesta</Button>
        <Button variant="danger" size="sm" onClick={onReject}>Rechazar</Button>
      </div>
    </Card>
  );
}
