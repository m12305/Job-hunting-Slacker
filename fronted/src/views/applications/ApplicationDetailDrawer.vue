<template>
  <el-drawer
    :model-value="modelValue"
    :size="drawerSize"
    title="投递详情"
    destroy-on-close
    @update:model-value="(v: boolean) => emit('update:modelValue', v)"
  >
    <el-skeleton v-if="loading" :rows="10" animated />
    <template v-else-if="detail">
      <!-- 头部 -->
      <div class="head">
        <div class="h-title-row">
          <h2 class="h-company">{{ detail.company }}</h2>
          <StatusTag :dict="APPLICATION_STATUS" :value="detail.status" />
        </div>
        <div class="h-position">{{ detail.position }}</div>
        <div class="h-tags">
          <span v-if="detail.job_type_name" class="tag-line">
            <span class="dot" :style="{ background: jtColor(detail.job_type_id) }" />{{ detail.job_type_name }}
          </span>
          <span v-if="detail.city" class="tag-line"><el-icon><Location /></el-icon>{{ detail.city }}</span>
          <span v-if="detail.channel" class="tag-line"><el-icon><Share /></el-icon>{{ labelOf(APPLICATION_CHANNELS, detail.channel) }}</span>
          <span v-if="detail.salary_min || detail.salary_max" class="tag-line mono">{{ fmtSalary(detail.salary_min, detail.salary_max) }}</span>
          <span v-if="detail.resume_version_name" class="tag-line"><el-icon><Document /></el-icon>{{ detail.resume_version_name }}</span>
        </div>
        <div v-if="detail.apply_time" class="h-time mono">投递于 {{ fmtDateTime(detail.apply_time) }}</div>
      </div>

      <!-- 黑名单警告 -->
      <el-alert
        v-if="detail.blacklist_hits > 0"
        :title="`该公司在避雷库中有 ${detail.blacklist_hits} 条避雷记录，可前往避雷库查看。`"
        type="warning"
        show-icon
        :closable="false"
        class="warn"
      />

      <div v-if="detail.source_url" class="source-link">
        <a :href="detail.source_url" target="_blank" rel="noopener">{{ detail.source_url }}</a>
      </div>
      <p v-if="detail.remark" class="remark">{{ detail.remark }}</p>

      <!-- 操作 -->
      <div class="actions">
        <el-button type="primary" :disabled="!nextOptions.length" @click="openStatusDialog">
          <el-icon><Switch /></el-icon>&nbsp;流转状态（{{ nextOptions.length }} 个去向）
        </el-button>
        <el-button @click="openEdit"><el-icon><Edit /></el-icon>&nbsp;编辑</el-button>
        <el-button @click="(openExamLink = !openExamLink)"><el-icon><EditPen /></el-icon>&nbsp;笔试</el-button>
        <el-button @click="(openInterviewLink = !openInterviewLink)"><el-icon><ChatLineSquare /></el-icon>&nbsp;面试</el-button>
      </div>

      <!-- 新建笔试/面试两个浮层按钮 -->
      <transition name="pop">
        <div v-if="openExamLink || openInterviewLink" class="quick-create">
          <el-button v-if="openExamLink" type="primary" plain size="small" @click="linkTo('/exams', true)">
            <el-icon><Plus /></el-icon>&nbsp;为该公司新建笔试
          </el-button>
          <el-button v-if="openExamLink" @click="openExamLink = false">取消</el-button>
          <el-button v-if="openInterviewLink" type="primary" plain size="small" @click="linkTo('/interviews', true)">
            <el-icon><Plus /></el-icon>&nbsp;为该公司新建面试
          </el-button>
          <el-button v-if="openInterviewLink" @click="openInterviewLink = false">取消</el-button>
        </div>
      </transition>

      <!-- 状态时间线 -->
      <section class="section">
        <div class="section-title">状态流转时间线</div>
        <template v-if="detail.timeline.length">
          <div v-for="(log, i) in detail.timeline" :key="log.id" class="tl-item">
            <div class="tl-marker">
              <span class="tl-dot" :class="{ first: i === 0 }" />
              <span v-if="i < detail!.timeline.length - 1" class="tl-line" />
            </div>
            <div class="tl-body">
              <div class="tl-row">
                <span v-if="log.from_status" class="tl-from">{{ labelOf(APPLICATION_STATUS, log.from_status) }}</span>
                <el-icon v-if="log.from_status"><Right /></el-icon>
                <el-icon v-else><Plus /></el-icon>
                <span class="tl-to">{{ labelOf(APPLICATION_STATUS, log.to_status) }}</span>
                <span class="tl-time mono">{{ fmtDateTime(log.changed_at) }}</span>
              </div>
              <div v-if="log.note" class="tl-note">{{ log.note }}</div>
            </div>
          </div>
        </template>
        <div v-else class="no-timeline muted">暂无状态流转记录，创建投递时选择的初始状态即起点。</div>
      </section>

      <!-- 关联笔试 / 面试 / Offer -->
      <section v-if="detail.exams.length || detail.interviews.length || detail.offers.length" class="section">
        <div class="section-title">关联的笔面试与 Offer</div>

        <div v-if="detail.exams.length" class="rel-block">
          <div class="rel-title">笔试</div>
          <button v-for="e in detail.exams" :key="e.id" class="rel-row" @click="router.push({ path: '/exams', query: { focus: e.id } })">
            <span>{{ labelOf(EXAM_PLATFORMS, e.platform) }}</span>
            <span class="mono rel-time">{{ fmtDateTime(e.exam_time) }}</span>
            <StatusTag :dict="PROGRESS_STATUS" :value="e.status" />
            <el-icon><ArrowRight /></el-icon>
          </button>
        </div>

        <div v-if="detail.interviews.length" class="rel-block">
          <div class="rel-title">面试</div>
          <button v-for="i in detail.interviews" :key="i.id" class="rel-row" @click="router.push({ path: '/interviews', query: { focus: i.id } })">
            <span>{{ labelOf(INTERVIEW_ROUNDS, i.round) }}</span>
            <span class="mono rel-time">{{ fmtDateTime(i.interview_time) }}</span>
            <StatusTag :dict="PROGRESS_STATUS" :value="i.status" />
            <el-icon><ArrowRight /></el-icon>
          </button>
        </div>

        <div v-if="detail.offers.length" class="rel-block">
          <div class="rel-title">Offer</div>
          <button v-for="o in detail.offers" :key="o.id" class="rel-row" @click="router.push('/offers')">
            <span>{{ o.company }} · {{ o.position || detail.company }}</span>
            <StatusTag :dict="OFFER_STATUS" :value="o.status" />
            <el-icon><ArrowRight /></el-icon>
          </button>
        </div>
      </section>
    </template>

    <!-- 编辑复用投递表单（简化内联） -->
    <el-dialog
      v-model="editVisible"
      :title="`编辑投递 · ${detail?.company ?? ''}`"
      width="620px"
      append-to-body
      destroy-on-close
    >
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-position="top">
        <div class="egrid">
          <el-form-item label="公司" prop="company"><el-input v-model="editForm.company" /></el-form-item>
          <el-form-item label="岗位" prop="position"><el-input v-model="editForm.position" /></el-form-item>
          <el-form-item label="城市"><el-input v-model="editForm.city" /></el-form-item>
          <el-form-item label="岗位类型">
            <el-select v-model="editForm.job_type_id" clearable style="width: 100%">
              <el-option v-for="jt in jobTypes" :key="jt.id" :label="jt.name" :value="jt.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="薪资下限（K）">
            <el-input-number v-model="editForm.salary_min" :min="0" :max="999" style="width: 100%" />
          </el-form-item>
          <el-form-item label="薪资上限（K）">
            <el-input-number v-model="editForm.salary_max" :min="0" :max="999" style="width: 100%" />
          </el-form-item>
          <el-form-item label="渠道">
            <el-select v-model="editForm.channel" clearable style="width: 100%">
              <el-option v-for="(v, k) in APPLICATION_CHANNELS" :key="k" :label="v.label" :value="k" />
            </el-select>
          </el-form-item>
          <el-form-item label="投递时间">
            <el-date-picker v-model="editForm.apply_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
          </el-form-item>
        </div>
        <el-form-item label="投递链接"><el-input v-model="editForm.source_url" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="editForm.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="editSaving" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 状态流转 -->
    <el-dialog v-model="statusVisible" title="流转投递状态" width="440px" append-to-body destroy-on-close>
      <div class="status-flow">
        <div class="flow-row">
          <span class="muted">当前</span>
          <StatusTag :dict="APPLICATION_STATUS" :value="detail?.status" />
          <el-icon><Right /></el-icon>
          <el-select v-model="nextStatus" placeholder="选择下一状态" style="width: 180px">
            <el-option v-for="s in nextOptions" :key="s" :label="labelOf(APPLICATION_STATUS, s)" :value="s" />
          </el-select>
        </div>
        <div v-if="!nextOptions.length" class="flow-fail">当前状态已是终态，无法继续流转。</div>
        <el-form-item label="备注（选填）">
          <el-input v-model="statusNote" type="textarea" :rows="2" placeholder="如「一面挂，项目深挖不够」" />
        </el-form-item>
      </div>
      <template #footer>
        <el-button @click="statusVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!nextStatus" :loading="statusSaving" @click="saveStatus">确认流转</el-button>
      </template>
    </el-dialog>
  </el-drawer>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useDictStore } from '@/stores/dict'
