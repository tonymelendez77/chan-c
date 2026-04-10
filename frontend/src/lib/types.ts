// Enums matching backend
export type UserRole = "admin" | "company" | "worker";
export type CompanyType = "construction" | "architecture" | "property_management" | "other";
export type SubscriptionPlan = "none" | "basic" | "pro";
export type Language = "spanish" | "kiche" | "mam" | "other";
export type ProfileStatus = "pending_review" | "active" | "suspended";
export type Trade =
  | "electrician" | "plumber" | "carpenter" | "mason" | "painter"
  | "welder" | "roofer" | "general_labor" | "security" | "housemaid"
  | "gardener" | "other";
export type SkillLevel = "junior" | "mid" | "senior";
export type SkillLevelRequired = "junior" | "mid" | "senior" | "any";
export type JobStatus = "draft" | "open" | "matching" | "filled" | "completed" | "cancelled";
export type MatchStatus =
  | "pending_company" | "pending_worker" | "pending_ai_call"
  | "call_in_progress" | "pending_review" | "pending_company_decision"
  | "accepted" | "rejected_company" | "rejected_worker" | "cancelled";
export type WorkerReply = "yes" | "no" | "contra" | "problema";
export type ExtractionFinalStatus = "interested" | "not_interested" | "interested_with_conditions";

// Trade display names in Spanish
export const TRADE_LABELS: Record<Trade, string> = {
  electrician: "Electricista",
  plumber: "Plomero",
  carpenter: "Carpintero",
  mason: "Albañil",
  painter: "Pintor",
  welder: "Soldador",
  roofer: "Techador",
  general_labor: "Ayudante general",
  security: "Seguridad",
  housemaid: "Limpieza",
  gardener: "Jardinero",
  other: "Otro",
};

export const SKILL_LABELS: Record<SkillLevel | "any", string> = {
  junior: "Junior",
  mid: "Intermedio",
  senior: "Senior",
  any: "Cualquiera",
};

// Interfaces
export interface Company {
  id: string;
  user_id: string;
  name: string;
  contact_name: string;
  phone: string;
  email: string;
  zone: string;
  company_type: CompanyType;
  tax_id: string;
  is_verified: boolean;
  subscription_plan: SubscriptionPlan;
  created_at: string;
}

export interface Job {
  id: string;
  company_id: string;
  title: string;
  trade_required: Trade;
  skill_level_required: SkillLevelRequired;
  zone: string;
  start_date: string;
  end_date: string;
  daily_rate: number;
  currency: string;
  headcount: number;
  description: string;
  special_requirements?: string;
  status: JobStatus;
  created_by: string;
  created_at: string;
  updated_at: string;
  company_name?: string;
  match_count?: number;
}

export interface Worker {
  id: string;
  full_name: string;
  phone: string;
  zone: string;
  language: Language;
  is_available: boolean;
  is_active: boolean;
  is_vetted: boolean;
  rating_avg: number;
  total_jobs: number;
  created_at: string;
  dpi?: string;
  notes?: string;
  paused?: boolean;
  paused_until?: string;
  paused_reason?: string;
  pause_reason_code?: string;
  profile?: WorkerProfile;
  trades?: WorkerTrade[];
}

export interface WorkerProfile {
  id: string;
  worker_id: string;
  bio?: string;
  initial_score?: number;
  profile_status: ProfileStatus;
  total_earnings: number;
  response_rate: number;
  completion_rate: number;
}

export interface WorkerTrade {
  id: string;
  worker_id: string;
  trade: Trade;
  skill_level: SkillLevel;
  years_experience: number;
  can_cover?: string[];
  cannot_cover?: string[];
  verified_by_admin: boolean;
  created_at: string;
}

export interface Match {
  id: string;
  job_id: string;
  worker_id: string;
  created_by: string;
  status: MatchStatus;
  offered_rate: number;
  final_rate?: number;
  worker_reply?: WorkerReply;
  company_notified_at?: string;
  worker_sms_sent_at?: string;
  worker_replied_at?: string;
  company_decided_at?: string;
  created_at: string;
  updated_at: string;
  worker_name?: string;
  worker_phone?: string;
  job_title?: string;
  company_name?: string;
}

export interface Counteroffer {
  id: string;
  match_id: string;
  proposed_by: "worker" | "company";
  original_rate: number;
  proposed_rate?: number;
  original_start: string;
  proposed_start?: string;
  original_end: string;
  proposed_end?: string;
  notes?: string;
  status: "pending" | "accepted" | "rejected";
}

export interface AIExtraction {
  id: string;
  call_id: string;
  can_cover?: string[];
  cannot_cover?: string[];
  counteroffer_price?: number;
  counteroffer_dates?: string;
  counteroffer_notes?: string;
  availability_notes?: string;
  final_status?: ExtractionFinalStatus;
  confidence_score?: number;
  requires_admin_review: boolean;
}

export interface DashboardStats {
  active_workers: number;
  vetted_workers: number;
  open_jobs: number;
  active_matches: number;
  pending_matches: number;
  completed_jobs_this_month: number;
  total_companies: number;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  role: UserRole;
}
