/* ============================================================
   Axios 实例与统一请求封装
   响应结构：{ code, message, data }；code!==0 视为业务错误
   ============================================================ */
import axios, { type AxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types'

const http = axios.create({
  baseURL: '/api',
  timeout: 20000,
})

http.interceptors.response.use(
  (res) => {
    const body = res.data as ApiResponse | undefined
    if (body && typeof body === 'object' && 'code' in body && body.code !== 0) {
      ElMessage.error(body.message || '请求失败')
      return Promise.reject(new Error(body.message || '请求失败'))
    }
    return res
  },
  (error) => {
    const msg =
      error.response?.data?.message || (error.code === 'ECONNABORTED' ? '请求超时，请检查后端服务' : error.message)
    ElMessage.error(msg || '网络错误')
    return Promise.reject(error)
  },
)

async function unwrap<T>(config: AxiosRequestConfig): Promise<T> {
  const res = await http.request<ApiResponse<T>>(config)
  return res.data.data as T
}

export function get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  return unwrap<T>({ method: 'GET', url, params })
}

export function post<T>(url: string, data?: unknown): Promise<T> {
  return unwrap<T>({ method: 'POST', url, data })
}

export function put<T>(url: string, data?: unknown): Promise<T> {
  return unwrap<T>({ method: 'PUT', url, data })
}

export function del<T>(url: string): Promise<T> {
  return unwrap<T>({ method: 'DELETE', url })
}

/** multipart 文件上传（字段名统一为 file，可带额外表单字段） */
export function uploadFile<T>(
  url: string,
  file: File,
  extra?: Record<string, string>,
  onProgress?: (percent: number) => void,
): Promise<T> {
  const fd = new FormData()
  fd.append('file', file)
  if (extra) {
    for (const [k, v] of Object.entries(extra)) fd.append(k, v)
  }
  return unwrap<T>({
    method: 'POST',
    url,
    data: fd,
    timeout: 120000,
    onUploadProgress: (e) => {
      if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100))
    },
  })
}

/** 二进制下载（导出 JSON 等） */
export async function downloadBlob(url: string, filename: string, params?: Record<string, unknown>): Promise<void> {
  const res = await http.request({ method: 'GET', url, params, responseType: 'blob', timeout: 60000 })
  const blob = res.data as Blob
  const objectUrl = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = objectUrl
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(objectUrl), 5000)
}

export default http
