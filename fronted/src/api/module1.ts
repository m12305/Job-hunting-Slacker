/* 模块一：岗位类型 / 简历 / 修改日志 / 素材 / 资产 */
import { del, get, post, put, uploadFile } from './http'
import type { Asset, JobType, Material, Resume, ResumeDetail, ResumeLog } from '@/types'

/* ---- 岗位类型 ---- */
export const listJobTypes = () => get<JobType[]>('/job-types')
export const createJobType = (data: Partial<JobType>) => post<JobType>('/job-types', data)
export const updateJobType = (id: number, data: Partial<JobType>) => put<JobType>(`/job-types/${id}`, data)
export const deleteJobType = (id: number) => del<null>(`/job-types/${id}`)

/* ---- 简历版本 ---- */
export function listResumes(params?: { job_type_id?: number; keyword?: string }) {
  return get<Resume[]>('/resumes', params)
}
export const getResume = (id: number) => get<ResumeDetail>(`/resumes/${id}`)
export const createResume = (data: Partial<Resume>) => post<Resume>('/resumes', data)
export const updateResume = (id: number, data: Partial<Resume>) => put<Resume>(`/resumes/${id}`, data)
export const deleteResume = (id: number) => del<null>(`/resumes/${id}`)
export const uploadResumeFile = (id: number, file: File, onProgress?: (p: number) => void) =>
  uploadFile<Resume>(`/resumes/${id}/upload`, file, undefined, onProgress)
export const setResumeDefault = (id: number) => post<Resume>(`/resumes/${id}/set-default`)

/** 下载/预览 URL（iframe 或新窗口直接使用） */
export const resumeFileUrl = (id: number, disposition: 'inline' | 'attachment' = 'inline') =>
  `/api/resumes/${id}/file?disposition=${disposition}`

/** 预览地址（PDF 直接返回 / Word 转 PDF） */
export const resumePreviewUrl = (id: number) => `/api/resumes/${id}/preview`

/* ---- 修改日志 ---- */
export const listResumeLogs = (id: number) => get<ResumeLog[]>(`/resumes/${id}/logs`)
export const createResumeLog = (data: { resume_version_id: number; change_desc: string; changed_at?: string }) =>
  post<ResumeLog>('/resume-logs', data)

/* ---- 素材库 ---- */
export const listMaterialCategories = () => get<string[]>('/materials/categories')
export function listMaterials(params?: { category?: string; keyword?: string; tag?: string }) {
  return get<Material[]>('/materials', params)
}
export const createMaterial = (data: Partial<Material>) => post<Material>('/materials', data)
export const updateMaterial = (id: number, data: Partial<Material>) => put<Material>(`/materials/${id}`, data)
export const deleteMaterial = (id: number) => del<null>(`/materials/${id}`)

/* ---- 资产归档 ---- */
export function listAssets(params?: { category?: string; keyword?: string }) {
  return get<Asset[]>('/assets', params)
}
export const createAsset = (data: Partial<Asset>) => post<Asset>('/assets', data)
export const updateAsset = (id: number, data: Partial<Asset>) => put<Asset>(`/assets/${id}`, data)
export const deleteAsset = (id: number) => del<null>(`/assets/${id}`)
export const uploadAsset = (data: { category: string; title: string; description?: string; tags?: string; file: File }) =>
  uploadFile<Asset>('/assets/upload', data.file, {
    category: data.category,
    title: data.title,
    ...(data.description ? { description: data.description } : {}),
    ...(data.tags ? { tags: data.tags } : {}),
  })