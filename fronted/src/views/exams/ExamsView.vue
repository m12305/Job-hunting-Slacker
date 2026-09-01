<template>
  <div class="page">
    <PageHeader
      kicker="MODULE 03 · 笔试面试"
      title="笔试管理"
      desc="记录笔试时间、平台、链接与账号密码，考后填写复盘，形成可追溯的笔试闭环。"
    >
      <template #actions>
        <el-button type="primary" @click="openCreate"><el-icon><Plus /></el-icon>&nbsp;新增笔试</el-button>
      </template>
    </PageHeader>

    <div class="filter-row">
      <button class="chip" :class="{ active: filterStatus === '' }" @click="filterStatus = ''; load()">
        全部 <span class="mono">{{ items.length }}</span>
      </button>
      <button v-for="(v, k) in PROGRESS_STATUS" :key="k" class="chip" :class="{ active: filterStatus === k }" @click="filterStatus = k; load()">
        <span class="dot" :style="{ background: v.dot }" />{{ v.label }}
      </button>
      <el-select v-model="filterPlatform" placeholder="全部平台" clearable class="p-select" @change="load()">
        <el-option v-for="(v, k) in EXAM_PLATFORMS" :key="k" :label="v.label" :value="k" />
      </el-select>
    </div>

    <el-skeleton v-if="loading" :rows="6" animated class="panel" style="padding: 20px" />
    <EmptyState
      v-else-if="!items.length"
      icon="EditPen"
      title="还没有笔试记录"
      desc="投递进入「笔试」阶段后，在这里登记时间与链接，避免错过关键节点。"
    >
      <template #action>
        <el-button type="primary" @click="openCreate">新增笔试</el-button>
      </template>
    </EmptyState>

    <div v-else class="list">
      <article v-for="e in items" :key="e.id" class="exam panel card-hover">
        <div class="e-left">
          <div class="e-time-mono">
            <div class="e-date mono">{{ e.exam_time ? fmtDate(e.exam_time) : '待定' }}</div>
            <div v-if="e.exam_time" class="e-time mono">{{ timePart(e.exam_time) }}</div>
          </div>
          <div class="e-mid">
            <div class="e-top">
              <StatusTag :dict="EXAM_PLATFORMS" :value="e.platform" />
              <StatusTag :dict="PROGRESS_STATUS" :value="e.status" />
              <span v-if="e.duration_minutes" class="mono e-duration">{{ e.duration_minutes }} 分钟</span>
            </div>
            <div class="e-links">
              <a v-if="safeHttpUrl(e.exam_link)" :href="safeHttpUrl(e.exam_link) || undefined" target="_blank" rel="noopener" class="link" @click.stop>
                <el-icon><Link /></el-icon><span class="l-text">{{ e.exam_link }}</span>
              </a>
              <span v-if="e.account" class="cred">
                <el-icon><User /></el-icon>{{ e.account }}
                <template v-if="e.password">
                  <span class="pwd">{{ showPwd.has(e.id) ? e.password : '••••••' }}</span>
                  <button class="eye" @click.stop="togglePwd(e.id)">
                    <el-icon><component :is="showPwd.has(e.id) ? 'Hide' : 'View'" /></el-icon>
                  </button>
                </template>
              </span>
            </div>
            <div v-if="appOf(e.application_id)" class="e-app">
              <span class="muted">关联投递</span>
              <button class="app-link" @click="goApp(e)">{{ appOf(e.application_id) }}</button>
            </div>
            <div v-if="reviews.get(e.id)?.summary" class="e-review-summary">
              <el-icon><DocumentChecked /></el-icon>{{ reviews.get(e.id)?.summary }}
            </div>
          </div>
        </div>

        <div class="e-ops">
          <el-tooltip :content="reviews.get(e.id) ? '修改复盘' : '写复盘'" placement="top">
            <button class="op" :class="{ active: !!reviews.get(e.id) }" @click="openReview(e)">
              <el-icon><EditPen /></el-icon>
            </button>
          </el-tooltip>
          <el-tooltip :content="e.status === 'done' ? '已完成' : (e.status === 'cancelled' ? '已取消' : '标记完成')" placement="top">
            <button class="op" :disabled="e.status !== 'upcoming'" @click="markDone(e)">
              <el-icon><CircleCheck /></el-icon>
            </button>
          </el-tooltip>
          <el-tooltip content="编辑" placement="top">
            <button class="op" @click="openEdit(e)"><el-icon><Edit /></el-icon></button>
          </el-tooltip>
          <el-tooltip content="删除" placement="top">
            <button class="op danger" @click="remove(e)"><el-icon><Delete /></el-icon></button>
          </el-tooltip>
        </div>
      </article>
    </div>

    <!-- 表单 -->
    <el-dialog
      v-model="formVisible"
      :title="editing ? '编辑笔试' : '新增笔试'"
      width="min(560px, calc(100vw - 24px))"
      class="viewport-dialog"
      append-to-body
      destroy-on-close
      top="2vh"
    >
      <el-form :model="form" label-position="top">
        <el-form-item label="关联投递">
          <el-select v-model="form.application_id" clearable filterable style="width: 100%" placeholder="选择投递记录">
            <el-option v-for="a in appOptions" :key="a.id" :label="`${a.company} · ${a.position}`" :value="a.id" />
          </el-select>
        </el-form-item>
        <div class="f-row">
          <el-form-item label="笔试时间">
            <el-date-picker v-model="form.exam_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
          </el-form-item>
          <el-form-item label="时长（分钟）">
            <el-input-number v-model="form.duration_minutes" :min="10" :max="600" :step="10" style="width: 100%" />
          </el-form-item>
        </div>
        <div class="f-row">
          <el-form-item label="平台">
            <el-select v-model="form.platform" style="width: 100%">
              <el-option v-for="(v, k) in EXAM_PLATFORMS" :key="k" :label="v.label" :value="k" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="form.status" style="width: 100%">
              <el-option v-for="(v, k) in PROGRESS_STATUS" :key="k" :label="v.label" :value="k" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="笔试链接">
          <el-input v-model="form.exam_link" placeholder="https://…" />
        </el-form-item>
        <div class="f-row">
          <el-form-item label="账号">
            <el-input v-model="form.account" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" show-password placeholder="本地明文存储（个人使用）" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <!-- 复盘 -->
    <el-dialog v-model="reviewVisible" :title="`笔试复盘 · ${editingPlatform || ''}`" width="580px" destroy-on-close>
      <el-form :model="reviewForm" label-position="top">
        <el-form-item label="是否通过">
          <el-radio-group v-model="reviewForm.passed">
            <el-radio-button :value="true">通过</el-radio-button>
            <el-radio-button :value="false">未通过</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <div class="f-row">
          <el-form-item label="通过率 / 分数">
            <el-input v-model="reviewForm.score" placeholder="如 通过率 60% / 得分 78" />
          </el-form-item>
          <el-form-item label="考点标签">
            <el-input v-model="reviewForm.key_points" placeholder="逗号分隔，如 排序, 二分" />
          </el-form-item>
        </div>
        <el-form-item label="笔试题目记录">
          <el-input v-model="reviewForm.questions" type="textarea" :rows="3" placeholder="还记得的题目，尽量回忆原题…" />
        </el-form-item>
        <el-form-item label="错题与正确答案">
          <el-input v-model="reviewForm.wrong_questions" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="整体复盘总结">
          <el-input v-model="reviewForm.summary" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button type="primary" :loading="reviewSaving" @click="saveReview">保存复盘</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import {
  createExam,
  deleteExam,
  getExamReview,
  listApplications,
  listExams,
  saveExamReview,
  updateExam,
} from '@/api'
import type { Exam, ExamReview } from '@/types'
import { EXAM_PLATFORMS, PROGRESS_STATUS, labelOf } from '@/constants'
import { fmtDate, fmtDateTime } from '@/utils/format'
import { safeHttpUrl } from '@/utils/download'
import type { Application } from '@/types'

