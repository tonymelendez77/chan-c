import api from "./api";

// Dashboard
export const fetchDashboardStats = () => api.get("/api/dashboard/stats").then((r) => r.data);
export const fetchPendingMatches = () => api.get("/api/matches/pending").then((r) => r.data);

// Matches
export const fetchMatches = (params?: string) => api.get(`/api/matches${params ? `?${params}` : ""}`).then((r) => r.data);
export const fetchMatch = (id: string) => api.get(`/api/matches/${id}`).then((r) => r.data);
export const updateMatchStatus = (id: string, body: Record<string, unknown>) => api.patch(`/api/matches/${id}/status`, body).then((r) => r.data);
export const sendJobOffer = (matchId: string) => api.post("/api/sms/send-offer", { match_id: matchId }).then((r) => r.data);

// AI Pipeline
export const triggerAICalls = () => api.post("/api/ai/trigger-calls").then((r) => r.data);
export const processCompletedCalls = () => api.post("/api/ai/process-completed").then((r) => r.data);
export const fetchAICalls = (params?: string) => api.get(`/api/ai/calls${params ? `?${params}` : ""}`).then((r) => r.data);
export const fetchAICall = (id: string) => api.get(`/api/ai/calls/${id}`).then((r) => r.data);
export const reviewExtraction = (callId: string, corrections: Record<string, unknown>) => api.patch(`/api/ai/calls/${callId}/review`, corrections).then((r) => r.data);

// Workers
export const fetchWorkers = (params?: string) => api.get(`/api/workers${params ? `?${params}` : ""}`).then((r) => r.data);
export const fetchWorker = (id: string) => api.get(`/api/workers/${id}`).then((r) => r.data);
export const approveWorker = (id: string) => api.post(`/api/recruitment/${id}/approve`).then((r) => r.data);
export const rejectWorker = (id: string) => api.post(`/api/recruitment/${id}/reject`).then((r) => r.data);
export const sendTestSMS = (phone: string, message: string) => api.post("/api/sms/send-test", { phone, message }).then((r) => r.data);

// Companies
export const fetchCompanies = () => api.get("/api/companies").then((r) => r.data);
export const fetchCompany = (id: string) => api.get(`/api/companies/${id}`).then((r) => r.data);

// Recruitment
export const fetchRecruitmentPipeline = () => api.get("/api/recruitment/pipeline").then((r) => r.data);
export const fetchPendingWorkers = () => api.get("/api/recruitment/pending").then((r) => r.data);
export const fetchRecruitmentDetail = (id: string) => api.get(`/api/recruitment/${id}`).then((r) => r.data);
export const triggerIntakeCalls = () => api.post("/api/recruitment/trigger-intake-calls").then((r) => r.data);
export const triggerReferenceCalls = () => api.post("/api/recruitment/trigger-reference-calls").then((r) => r.data);

// Jobs
export const fetchJobs = (params?: string) => api.get(`/api/jobs${params ? `?${params}` : ""}`).then((r) => r.data);
export const fetchJob = (id: string) => api.get(`/api/jobs/${id}`).then((r) => r.data);
export const updateJobStatus = (id: string, status: string) => api.patch(`/api/jobs/${id}/status`, { status }).then((r) => r.data);
