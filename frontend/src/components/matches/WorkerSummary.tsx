import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { CheckCircle, XCircle, Calendar, Wrench } from "lucide-react";

type ToolsStatus = "own_tools" | "needs_tools" | "partial_tools" | "depends_on_job" | null | undefined;

interface WorkerSummaryProps {
  workerName: string;
  canCover?: string[];
  cannotCover?: string[];
  availability?: string;
  toolsStatus?: ToolsStatus;
  toolsNotes?: string | null;
  onAccept: () => void;
  onReject: () => void;
  onRequestOther: () => void;
  loading?: boolean;
}

const TOOLS_BADGE: Record<string, { cls: string; label: string }> = {
  own_tools: { cls: "bg-emerald-50 text-emerald-700 border-emerald-200", label: "🔧 Tiene sus herramientas" },
  partial_tools: { cls: "bg-amber-50 text-amber-700 border-amber-200", label: "🔨 Tiene algunas" },
  needs_tools: { cls: "bg-blue-50 text-blue-700 border-blue-200", label: "📦 Necesita herramientas" },
  depends_on_job: { cls: "bg-slate-50 text-slate-600 border-slate-200", label: "🤔 Depende del trabajo" },
};

export default function WorkerSummary({
  workerName, canCover = [], cannotCover = [],
  availability, toolsStatus, toolsNotes,
  onAccept, onReject, onRequestOther, loading,
}: WorkerSummaryProps) {
  const toolsBadge = toolsStatus ? TOOLS_BADGE[toolsStatus] : null;
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
        <div className="mb-3">
          <p className="text-sm font-medium text-slate-700 flex items-center gap-1 mb-1">
            <Calendar className="h-4 w-4" /> Disponibilidad:
          </p>
          <p className="text-sm text-slate-600 ml-5">{availability}</p>
        </div>
      )}

      {toolsBadge && (
        <div className="mb-4">
          <p className="text-sm font-medium text-slate-700 flex items-center gap-1 mb-1">
            <Wrench className="h-4 w-4" /> Herramientas:
          </p>
          <div className="ml-5">
            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${toolsBadge.cls}`}>{toolsBadge.label}</span>
            {toolsNotes && <p className="text-xs text-slate-500 mt-1">{toolsNotes}</p>}
          </div>
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
