import Card from "@/components/ui/Card";
import { Star, MapPin, Briefcase } from "lucide-react";
import { TRADE_LABELS, SKILL_LABELS, type Worker } from "@/lib/types";
import TradesBadges from "./TradesBadges";
import RatingStars from "./RatingStars";

export default function WorkerProfileCard({ worker }: { worker: Worker }) {
  return (
    <Card>
      <div className="flex items-start gap-4">
        <div className="rounded-full bg-amber-100 text-amber-700 w-12 h-12 flex items-center justify-center font-bold text-lg">
          {worker.full_name.charAt(0)}
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-slate-900">{worker.full_name}</h3>
          <div className="flex items-center gap-3 text-sm text-slate-500 mt-1">
            <span className="flex items-center gap-1">
              <MapPin className="h-3.5 w-3.5" /> Zona {worker.zone}
            </span>
            <span className="flex items-center gap-1">
              <Briefcase className="h-3.5 w-3.5" /> {worker.total_jobs} trabajos
            </span>
          </div>
          <div className="mt-2">
            <RatingStars rating={worker.rating_avg} />
          </div>
          {worker.trades && worker.trades.length > 0 && (
            <div className="mt-3">
              <TradesBadges trades={worker.trades} />
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
