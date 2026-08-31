<template>
  <el-drawer
    :model-value="modelValue"
    :size="drawerSize"
    :title="resume?.version_name || '简历预览'"
    destroy-on-close
    @update:model-value="(v: boolean) => emit('update:modelValue', v)"
  >
    <template #header>
      <div class="drawer-head">
        <div>
          <div class="dtitle">{{ resume?.version_name || '简历预览' }}</div>
          <div class="dsub">
            <StatusTag :dict="RESUME_STATUS" :value="resume?.status" />
            <span v-if="resume?.target_position">{{ resume.target_position }}</span>
          </div>
        </div>
        <div v-if="resume" class="dops">
          <el-button size="small" :disabled="!resume.file_path" @click="openInTab">
            <el-icon><Position /></el-icon>&nbsp;新窗口
          </el-button>
          <el-button size="small" type="primary" plain :disabled="!resume.file_path" @click="download">
            <el-icon><Download /></el-icon>&nbsp;下载文件
          </el-button>
        </div>
      </div>
    </template>

    <el-tabs v-model="tab" class="drawer-tabs">
      <!-- 预览 -->
      <el-tab-pane label="预览" name="preview">
        <div v-if="!resume?.file_path" class="preview-fallback">
          <EmptyState icon="Document" title="尚未上传简历文件" desc="先为这个版本上传 PDF 或 Word 文件，即可在应用内预览。" />
        </div>

        <div v-else-if="previewError" class="preview-fallback">
          <EmptyState
            icon="Warning"
            :title="previewError"
            desc="当前环境可能缺少 LibreOffice 转换支持，可下载文件后用本机软件查看。"
          >
            <template #action>
              <el-button type="primary" plain @click="download">下载原文件</el-button>
            </template>
          </EmptyState>
        </div>

        <div v-else class="pdf-wrap">
          <div v-if="previewLoading" class="pdf-loading">
            <el-icon class="is-loading" :size="22"><Loading /></el-icon>
            <span>正在加载预览{{ resume?.file_type === 'doc' || resume?.file_type === 'docx' ? '（Word 正在转换…）' : '' }}</span>
          </div>
          <iframe v-show="!previewLoading" :src="previewSrc" class="pdf-frame" />
        </div>
      </el-tab-pane>

      <!-- 修改日志 -->
      <el-tab-pane label="修改日志" name="logs">
        <div class="log-compose">
          <el-input v-model="newLog" placeholder="记录一次修改，如「更新项目经历 STAR 描述」" @keyup.enter="addLog" />
          <el-button type="primary" plain :disabled="!newLog.trim()" @click="addLog">记录</el-button>
        </div>

        <el-skeleton v-if="logsLoading" :rows="4" animated />
        <EmptyState v-else-if="!logs.length" icon="Clock" title="还没有修改记录" desc="每次上传文件或手动记录，都会在这里留下时间线。" />

        <div v-else class="timeline">
          <div v-for="(log, i) in logs" :key="log.id" class="tl-item">
            <div class="tl-marker">
              <span class="tl-dot" :class="{ first: i === 0 }" />
              <span v-if="i < logs.length - 1" class="tl-line" />
            </div>
            <div class="tl-body">
              <div class="tl-desc">{{ log.change_desc }}</div>
              <div class="tl-time mono">{{ fmtDateTime(log.changed_at) }} · {{ log.trigger_source === 'sync' ? '同步' : '手动' }}</div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </el-drawer>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import StatusTag from '@/components/StatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import { createResumeLog, listResumeLogs, resumeFileUrl, resumePreviewUrl } from '@/api'
import http from '@/api/http'
import type { Resume, ResumeLog } from '@/types'
import { RESUME_STATUS } from '@/constants'
import { fmtDateTime } from '@/utils/format'
import { openDownload } from '@/utils/download'

const props = defineProps<{ modelValue: boolean; resume: Resume | null }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void; (e: 'uploaded'): void }>()

const drawerSize = computed(() => (window.innerWidth < 860 ? '100%' : '68%'))

