import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    company = "company"
    worker = "worker"


class CompanyType(str, enum.Enum):
    construction = "construction"
    architecture = "architecture"
    property_management = "property_management"
    other = "other"


class SubscriptionPlan(str, enum.Enum):
    none = "none"
    basic = "basic"
    pro = "pro"


class Language(str, enum.Enum):
    spanish = "spanish"
    kiche = "kiche"
    mam = "mam"
    other = "other"


class ProfileStatus(str, enum.Enum):
    pending_review = "pending_review"
    active = "active"
    suspended = "suspended"


class Trade(str, enum.Enum):
    electrician = "electrician"
    plumber = "plumber"
    carpenter = "carpenter"
    mason = "mason"
    painter = "painter"
    welder = "welder"
    roofer = "roofer"
    general_labor = "general_labor"
    security = "security"
    housemaid = "housemaid"
    gardener = "gardener"
    other = "other"


class SkillLevel(str, enum.Enum):
    junior = "junior"
    mid = "mid"
    senior = "senior"


class SkillLevelRequired(str, enum.Enum):
    junior = "junior"
    mid = "mid"
    senior = "senior"
    any = "any"


class ReferenceOutcome(str, enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class ReferenceCallStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    no_answer = "no_answer"
    failed = "failed"


class JobStatus(str, enum.Enum):
    draft = "draft"
    open = "open"
    matching = "matching"
    filled = "filled"
    completed = "completed"
    cancelled = "cancelled"


class MatchStatus(str, enum.Enum):
    pending_company = "pending_company"
    pending_worker = "pending_worker"
    pending_ai_call = "pending_ai_call"
    call_in_progress = "call_in_progress"
    pending_review = "pending_review"
    pending_company_decision = "pending_company_decision"
    accepted = "accepted"
    rejected_company = "rejected_company"
    rejected_worker = "rejected_worker"
    cancelled = "cancelled"


class WorkerReply(str, enum.Enum):
    yes = "yes"
    no = "no"
    contra = "contra"
    problema = "problema"


class CounterofferProposedBy(str, enum.Enum):
    worker = "worker"
    company = "company"


class CounterofferStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class AICallType(str, enum.Enum):
    intake = "intake"
    reference_check = "reference_check"
    job_offer = "job_offer"
    counteroffer = "counteroffer"
    post_job_rating = "post_job_rating"


class AICallStatus(str, enum.Enum):
    initiated = "initiated"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"
    no_answer = "no_answer"


class ExtractionFinalStatus(str, enum.Enum):
    interested = "interested"
    not_interested = "not_interested"
    interested_with_conditions = "interested_with_conditions"


class OnboardingCallType(str, enum.Enum):
    intake = "intake"
    reference_check = "reference_check"


class SMSDirection(str, enum.Enum):
    inbound = "inbound"
    outbound = "outbound"


class SMSStatus(str, enum.Enum):
    sent = "sent"
    delivered = "delivered"
    failed = "failed"
    received = "received"


class RatedBy(str, enum.Enum):
    company = "company"
    worker = "worker"


class PaymentType(str, enum.Enum):
    # Legacy values kept to avoid DB enum migration; new records use commission
    placement_fee = "placement_fee"
    subscription = "subscription"
    commission = "commission"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    invoiced = "invoiced"
    paid = "paid"
    overdue = "overdue"
