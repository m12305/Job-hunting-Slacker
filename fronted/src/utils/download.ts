/* 文件下载工具 */

/** 触发浏览器下载（同源 URL，利用后端 Content-Disposition） */
export function openDownload(url: string, target = '_blank'): void {
  const a = document.createElement('a')
  a.href = url
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