const tab = ref('preview')
const logs = ref<ResumeLog[]>([])
const logsLoading = ref(false)
const newLog = ref('')

const previewSrc = ref('')
const previewLoading = ref(false)
const previewError = ref('')

watch(
  () => props.modelValue,
  async (open) => {
    if (!open || !props.resume) return
    tab.value = 'preview'
    logs.value = []
    newLog.value = ''
    previewError.value = ''
    if (props.resume.file_path) await preparePreview()
    loadLogs()
  },
)

async function preparePreview() {
  const r = props.resume!
  if (r.file_type === 'pdf') {
    previewSrc.value = resumePreviewUrl(r.id)
    return
  }
  if (r.file_type === 'doc' || r.file_type === 'docx') {
    // Word：尝试后端转换；失败时优雅降级
    previewLoading.value = true
    try {
      const res = await http.request({ method: 'GET', url: resumePreviewUrl(r.id), responseType: 'blob', timeout: 90000 })
      const blob = res.data as Blob
      if (blob.type === 'application/pdf' && blob.size > 0) {
        previewSrc.value = URL.createObjectURL(blob)
      } else {
        previewError.value = 'Word 转换结果异常，无法预览'
      }
    } catch (e) {
      const axiosErr = e as { response?: { status?: number } }
      if (axiosErr.response?.status === 409) {
        previewError.value = '当前环境不支持 Word 在线预览（缺少转换组件）'
      } else {
        previewError.value = '预览加载失败'
      }
    } finally {
      previewLoading.value = false
    }
  }
}

async function loadLogs() {
  if (!props.resume) return
  logsLoading.value = true
  try {
    logs.value = await listResumeLogs(props.resume.id)
  } finally {
    logsLoading.value = false
  }
}

async function addLog() {
  const desc = newLog.value.trim()
  if (!desc || !props.resume) return
  await createResumeLog({ resume_version_id: props.resume.id, change_desc: desc })
  newLog.value = ''
  ElMessage.success('已记录')
  loadLogs()
}

function download() {
  if (props.resume) openDownload(resumeFileUrl(props.resume.id, 'attachment'))
}
function openInTab() {
  if (props.resume) openDownload(resumeFileUrl(props.resume.id, 'inline'))
}
</script>

<style scoped>
.drawer-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  padding-right: 8px;
}
.dtitle {
  font-size: 15.5px;
  font-weight: 700;
}
.dsub {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  font-size: 12.5px;
  color: var(--ink-2);
}
.dops {
  display: flex;
  gap: 8px;
}
.drawer-tabs {
  margin-top: 8px;
}

.pdf-wrap {
  position: relative;
  height: calc(100dvh - 220px);
  background: #eceae4;
  border-radius: var(--r-md);
  overflow: hidden;
  border: 1px solid var(--line);
}
.pdf-frame {
  width: 100%;
  height: 100%;
  border: none;
  background: #fff;
}
.pdf-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--ink-3);
  font-size: 12.5px;
  background: var(--bg-soft);
}
.preview-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 320px;
  border: 1px dashed var(--line-strong);
  border-radius: var(--r-md);
  background: var(--bg-soft);
}

.log-compose {
  display: flex;
  gap: 8px;
  margin-bottom: 18px;
}
.timeline {
  display: flex;
  flex-direction: column;
}
.tl-item {
  display: flex;
  gap: 14px;
}
.tl-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 12px;
  flex-shrink: 0;
}
.tl-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--line-strong);
  margin-top: 5px;
  flex-shrink: 0;
}
.tl-dot.first {
  background: var(--accent);
}
.tl-line {
  flex: 1;
  width: 1.5px;
  background: var(--line);
  margin: 3px 0;
}
.tl-body {
  padding-bottom: 20px;
  min-width: 0;
}
.tl-desc {
  font-size: 13.5px;
  color: var(--ink);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 10px 14px;
  line-height: 1.6;
}
.tl-time {
  margin-top: 6px;
  font-size: 11.5px;
  color: var(--ink-3);
}
</style>