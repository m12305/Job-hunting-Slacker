/* 模块四：统计 */
import { get } from './http'
import type { JobTypeStat, StatsOverview, TimeStat } from '@/types'

export const getStatsOverview = () => get<StatsOverview>('/stats/overview')
export const getStatsByJobType = () => get<JobTypeStat[]>('/stats/by-job-type')
export function getStatsByTime(params?: { granularity?: 'day' | 'week' | 'month'; start?: string; end?: string }) {
  return get<TimeStat>('/stats/by-time', params)
}