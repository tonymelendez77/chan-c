import Badge from "@/components/ui/Badge";
import { TRADE_LABELS, SKILL_LABELS, type WorkerTrade } from "@/lib/types";

export default function TradesBadges({ trades }: { trades: WorkerTrade[] }) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {trades.map((t) => (
        <Badge key={t.id} variant="blue">
          {TRADE_LABELS[t.trade]} · {SKILL_LABELS[t.skill_level]} · {t.years_experience} años
        </Badge>
      ))}
    </div>
  );
}
