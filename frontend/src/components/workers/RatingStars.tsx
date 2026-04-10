import { Star } from "lucide-react";

export default function RatingStars({ rating }: { rating: number }) {
  const stars = Math.round(rating * 5);
  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((i) => (
        <Star
          key={i}
          className={`h-4 w-4 ${i <= stars ? "fill-amber-400 text-amber-400" : "text-slate-200"}`}
        />
      ))}
      <span className="text-xs text-slate-500 ml-1">({rating.toFixed(1)})</span>
    </div>
  );
}
