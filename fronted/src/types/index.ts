/* ============================================================
   领域类型（与 backend/schemas 一一对应）
   ============================================================ */

export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

export interface PageData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

/* ---------- 模块一 ---------- */
export interface JobType {
  id: number
  name: string
  color: string | null
  sort_order: number
  created_at: string
  updated_at: string
}

export interface Resume {
  id: number
  job_type_id: number | null
  job_type_name: string | null
  version_name: string
  target_position: string | null
  file_path: string | null
  file_name: string | null
  file_type: string | null
  file_size: number | null
  status: string
  is_default: boolean
  remark: string | null
  created_at: string
  updated_at: string
}

export interface ResumeDetail extends Resume {
  logs: ResumeLog[]
}

export interface ResumeLog {
  id: number
  resume_version_id: number
  change_desc: string
  changed_at: string
  trigger_source: string
}

export interface Material {
  id: number
  category: string
  title: string
  organization: string | null
  role: string | null
  start_date: string | null
  end_date: string | null
  description: string | null
  highlights: string | null
  tech_stack: string[] | null
  attachments: string[] | null
  tags: string[] | null
  created_at: string
  updated_at: string
}

export interface Asset {
  id: number
  category: string
  title: string
  url: string | null
  file_path: string | null
  description: string | null
  tags: string[] | null
  created_at: string
  updated_at: string
}

/* ---------- 模块二 ---------- */
export interface Application {
  id: number
  company: string
  position: string
  city: string | null
  salary_min: number | null
  salary_max: number | null
  salary_currency: string
  channel: string | null
  apply_time: string | null
  resume_version_id: number | null
  resume_version_name: string | null
  job_type_id: number | null
  job_type_name: string | null
  status: string
  source_url: string | null
  remark: string | null
  created_at: string
  updated_at: string
}

export interface StatusLog {
  id: number
  application_id: number
  from_status: string | null
  to_status: string
  note: string | null
  changed_at: string
}

export interface LinkedExam {
  id: number
  exam_time: string | null
  platform: string | null
  status: string
}

export interface LinkedInterview {
  id: number
  round: string | null
  interview_time: string | null
  status: string
}

export interface LinkedOffer {
  id: number
  company: string
  position: string | null
  salary_base: number | null
  status: string
}

export interface ApplicationDetail extends Application {
  timeline: StatusLog[]
  exams: LinkedExam[]
  interviews: LinkedInterview[]
  offers: LinkedOffer[]
  blacklist_hits: number
}

export interface Offer {
  id: number
  application_id: number | null
  company: string
  position: string | null
  city: string | null
  salary_base: number | null
  salary_months: number | null
  bonus_performance: number | null
  signing_bonus: number | null
  housing_fund: string | null
  stock_options: string | null
  work_intensity: number | null
  industry_prospect: number | null
  company_scale: string | null
  position_development: number | null
  other_notes: string | null
  status: string
  extra_scores: Record<string, number> | null
  created_at: string
  updated_at: string
}

export interface OfferWeight {
  id: number
  dimension_key: string
  dimension_name: string
  weight: number
  enabled: boolean
  sort_order: number
}

export interface CompareOfferResult {
  offer_id: number
  company: string
  position: string | null
  city: string | null
  scores: Record<string, number>
  total: number
  recommended: boolean
  rank: number
}

export interface OfferCompareResult {
  results: CompareOfferResult[]
  dimensions: { key: string; name: string; weight: number; enabled: boolean }[]
}

/* ---------- 模块三 ---------- */
export interface Exam {
  id: number
  application_id: number | null
  exam_time: string | null
  platform: string | null
  exam_link: string | null
  account: string | null
  password: string | null
  duration_minutes: number | null
  status: string
  created_at: string
  updated_at: string
}

export interface ExamReview {
  id: number
  exam_id: number
  passed: boolean | null
  score: string | null
  questions: string | null
  wrong_questions: string | null
  key_points: string[] | null
  summary: string | null
  created_at: string
  updated_at: string
}

export interface Interview {
  id: number
  application_id: number | null
  round: string | null
  interview_time: string | null
  interview_link: string | null
  self_intro: string | null
  prep_checklist: PrepItem[] | null
  status: string
  created_at: string
  updated_at: string
}

export interface PrepItem {
  label: string
  done: boolean
}

export interface InterviewQa {
  id: number
  interview_id: number
  question: string
  my_answer: string | null
  feedback: string | null
  category: string | null
  created_at: string
}

export interface InterviewResult {
  id: number
  interview_id: number
  result: string | null
  fail_reason: string | null
  audio_path: string | null
  summary: string | null
  created_at: string
  updated_at: string
}

export interface Question {
  id: number
  category: string | null
  title: string
  difficulty: string | null
  content: string | null
  answer: string | null
  tags: string[] | null
  source: string | null
  review_status: string
  created_at: string
  updated_at: string
}

/* ---------- 模块四 ---------- */
export interface StatsOverview {
  total_applications: number
  effective_applications: number
  resume_rejected_rate: number
  exam_pass_rate: number
  interview_rate: number
  offer_rate: number
}

export interface JobTypeStat {
  job_type: string
  total_applications: number
  effective_applications: number
  exam_count: number
  interview_count: number
  offer_count: number
  exam_rate: number
  interview_rate: number
  offer_rate: number
}

export interface TimeStat {
  granularity: string
  items: { label: string; count: number }[]
}

/* ---------- 模块五 ---------- */
export interface Script {
  id: number
  category: string
  title: string
  content: string
  tags: string[] | null
  is_favorite: boolean
  usage_count: number
  created_at: string
  updated_at: string
}

export interface BlacklistItem {
  id: number
  company: string
  position: string | null
  issue_type: string | null
  detail: string | null
  source: string | null
  created_at: string
  updated_at: string
}

export interface Task {
  id: number
  task_type: string
  ref_id: number | null
  ref_type: string | null
  title: string
  due_date: string
  done: boolean
  done_at: string | null
  created_at: string
  updated_at: string
}

export interface DashboardToday {
  date: string
  apply_todo: { id: number; company: string; position: string; city: string | null }[]
  review_todo: { type: string; id: number; title: string; application_id: number | null }[]
  question_todo: { id: number; title: string; category: string | null; difficulty: string | null }[]
  tasks: Task[]
  streak: number
  week_done: number
  week_total: number
}

export interface Streak {
  streak: number
  week_done: number
  week_total: number
}

/* ---------- 系统 ---------- */
export type SettingsMap = Record<string, unknown>

export interface HealthInfo {
  status: string
  app: string
  version: string
  time: string
}