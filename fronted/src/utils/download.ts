/* 文件下载工具 */

/** 仅允许浏览器打开 http(s) 或当前站点相对地址。 */
export function safeHttpUrl(url: string | null | undefined): string | null {
  if (!url) return null
  try {
    const parsed = new URL(url, window.location.origin)
    return ['http:', 'https:'].includes(parsed.protocol) ? parsed.href : null
  } catch {
    return null
  }
}

/** 触发浏览器下载（同源 URL，利用后端 Content-Disposition） */
export function openDownload(url: string, target = '_blank'): void {
  const safeUrl = safeHttpUrl(url)
  if (!safeUrl) return
  const a = document.createElement('a')
  a.href = safeUrl
  a.target = target
  a.rel = 'noopener'
  document.body.appendChild(a)
  a.click()
  a.remove()
}

/** 将 Blob 保存为本地文件 */
export function saveBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 5000)
}