import StatusTag from '@/components/StatusTag.vue'
import { getApplication, updateApplication, changeApplicationStatus } from '@/api'
import type { ApplicationDetail } from '@/types'
import {
  APPLICATION_CHANNELS,
  APPLICATION_STATUS,
  EXAM_PLATFORMS,
  INTERVIEW_ROUNDS,
  OFFER_STATUS,
  PROGRESS_STATUS,
  STATUS_TRANSITIONS,
  labelOf,
} from '@/constants'
import { fmtDateTime, fmtSalary } from '@/utils/format'

const props = defineProps<{
  modelValue: boolean
  applicationId: number | null
  reloadKey?: number
}>()
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void; (e: 'changed'): void }>()

const router = useRouter()
const dict = useDictStore()
const jobTypes = computed(() => dict.jobTypes)

const drawerSize = computed(() => (window.innerWidth < 860 ? '100%' : '55%'))

const detail = ref<ApplicationDetail | null>(null)
const loading = ref(false)
const jtColor = (id: number | null) => dict.jobTypeColor(id)

const nextOptions = computed(() => (detail.value ? (STATUS_TRANSITIONS[detail.value.status] ?? []) : []))
const openExamLink = ref(false)
const openInterviewLink = ref(false)

async function fetchData() {
  if (!props.applicationId) return
  loading.value = true
  try {
    detail.value = await getApplication(props.applicationId)
    openExamLink.value = false
    openInterviewLink.value = false
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.modelValue, props.applicationId, props.reloadKey],
  ([open]) => {
    if (open && props.applicationId) fetchData()
  },
  { immediate: true },
)

