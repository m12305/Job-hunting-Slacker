/* ============================================================
   枚举字典：后端小写下划线枚举 → 中文展示名 / 展示色
   ============================================================ */

export interface DictEntry {
  label: string
  color: string
  dot: string
}

export function makeDict(entries: Record<string, [label: string, dot: string]>): Record<string, DictEntry> {
  const out: Record<string, DictEntry> = {}
  for (const [key, [label, dot]] of Object.entries(entries)) {
    out[key] = { label, color: dot, dot }
  }
  return out
}

/* 简历状态 */
export const RESUME_STATUS = makeDict({
  draft: ['草稿', '#a8a29e'],
  active: ['使用中', '#1a7f5c'],
  archived: ['已归档', '#8f8a83'],
})

/* 投递状态（状态机全序） */
export const APPLICATION_STATUS = makeDict({
  pending: ['待投递', '#8f8a83'],
  applied: ['已投递', '#0369a1'],
  resume_screening: ['筛选中', '#1d4ed8'],
  resume_rejected: ['挂简历', '#b3402f'],
  exam: ['笔试中', '#b45309'],
  interview: ['面试中', '#0f766e'],
  ended: ['已结束', '#57534e'],
  offered: ['已 Offer', '#1a7f5c'],
  rejected: ['已拒', '#9f1239'],
})

/* 状态机：当前状态 -> 合法下一步（与 backend core/constants 一致） */
export const STATUS_TRANSITIONS: Record<string, string[]> = {
  pending: ['applied', 'ended'],
  applied: ['resume_screening', 'resume_rejected', 'exam', 'interview', 'ended'],
  resume_screening: ['resume_rejected', 'exam', 'interview', 'ended'],
  resume_rejected: ['ended'],
  exam: ['interview', 'ended'],
  interview: ['ended', 'offered', 'rejected'],
  ended: ['offered'],
  offered: ['rejected'],
  rejected: [],
}

/* 投递渠道 */
export const APPLICATION_CHANNELS = makeDict({
  boss: ['BOSS直聘', '#0369a1'],
  nowcoder: ['牛客', '#0f766e'],
  official: ['官网', '#b45309'],
  referral: ['内推', '#b7791f'],
  other: ['其他', '#8f8a83'],
})

/* Offer 状态 */
export const OFFER_STATUS = makeDict({
  pending: ['待决策', '#b45309'],
  accepted: ['已接受', '#1a7f5c'],
  rejected: ['已拒绝', '#8f8a83'],
})

/* 面试轮次 */
export const INTERVIEW_ROUNDS = makeDict({
  first: ['一面', '#0369a1'],
  second: ['二面', '#1d4ed8'],
  third: ['三面', '#0f766e'],
  hr: ['HR面', '#b7791f'],
  final: ['终面', '#9f1239'],
  other: ['其他', '#8f8a83'],
})

/* 笔试平台 */
export const EXAM_PLATFORMS = makeDict({
  nowcoder: ['牛客', '#0f766e'],
  saikr: ['赛码', '#0369a1'],
  official: ['官网', '#b45309'],
  other: ['其他', '#8f8a83'],
})

/* 笔试/面试的进行状态 */
export const PROGRESS_STATUS = makeDict({
  upcoming: ['进行中', '#b45309'],
  done: ['已完成', '#1a7f5c'],
  cancelled: ['已取消', '#8f8a83'],
})

/* 面试结果 */
export const INTERVIEW_RESULTS = makeDict({
  passed: ['通过', '#1a7f5c'],
  failed: ['挂掉', '#b3402f'],
})

/* 素材分类 */
export const MATERIAL_CATEGORIES = makeDict({
  project: ['项目经历', '#0369a1'],
  internship: ['实习经历', '#0f766e'],
  campus: ['校园经历', '#6d28d9'],
  award: ['获奖证书', '#b45309'],
  other: ['其他经历', '#8f8a83'],
})

/* 资产分类 */
export const ASSET_CATEGORIES = makeDict({
  blog: ['博客', '#0369a1'],
  project: ['项目', '#0f766e'],
  github: ['GitHub', '#1c1917'],
  transcript: ['成绩单', '#b45309'],
  certificate: ['证书', '#b7791f'],
  other: ['其他', '#8f8a83'],
})

/* 题库分类 */
export const QUESTION_CATEGORIES = makeDict({
  code: ['手撕代码', '#b3402f'],
  baguwen: ['八股文', '#0369a1'],
  project_ask: ['项目反问', '#0f766e'],
  other: ['其他', '#8f8a83'],
})

/* 题目难度 */
export const QUESTION_DIFFICULTY = makeDict({
  easy: ['简单', '#1a7f5c'],
  medium: ['中等', '#b7791f'],
  hard: ['困难', '#b3402f'],
})

/* 题目复习状态 */
export const QUESTION_REVIEW_STATUS = makeDict({
  new: ['新收录', '#8f8a83'],
  todo: ['待刷', '#b45309'],
  mastered: ['已掌握', '#1a7f5c'],
})

/* 话术分类 */
export const SCRIPT_CATEGORIES = makeDict({
  general: ['通用', '#b45309'],
  tech: ['技术', '#0f766e'],
  custom: ['自定义', '#6d28d9'],
})

/* 黑名单类型 */
export const BLACKLIST_TYPES = makeDict({
  overtime: ['加班严重', '#b3402f'],
  fake_salary: ['薪资虚假', '#9f1239'],
  free_trial: ['无偿试岗', '#b7791f'],
  trap_interview: ['套路面试', '#b45309'],
  other: ['其他', '#8f8a83'],
})

/* 任务类型 */
export const TASK_TYPES = makeDict({
  apply: ['投递', '#0369a1'],
  review: ['复盘', '#b7791f'],
  coding: ['刷题', '#b45309'],
  custom: ['自定义', '#6d28d9'],
})

/* 通用查找 */
export function labelOf(dict: Record<string, DictEntry>, key: string | null | undefined): string {
  if (!key) return '—'
  return dict[key]?.label ?? key
}

export function colorOf(dict: Record<string, DictEntry>, key: string | null | undefined): string {
  if (!key) return '#8f8a83'
  return dict[key]?.dot ?? '#8f8a83'
}

/* Offer 打分维度中文名（对比结果用） */
export const DIMENSION_NAMES: Record<string, string> = {
  salary: '薪资',
  city: '城市',
  work_intensity: '加班强度',
  industry: '行业前景',
  company_scale: '公司规模',
  position_dev: '岗位发展',
}