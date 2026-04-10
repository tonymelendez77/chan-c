import { cn } from "@/lib/utils";
import type { JobStatus, MatchStatus } from "@/lib/types";

type BadgeVariant = "blue" | "amber" | "green" | "gray" | "red" | "purple";

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

const variantStyles: Record<BadgeVariant, string> = {
  blue: "bg-blue-50 text-blue-700 border-blue-200",
  amber: "bg-amber-50 text-amber-700 border-amber-200",
  green: "bg-emerald-50 text-emerald-700 border-emerald-200",
  gray: "bg-slate-50 text-slate-600 border-slate-200",
  red: "bg-red-50 text-red-700 border-red-200",
  purple: "bg-purple-50 text-purple-700 border-purple-200",
};

export default function Badge({ children, variant = "gray", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border",
        variantStyles[variant],
        className
      )}
    >
      {children}
    </span>
  );
}

const JOB_STATUS_VARIANT: Record<JobStatus, BadgeVariant> = {
  draft: "gray",
  open: "blue",
  matching: "amber",
  filled: "green",
  completed: "gray",
  cancelled: "red",
};

const MATCH_STATUS_VARIANT: Record<MatchStatus, BadgeVariant> = {
  pending_company: "amber",
  pending_worker: "blue",
  pending_ai_call: "purple",
  call_in_progress: "purple",
  pending_review: "amber",
  pending_company_decision: "amber",
  accepted: "green",
  rejected_company: "red",
  rejected_worker: "red",
  cancelled: "gray",
};

export function JobStatusBadge({ status, label }: { status: JobStatus; label: string }) {
  return <Badge variant={JOB_STATUS_VARIANT[status]}>{label}</Badge>;
}

export function MatchStatusBadge({ status, label }: { status: MatchStatus; label: string }) {
  return <Badge variant={MATCH_STATUS_VARIANT[status]}>{label}</Badge>;
}