const route = useRoute()
const router = useRouter()

const items = ref<Exam[]>([])
const loading = ref(false)
const filterStatus = ref('')
const filterPlatform = ref('')
const appOptions = ref<Application[]>([])
const reviews = ref(new Map<number, ExamReview>())
const showPwd = ref(new Set<number>())

const appMap = computed(() => {
  const m = new Map<number, string>()
  for (const a of appOptions.value) m.set(a.id, `${a.company} · ${a.position}`)
  return m
})
const appOf = (id: number | null) => (id == null ? '' : appMap.value.get(id) ?? `投递 #${id}`)
const timePart = (iso: string) => fmtDateTime(iso).slice(11)

async function load() {
  loading.value = true
  try {
    items.value = await listExams({ status: filterStatus.value || undefined, application_id: undefined })
    if (filterPlatform.value) items.value = items.value.filter((e) => e.platform === filterPlatform.value)
    for (const e of items.value) {
      if (e.status === 'done' && !reviews.value.has(e.id)) {
        getExamReview(e.id).then((r) => {
          if (r) reviews.value.set(e.id, r)
        })
      }
    }
  } finally {
    loading.value = false
  }
}

function togglePwd(id: number) {
  const next = new Set(showPwd.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  showPwd.value = next
}
function goApp(e: Exam) {
  if (e.application_id != null) router.push({ path: '/applications', query: { focus: e.application_id } })
}

/* ---- 表单 ---- */
const formVisible = ref(false)
const editing = ref<Exam | null>(null)
const saving = ref(false)
const form = reactive<Record<string, unknown>>({
  application_id: null,
  exam_time: null,
  platform: '',
  exam_link: '',
  account: '',
  password: '',
  duration_minutes: null,
  status: 'upcoming',
})

function openCreate() {
  editing.value = null
  Object.assign(form, {
    application_id: null,
    exam_time: null,
    platform: 'nowcoder',
    exam_link: '',
    account: '',
    password: '',
    duration_minutes: 90,
    status: 'upcoming',
  })
  formVisible.value = true
}
function openEdit(e: Exam) {
  editing.value = e
  Object.assign(form, {
    application_id: e.application_id,
    exam_time: e.exam_time,
    platform: e.platform ?? '',
    exam_link: e.exam_link ?? '',
    account: e.account ?? '',
    password: e.password ?? '',
    duration_minutes: e.duration_minutes,
    status: e.status,
  })
  formVisible.value = true
}
async function save() {
  saving.value = true
  try {
    if (editing.value) await updateExam(editing.value.id, form)
    else await createExam(form)
    ElMessage.success('已保存')
    formVisible.value = false
    load()
  } finally {
    saving.value = false
  }
}
async function markDone(e: Exam) {
  await updateExam(e.id, { status: 'done' })
  ElMessage.success('已标记完成，别忘了写复盘')
  load()
}
async function remove(e: Exam) {
  await ElMessageBox.confirm('确定删除这场笔试？关联的复盘记录会一并删除。', '删除笔试', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteExam(e.id)
  ElMessage.success('已删除')
  load()
}

/* ---- 复盘 ---- */
const reviewVisible = ref(false)
const reviewSaving = ref(false)
const reviewExamId = ref<number | null>(null)
const editingPlatform = ref('')
const reviewForm = reactive<Record<string, unknown>>({
  passed: null,
  score: '',
  questions: '',
  wrong_questions: '',
  key_points: '',
  summary: '',
})

async function openReview(e: Exam) {
  reviewExamId.value = e.id
  editingPlatform.value = labelOf(EXAM_PLATFORMS, e.platform)
  const existing = reviews.value.get(e.id)
  Object.assign(reviewForm, {
    passed: existing?.passed ?? null,
    score: existing?.score ?? '',
    questions: existing?.questions ?? '',
    wrong_questions: existing?.wrong_questions ?? '',
    key_points: (existing?.key_points ?? []).join(', '),
    summary: existing?.summary ?? '',
  })
  reviewVisible.value = true
}
async function saveReview() {
  if (reviewExamId.value == null) return
  reviewSaving.value = true
  try {
    const keyPoints = String(reviewForm.key_points || '')
      .split(/[,，、]/)
      .map((s) => s.trim())
      .filter(Boolean)
    const saved = await saveExamReview(reviewExamId.value, {
      passed: reviewForm.passed ?? undefined,
      score: String(reviewForm.score || '') || undefined,
      questions: String(reviewForm.questions || '') || undefined,
      wrong_questions: String(reviewForm.wrong_questions || '') || undefined,
      key_points: keyPoints.length ? keyPoints : undefined,
      summary: String(reviewForm.summary || '') || undefined,
    })
    reviews.value.set(reviewExamId.value, saved)
    ElMessage.success('复盘已保存')
    reviewVisible.value = false
  } finally {
    reviewSaving.value = false
  }
}

/* 深链：?focus=id 打开复盘；?new=1&application_id=X 新建 */
watch(
  () => route.query,
  (q) => {
    if (q.new === '1' && q.application_id) {
      openCreate()
      form.application_id = Number(q.application_id)
      router.replace({ query: {} })
    } else if (q.focus && typeof q.focus === 'string') {
      const id = Number(q.focus)
      const found = items.value.find((e) => e.id === id)
      if (found) openReview(found)
      else {
        listExams().then((all) => {
          const e = all.find((x) => x.id === id)
          if (e) {
            items.value = all
            openReview(e)
          }
        })
      }
      router.replace({ query: {} })
    }
  },
  { immediate: true },
)

onMounted(async () => {
  load()
  try {
    const apps = await listApplications({ page_size: 100 })
    appOptions.value = apps.items
  } catch {
    /* 忽略 */
  }
})
</script>

<style scoped>
.filter-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 13px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--surface);
  color: var(--ink-2);
  font-size: 12.5px;
  font-family: inherit;
  cursor: pointer;
}
.chip.active {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: var(--accent-strong);
  font-weight: 600;
}
.p-select {
  width: 130px;
  margin-left: auto;
}
@media (max-width: 860px) {
  .p-select {
    margin-left: 0;
    width: 100%;
  }
}

