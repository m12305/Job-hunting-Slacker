/* 模块五 + 系统：话术 / 黑名单 / 任务 / 看板 / 设置 / 导出 / 健康 */
import { del, downloadBlob, get, post, put } from './http'
import type { BlacklistItem, DashboardToday, HealthInfo, Script, SettingsMap, Streak, Task } from '@/types'

/* ---- 话术库 ---- */
export function listScripts(params?: { category?: string; keyword?: string; favorite?: number }) {
  return get<Script[]>('/scripts', params)
}
export const createScript = (data: Record<string, unknown>) => post<Script>('/scripts', data)
export const updateScript = (id: number, data: Record<string, unknown>) => put<Script>(`/scripts/${id}`, data)
export const deleteScript = (id: number) => del<null>(`/scripts/${id}`)
export const setScriptFavorite = (id: number, favorite: boolean) =>
  put<Script>(`/scripts/${id}/favorite`, { favorite })
export const useScript = (id: number) => post<Script>(`/scripts/${id}/use`)

/* ---- 黑名单 ---- */
export function listBlacklist(params?: { company?: string; issue_type?: string }) {
  return get<BlacklistItem[]>('/blacklist', params)
}
export const createBlacklist = (data: Record<string, unknown>) => post<BlacklistItem>('/blacklist', data)
export const updateBlacklist = (id: number, data: Record<string, unknown>) =>
  put<BlacklistItem>(`/blacklist/${id}`, data)
export const deleteBlacklist = (id: number) => del<null>(`/blacklist/${id}`)
export const checkBlacklist = (company: string) => get<{ company: string; count: number }>('/blacklist/check', { company })

/* ---- 每日任务 ---- */
export function listTasks(params?: { due_date?: string }) {
  return get<Task[]>('/tasks', params)
}
export const createTask = (data: Record<string, unknown>) => post<Task>('/tasks', data)
export const updateTask = (id: number, data: Record<string, unknown>) => put<Task>(`/tasks/${id}`, data)
export const deleteTask = (id: number) => del<null>(`/tasks/${id}`)
export const setTaskDone = (id: number, done: boolean) => put<Task>(`/tasks/${id}/done`, { done })

/* ---- 看板 ---- */
export const getDashboardToday = () => get<DashboardToday>('/dashboard/today')
export const getDashboardStreak = () => get<Streak>('/dashboard/streak')

/* ---- 系统 ---- */
export const getSettings = () => get<SettingsMap>('/settings')
export const saveSettings = (data: Record<string, unknown>) => put<SettingsMap>('/settings', data)
export const exportBackup = () => downloadBlob('/export', `qiuzhao-backup-${new Date().toISOString().slice(0, 10)}.json`)
export function importBackup(tables: Record<string, unknown[]>) {
  return post<{ imported: Record<string, number> }>('/import', { tables })
}
export const getHealth = () => get<HealthInfo>('/health')