/* ---- 状态流转 ---- */
const statusVisible = ref(false)
const statusSaving = ref(false)
const nextStatus = ref('')
const statusNote = ref('')

function openStatusDialog() {
  nextStatus.value = ''
  statusNote.value = ''
  statusVisible.value = true
}
async function saveStatus() {
  if (!nextStatus.value) return
  statusSaving.value = true
  try {
    await changeApplicationStatus(props.applicationId!, { to_status: nextStatus.value, note: statusNote.value || undefined })
    ElMessage.success(`已流转为「${labelOf(APPLICATION_STATUS, nextStatus.value)}」`)
    statusVisible.value = false
    fetchData()
    emit('changed')
  } catch {
    /* 409 已提示 */
  } finally {
    statusSaving.value = false
  }
}

function linkTo(path: string, isNew: boolean) {
  router.push({ path, query: isNew ? { new: '1', application_id: String(props.applicationId) } : {} })
}

/* ---- 内联编辑 ---- */
const editVisible = ref(false)
const editSaving = ref(false)
const editFormRef = ref<FormInstance>()
const editForm = reactive<Record<string, unknown>>({})
const editRules: FormRules = {
  company: [{ required: true, message: '请填写公司', trigger: 'blur' }],
  position: [{ required: true, message: '请填写岗位', trigger: 'blur' }],
}
function openEdit() {
  if (!detail.value) return
  Object.assign(editForm, {
    company: detail.value.company,
    position: detail.value.position,
    city: detail.value.city ?? '',
    salary_min: detail.value.salary_min,
    salary_max: detail.value.salary_max,
    channel: detail.value.channel,
    apply_time: detail.value.apply_time,
    job_type_id: detail.value.job_type_id,
    source_url: detail.value.source_url ?? '',
    remark: detail.value.remark ?? '',
  })
  editVisible.value = true
}
async function saveEdit() {
  await editFormRef.value?.validate()
  editSaving.value = true
  try {
    await updateApplication(props.applicationId!, editForm)
    ElMessage.success('已保存')
    editVisible.value = false
    fetchData()
    emit('changed')
  } finally {
    editSaving.value = false
  }
}
</script>