.list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.exam {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px 18px;
}
.e-left {
  display: flex;
  gap: 16px;
  flex: 1;
  min-width: 0;
}
.e-date {
  font-size: 13px;
  font-weight: 600;
  color: var(--ink);
}
.e-time {
  font-size: 17px;
  font-weight: 700;
  color: var(--accent-strong);
  letter-spacing: -0.02em;
  margin-top: 2px;
}
.e-mid {
  flex: 1;
  min-width: 0;
}
.e-top {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.e-duration {
  font-size: 11.5px;
  color: var(--ink-3);
}
.e-links {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
  font-size: 12.5px;
}
.link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--accent-strong);
  text-decoration: none;
  max-width: 100%;
}
.l-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.cred {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--ink-2);
}
.pwd {
  font-family: var(--font-mono);
}
.eye {
  border: none;
  background: transparent;
  color: var(--ink-3);
  cursor: pointer;
  display: inline-flex;
  padding: 0;
}
.e-app {
  margin-top: 8px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.app-link {
  border: none;
  background: none;
  padding: 0;
  color: var(--accent-strong);
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
  font-weight: 550;
}
.e-review-summary {
  margin-top: 8px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--ok);
  background: var(--ok-soft);
  padding: 4px 10px;
  border-radius: 7px;
}
.e-ops {
  display: flex;
  gap: 2px;
  flex-shrink: 0;
}
.op {
  width: 30px;
  height: 30px;
  border: none;
  background: transparent;
  border-radius: 8px;
  color: var(--ink-3);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.op:hover {
  color: var(--accent-strong);
  background: var(--accent-soft);
}
.op.active {
  color: var(--accent-strong);
}
.op.danger:hover {
  color: var(--danger);
  background: var(--danger-soft);
}
.op:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.f-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 14px;
}
@media (max-width: 640px) {
  .f-row {
    grid-template-columns: 1fr;
  }
  .e-left {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
