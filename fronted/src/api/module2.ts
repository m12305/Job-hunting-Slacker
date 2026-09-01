/* 模块二：投递 / 状态流水 / Offer / 权重 / 对比 */
import { del, get, post, put } from './http'
import type {
  Application,
  ApplicationDetail,
  ApplicationPage,
  Offer,
  OfferCompareResult,
  OfferWeight,
  PageData,
  StatusLog,
} from '@/types'

/* ---- 投递 ---- */
export function listApplications(params?: {
  status?: string
  status_group?: string
  company?: string
  position?: string
  city?: string
  channel?: string
  job_type_id?: number
  keyword?: string
  apply_time_range?: string
  apply_time_from?: string
  apply_time_to?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
  page?: number
  page_size?: number
}) {
  return get<ApplicationPage>('/applications', params)
}
export const getApplication = (id: number) => get<ApplicationDetail>(`/applications/${id}`)
export const createApplication = (data: Record<string, unknown>) => post<Application>('/applications', data)
export const updateApplication = (id: number, data: Record<string, unknown>) =>
  put<Application>(`/applications/${id}`, data)
export const deleteApplication = (id: number) => del<null>(`/applications/${id}`)
export const changeApplicationStatus = (id: number, data: { to_status: string; note?: string; close_reason?: string }) =>
  put<Application & { changed: boolean }>(`/applications/${id}/status`, data)
export const getApplicationTimeline = (id: number) => get<StatusLog[]>(`/applications/${id}/timeline`)

/* ---- Offer ---- */
export function listOffers(params?: { status?: string; application_id?: number }) {
  return get<Offer[]>('/offers', params)
}
export const getOffer = (id: number) => get<Offer>(`/offers/${id}`)
export const createOffer = (data: Record<string, unknown>) => post<Offer>('/offers', data)
export const updateOffer = (id: number, data: Record<string, unknown>) => put<Offer>(`/offers/${id}`, data)
export const deleteOffer = (id: number) => del<null>(`/offers/${id}`)
export const compareOffers = (data: { offer_ids: number[]; weight_overrides?: Record<string, unknown> }) =>
  post<OfferCompareResult>('/offers/compare', data)

/* ---- 权重配置 ---- */
export const getWeightConfig = () => get<OfferWeight[]>('/offer-weight-config')
export const updateWeightConfig = (list: Partial<OfferWeight>[]) => put<OfferWeight[]>('/offer-weight-config', list)