<style scoped>
.head {
  padding: 4px 2px 16px;
  border-bottom: 1px solid var(--line);
  margin-bottom: 16px;
}
.h-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.h-company {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.h-position {
  margin-top: 2px;
  font-size: 13.5px;
  color: var(--ink-2);
}
.h-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px;
}
.tag-line {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12.5px;
  color: var(--ink-2);
}
.h-time {
  margin-top: 8px;
  font-size: 11.5px;
  color: var(--ink-3);
}
.warn {
  border-radius: 8px;
  margin-bottom: 12px;
}
.source-link {
  font-size: 12px;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.source-link a {
  color: var(--accent-strong);
  text-decoration: none;
}
.remark {
  font-size: 12.5px;
  color: var(--ink-2);
  background: var(--surface-2);
  border-radius: 8px;
  padding: 10px 12px;
  white-space: pre-line;
  margin: 0 0 14px;
}
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 18px;
}
.quick-create {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
  padding: 12px;
  background: var(--bg-soft);
  border: 1px dashed var(--line-strong);
  border-radius: 10px;
  flex-wrap: wrap;
}
.pop-enter-active,
.pop-leave-active {
  transition: opacity 0.2s ease, transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.section {
  margin-bottom: 22px;
}
.section-title {
  font-size: 12px;
  letter-spacing: 0.12em;
  color: var(--ink-3);
  font-weight: 600;
  margin-bottom: 12px;
  text-transform: uppercase;
}
.no-timeline {
  font-size: 12.5px;
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
}
.tl-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--line-strong);
  margin-top: 6px;
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
  padding-bottom: 16px;
  min-width: 0;
}
.tl-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.tl-from {
  color: var(--ink-3);
}
.tl-to {
  font-weight: 600;
  color: var(--ink);
}
.tl-time {
  margin-left: auto;
  font-size: 11px;
  color: var(--ink-3);
}
.tl-note {
  margin-top: 5px;
  font-size: 12px;
  color: var(--ink-2);
  background: var(--surface-2);
  border-radius: 8px;
  padding: 7px 10px;
}

.rel-block {
  margin-bottom: 12px;
}
.rel-title {
  font-size: 12px;
  color: var(--ink-3);
  margin-bottom: 6px;
}
.rel-row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--surface);
  font-size: 12.5px;
  color: var(--ink-2);
  cursor: pointer;
  margin-bottom: 6px;
  font-family: inherit;
  transition: all 0.18s;
}
.rel-row:hover {
  border-color: var(--accent-line);
  background: var(--accent-soft);
  color: var(--accent-strong);
}
.rel-time {
  color: var(--ink-3);
  margin-left: auto;
  font-size: 11.5px;
}
.egrid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 14px;
}
@media (max-width: 640px) {
  .egrid {
    grid-template-columns: 1fr;
  }
}
</style>