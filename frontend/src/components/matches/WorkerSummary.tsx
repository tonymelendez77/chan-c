import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { CheckCircle, XCircle, Calendar } from "lucide-react";

interface WorkerSummaryProps {
  workerName: string;
  canCover?: string[];
  cannotCover?: string[];
  availability?: string;
  onAccept: () => void;
  onReject: () => void;
  onRequestOther: () => void;
  loading?: boolean;
}

export default function WorkerSummary({
  workerName, canCover = [], cannotCover = [],
  availability, onAccept, onReject, onRequestOther, loading,
}: WorkerSummaryProps) {
  return (
    <Card className="border-amber-200 bg-amber-50/30">
      <h4 className="font-semibold text-slate-900 mb-4">
        {workerName} está interesado en su proyecto
      </h4>

      {canCover.length > 0 && (
        <div className="mb-3">
          <p className="text-sm font-medium text-emerald-700 flex items-center gap-1 mb-1">
            <CheckCircle className="h-4 w-4" /> Puede cubrir:
          </p>
          <ul className="ml-6 space-y-0.5">
            {canCover.map((item, i) => (
              <li key={i} className="text-sm text-slate-700">• {item}</li>
            ))}
          </ul>
        </div>
      )}

      {cannotCover.length > 0 && (
        <div className="mb-3">
          <p className="text-sm font-medium text-red-700 flex items-center gap-1 mb-1">
            <XCircle className="h-4 w-4" /> No puede cubrir:
          </p>
          <ul className="ml-6 space-y-0.5">
            {cannotCover.map((item, i) => (
              <li key={i} className="text-sm text-slate-700">• {item}</li>
            ))}
          </ul>
        </div>
      )}

      {availability && (
        <div className="mb-4">
          <p className="text-sm font-medium text-slate-700 flex items-center gap-1 mb-1">
            <Calendar className="h-4 w-4" /> Disponibilidad:
          </p>
          <p className="text-sm text-slate-600 ml-5">{availability}</p>
        </div>
      )}

      <div className="flex flex-wrap gap-2 pt-2 border-t border-amber-200">
        <Button onClick={onAccept} loading={loading}>Aceptar trabajador</Button>
        <Button variant="ghost" onClick={onRequestOther}>Solicitar otro</Button>
        <Button variant="danger" size="sm" onClick={onReject}>Rechazar</Button>
      </div>
    </Card>
  );
}
