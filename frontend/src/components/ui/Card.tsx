import { cn } from "@/lib/utils";

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export default function Card({ children, className }: CardProps) {
  return (
    <div className={cn("bg-white rounded-lg shadow-sm border border-slate-100 p-6", className)}>
      {children}
    </div>
  );
}
