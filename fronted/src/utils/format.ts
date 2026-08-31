/* 日期 / 数字格式化工具 */

const pad = (n: number) => String(n).padStart(2, '0')

/** ISO 字符串 → "YYYY-MM-DD" */
export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso.slice(0, 10)
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

/** ISO 字符串 → "YYYY-MM-DD HH:mm" */
export function fmtDateTime(iso: string | null | undefined): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return `${fmtDate(iso)} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const WEEKDAYS = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

/** 今日中文日期，如 "8月30日 · 周六" */
export function todayLabel(now = new Date()): string {
  return `${now.getMonth() + 1}月${now.getDate()}日 · ${WEEKDAYS[now.getDay()]}`
}

/** 相对时间："刚刚 / N 分钟前 / N 小时前 / N 天前 / 日期" */
export function fmtRelative(iso: string | null | undefined): string {
  if (!iso) return '—'
  const t = new Date(iso).getTime()
  if (Number.isNaN(t)) return iso
  const diff = Date.now() - t
  const min = Math.floor(diff / 60000)
  if (min < 1) return '刚刚'
  if (min < 60) return `${min} 分钟前`
  const hour = Math.floor(min / 60)
  if (hour < 24) return `${hour} 小时前`
  const day = Math.floor(hour / 24)
  if (day < 7) return `${day} 天前`
  return fmtDate(iso)
}

/** 字节数 → "1.2 MB" */
export function fmtSize(bytes: number | null | undefined): string {
  if (!bytes) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

/** 薪资区间 "15–25K" */
export function fmtSalary(min: number | null | undefined, max: number | null | undefined, currency = 'CNY'): string {
  const cur = currency === 'USD' ? '$' : ''
  const k = currency === 'USD' ? 'K' : 'K'
  if (min == null && max == null) return '—'
  if (min == null) return `${cur}${max}${k}`
  if (max == null) return `${cur}${min}${k}`
  return min === max ? `${cur}${min}${k}` : `${cur}${min}–${max}${k}`
}

/** 小数比例 → "35.0%" */
export function fmtRate(rate: number | null | undefined, digits = 1): string {
  if (rate == null) return '—'
  return `${(rate * 100).toFixed(digits)}%`
}

/** 年薪（Offer）：base × 月数 + 绩效 + 签字费 */
export function annualSalary(o: {
  salary_base: number | null
  salary_months: number | null
  bonus_performance: number | null
  signing_bonus: number | null
}): number | null {
  if (o.salary_base == null) return null
  return o.salary_base * (o.salary_months || 12) + (o.bonus_performance || 0) + (o.signing_bonus || 0)
}

/* 从相对文件路径取文件名（data/files/xxx/x.pdf → x.pdf） */
export function baseName(path: string | null | undefined): string {
  if (!path) return ''
  return path.split('/').pop() || path
}