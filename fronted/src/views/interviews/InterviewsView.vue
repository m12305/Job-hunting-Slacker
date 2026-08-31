<template>
  <div class="page">
    <PageHeader
      kicker="MODULE 03 · 笔试面试"
      title="面试管理"
      desc="按轮次记录面试安排，沉淀问答复盘与结果，录音存档；同一投递的多轮面试按时间线组织。"
    >
      <template #actions>
        <el-button type="primary" @click="openCreate"><el-icon><Plus /></el-icon>&nbsp;新增面试</el-button>
      </template>
    </PageHeader>

    <div class="filter-row">
      <el-select v-model="filterRound" placeholder="全部轮次" clearable class="r-select" @change="load()">
        <el-option v-for="(v, k) in INTERVIEW_ROUNDS" :key="k" :label="v.label" :value="k" />
      </el-select>
      <el-select v-model="filterStatus" placeholder="全部状态" clearable class="r-select" @change="load()">
        <el-option v-for="(v, k) in PROGRESS_STATUS" :key="k" :label="v.label" :value="k" />
      </el-select>
      <span class="f-hint muted">同一投递下的多轮面试会按时间线聚合展示。</span>
    </div>

    <el-skeleton v-if="loading" :rows="6" animated class="panel" style="padding: 20px" />
    <EmptyState
      v-else-if="!groups.length"
      icon="ChatLineSquare"
      title="还没有面试记录"
      desc="投递进入「面试」阶段后，在这里登记每一轮面试的时间与链接。"
    >
      <template #action>
        <el-button type="primary" @click="openCreate">新增面试</el-button>
      </template>
    </EmptyState>

    <div v-else class="groups">
      <section v-for="g in groups" :key="g.key" class="group panel">
        <div class="g-head">
          <div class="g-app">
            <el-icon><OfficeBuilding /></el-icon>
            <span class="g-company">{{ g.appLabel }}</span>
            <button v-if="g.applicationId != null" class="g-jump" @click="goApp(g.applicationId)">
              投递详情 <el-icon><ArrowRight /></el-icon>
            </button>
          </div>
          <span class="mono g-note">{{ g.items.length }} 轮</span>
        </div>

        <div class="g-timeline">
          <div
            v-for="(i, idx) in g.items"
            :key="i.id"
            class="g-row"
            :class="{ last: idx === g.items.length - 1 }"
          >
            <div class="g-track">
              <span class="g-dot" :class="i.status" />
              <span v-if="idx < g.items.length - 1" class="g-line" />
            </div>
            <article class="interview" :class="{ done: i.status === 'done' }">
              <div class="i-head">
                <StatusTag :dict="INTERVIEW_ROUNDS" :value="i.round" />
                <StatusTag :dict="PROGRESS_STATUS" :value="i.status" />
                <el-tag v-if="results.get(i.id)" :type="results.get(i.id)?.result === 'passed' ? 'success' : 'danger'" size="small" effect="plain">
                  {{ results.get(i.id)?.result === 'passed' ? '通过' : '挂掉' }}
                </el-tag>
                <span class="mono i-time">{{ i.interview_time ? fmtDateTime(i.interview_time) : '时间待定' }}</span>
              </div>

              <div class="i-body">
                <div v-if="i.interview_link" class="i-link">
                  <a :href="i.interview_link" target="_blank" rel="noopener">
                    <el-icon><Link /></el-icon>{{ i.interview_link }}
                  </a>
                </div>

                <div v-if="prepSummary(i) && !i.self_intro" class="i-prep">
                  <el-icon><Checked /></el-icon>
                  准备清单 {{ prepSummary(i) }}
                </div>

                <div v-if="i.self_intro" class="i-intro">
                  <div class="i-label">自我介绍脚本</div>
                  <p>{{ i.self_intro }}</p>
                </div>

                <div v-if="prepSummary(i)" class="i-prep">
                  <div class="i-label">准备清单 （{{ prepSummary(i) }}）</div>
                </div>
              </div>

              <div class="i-ops">
                <el-button size="small" :type="qaCount(i.id) ? 'primary' : 'default'" plain @click="openQa(i)">
                  <el-icon><ChatDotRound /></el-icon>&nbsp;问答复盘{{ qaCount(i.id) ? `（${qaCount(i.id)}）` : '' }}
                </el-button>
                <el-button size="small" :type="results.get(i.id) ? 'success' : 'default'" plain @click="openResult(i)">
                  <el-icon><Trophy /></el-icon>&nbsp;面试结果
                </el-button>
                <el-button size="small" :disabled="i.status !== 'upcoming'" @click="markDone(i)">
                  <el-icon><CircleCheck /></el-icon>&nbsp;标记完成
                </el-button>
                <el-tooltip content="编辑" placement="top">
                  <button class="op" @click="openEdit(i)"><el-icon><Edit /></el-icon></button>
                </el-tooltip>
                <el-tooltip content="删除" placement="top">
                  <button class="op danger" @click="remove(i)"><el-icon><Delete /></el-icon></button>
                </el-tooltip>
              </div>
            </article>
          </div>
        </div>
      </section>
    </div>

    <!-- 表单 -->
    <el-dialog v-model="formVisible" :title="editing ? '编辑面试' : '新增面试'" width="620px" destroy-on-close top="4vh">
      <el-form :model="form" label-position="top">
        <div class="f-row">
          <el-form-item label="关联投递">
            <el-select v-model="form.application_id" clearable filterable style="width: 100%" placeholder="选择投递记录">
              <el-option v-for="a in appOptions" :key="a.id" :label="`${a.company} · ${a.position}`" :value="a.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="轮次">
            <el-select v-model="form.round" style="width: 100%">
              <el-option v-for="(v, k) in INTERVIEW_ROUNDS" :key="k" :label="v.label" :value="k" />
            </el-select>
          </el-form-item>
        </div>
        <div class="f-row">
          <el-form-item label="面试时间">
            <el-date-picker v-model="form.interview_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="form.status" style="width: 100%">
              <el-option v-for="(v, k) in PROGRESS_STATUS" :key="k" :label="v.label" :value="k" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="面试链接（视频会议）">
          <el-input v-model="form.interview_link" placeholder="https://…" />
        </el-form-item>
        <el-form-item label="自我介绍脚本">
          <el-input v-model="form.self_intro" type="textarea" :rows="3" placeholder="可先在话术库准备，再粘贴到这里" />
        </el-form-item>
        <el-form-item label="准备清单">
          <div class="prep-editor">
            <div v-for="(item, i) in prepItems" :key="i" class="prep-line">
              <el-checkbox v-model="item.done" />
              <el-input v-model="item.label" placeholder="准备项" size="small" />
              <button class="op danger" @click="prepItems.splice(i, 1)"><el-icon><Delete /></el-icon></button>
            </div>
            <div v-if="!prepItems.length" class="prep-empty muted">暂无准备项，点击下方按钮添加</div>
            <el-button size="small" text type="primary" @click="prepItems.push({ label: '', done: false })">
              <el-icon><Plus /></el-icon>&nbsp;添加准备项
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <!-- 问答复盘抽屉 -->
    <InterviewQaDrawer v-model="qaVisible" :interview="qaTarget" @changed="reloadQaCounts" />

    <!-- 面试结果 -->
    <el-dialog v-model="resultVisible" title="面试结果记录" width="540px" destroy-on-close>
      <el-form :model="resultForm" label-position="top">
        <el-form-item label="结果" required>
          <el-radio-group v-model="resultForm.result">
            <el-radio-button value="passed">通过</el-radio-button>
            <el-radio-button value="failed">挂掉</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="resultForm.result === 'failed'" label="挂掉原因（复盘）">
          <el-input v-model="resultForm.fail_reason" type="textarea" :rows="3" placeholder="哪一环节、哪些问题没答好…" />
        </el-form-item>
        <el-form-item label="整体总结">
          <el-input v-model="resultForm.summary" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="面试录音">
          <div class="audio-row">
            <el-button size="small" @click="pickAudio"><el-icon><Upload /></el-icon>&nbsp;上传录音</el-button>
            <input ref="audioInput" type="file" accept=".mp3,.m4a,.wav" class="hidden" @change="onAudioPick" />
            <span v-if="currentAudio" class="audio-name mono">{{ currentAudio }}</span>
            <span v-else class="muted">支持 mp3 / m4a / wav，本地存档</span>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resultVisible = false">取消</el-button>
        <el-button type="primary" :loading="resultSaving" @click="saveResult">保存结果</el-button>
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
import InterviewQaDrawer from './InterviewQaDrawer.vue'
import {
  createInterview,
  deleteInterview,
  getInterviewResult,
  listApplications,
  listInterviews,
  listInterviewQa,
  saveInterviewResult,
  updateInterview,
  uploadInterviewAudio,
} from '@/api'
import type { Application, Interview, InterviewResult } from '@/types'
import { INTERVIEW_ROUNDS, PROGRESS_STATUS } from '@/constants'
import { fmtDateTime, baseName } from '@/utils/format'

const route = useRoute()
const router = useRouter()

const items = ref<Interview[]>([])
const loading = ref(false)
const filterRound = ref('')
const filterStatus = ref('')
const appOptions = ref<Application[]>([])
const results = ref(new Map<number, InterviewResult>())
const qaCounts = ref(new Map<number, number>())

const appMap = computed(() => {
  const m = new Map<number, string>()
  for (const a of appOptions.value) m.set(a.id, `${a.company} · ${a.position}`)
  return m
})

const groups = computed(() => {
  const g = new Map<string, { key: string; applicationId: number | null; appLabel: string; items: Interview[] }>()
  for (const i of items.value) {
    const key = i.application_id != null ? `app-${i.application_id}` : `none-${i.id}`
    if (!g.has(key)) {
      g.set(key, {
        key,
        applicationId: i.application_id,
        appLabel: i.application_id != null ? (appMap.value.get(i.application_id) ?? `投递 #${i.application_id}`) : '未关联投递',
        items: [],
      })
    }
    g.get(key)!.items.push(i)
  }
  for (const group of g.values()) {
    group.items.sort((a, b) => {
      if (a.interview_time && b.interview_time) return a.interview_time.localeCompare(b.interview_time)
      return a.id - b.id
    })
  }
  return [...g.values()]
})

async function load() {
  loading.value = true
  try {
    items.value = await listInterviews({ round: filterRound.value || undefined, status: filterStatus.value || undefined })
    for (const i of items.value) {
      if (i.status === 'done' && !results.value.has(i.id)) {
        getInterviewResult(i.id).then((r) => {
          if (r) results.value.set(i.id, r)
        })
      }
      if (!qaCounts.value.has(i.id)) {
        listInterviewQa(i.id).then((qa) => qaCounts.value.set(i.id, qa.length))
      }
    }
  } finally {
    loading.value = false
  }
}

const prepSummary = (i: Interview) => {
  const list = i.prep_checklist ?? []
  if (!list.length) return ''
  const done = list.filter((p) => p.done).length
  return `${done}/${list.length}`
}
const qaCount = (id: number) => qaCounts.value.get(id) ?? 0
function reloadQaCounts() {
  for (const i of items.value) listInterviewQa(i.id).then((qa) => qaCounts.value.set(i.id, qa.length))
}
function goApp(id: number) {
  router.push({ path: '/applications', query: { focus: id } })
}

/* ---- 表单 ---- */
const formVisible = ref(false)
const editing = ref<Interview | null>(null)
const saving = ref(false)
const prepItems = ref<{ label: string; done: boolean }[]>([])
const form = reactive<Record<string, unknown>>({
  application_id: null,
  round: 'first',
  interview_time: null,
  interview_link: '',
  self_intro: '',
  status: 'upcoming',
})

function openCreate() {
  editing.value = null
  prepItems.value = [{ label: '熟悉 JD', done: false }, { label: '自我介绍', done: false }]
  Object.assign(form, {
    application_id: null,
    round: 'first',
    interview_time: null,
    interview_link: '',
    self_intro: '',
    status: 'upcoming',
  })
  formVisible.value = true
}
function openEdit(i: Interview) {
  editing.value = i
  prepItems.value = (i.prep_checklist ?? []).map((p) => ({ label: String(p.label ?? ''), done: Boolean(p.done) }))
  if (!prepItems.value.length) prepItems.value = []
  Object.assign(form, {
    application_id: i.application_id,
    round: i.round ?? 'first',
    interview_time: i.interview_time,
    interview_link: i.interview_link ?? '',
    self_intro: i.self_intro ?? '',
    status: i.status,
  })
  formVisible.value = true
}
async function save() {
  saving.value = true
  try {
    const data = {
      ...form,
      prep_checklist: prepItems.value.filter((p) => p.label.trim()),
    }
    if (editing.value) await updateInterview(editing.value.id, data)
    else await createInterview(data)
    ElMessage.success('已保存')
    formVisible.value = false
    load()
  } finally {
    saving.value = false
  }
}
async function markDone(i: Interview) {
  await updateInterview(i.id, { status: 'done' })
  ElMessage.success('已标记完成，记得写问答与结果')
  load()
}
async function remove(i: Interview) {
  await ElMessageBox.confirm('确定删除这场面试？关联的问答与结果会一并删除。', '删除面试', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteInterview(i.id)
  ElMessage.success('已删除')
  load()
}

/* ---- 问答抽屉 ---- */
const qaVisible = ref(false)
const qaTarget = ref<Interview | null>(null)
function openQa(i: Interview) {
  qaTarget.value = i
  qaVisible.value = true
}

/* ---- 结果 ---- */
const resultVisible = ref(false)
const resultSaving = ref(false)
const resultTarget = ref<Interview | null>(null)
const currentAudio = ref('')
const audioInput = ref<HTMLInputElement | null>(null)
const resultForm = reactive<Record<string, unknown>>({
  result: 'passed',
  fail_reason: '',
  summary: '',
})

async function openResult(i: Interview) {
  resultTarget.value = i
  const existing = results.value.get(i.id)
  Object.assign(resultForm, {
    result: existing?.result ?? 'passed',
    fail_reason: existing?.fail_reason ?? '',
    summary: existing?.summary ?? '',
  })
  currentAudio.value = existing?.audio_path ? baseName(existing.audio_path) : ''
  resultVisible.value = true
}
function pickAudio() {
  audioInput.value?.click()
}
async function onAudioPick(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file || !resultTarget.value) return
  try {
    const saved = await uploadInterviewAudio(resultTarget.value.id, file)
    currentAudio.value = baseName(saved.audio_path ?? file.name)
    results.value.set(resultTarget.value.id, saved)
    ElMessage.success('录音已上传')
  } catch {
    /* 已提示 */
  }
}
async function saveResult() {
  if (!resultTarget.value || !resultForm.result) return
  resultSaving.value = true
  try {
    const saved = await saveInterviewResult(resultTarget.value.id, {
      result: resultForm.result,
      fail_reason: String(resultForm.fail_reason || '') || undefined,
      summary: String(resultForm.summary || '') || undefined,
    })
    results.value.set(resultTarget.value.id, saved)
    ElMessage.success('结果已保存')
    resultVisible.value = false
    load()
  } finally {
    resultSaving.value = false
  }
}

/* 深链 */
watch(
  () => route.query,
  (q) => {
    if (q.new === '1' && q.application_id) {
      openCreate()
      form.application_id = Number(q.application_id)
      router.replace({ query: {} })
    } else if (q.focus && typeof q.focus === 'string') {
      const id = Number(q.focus)
      const found = items.value.find((i) => i.id === id)
      if (found) openResult(found)
      else {
        listInterviews().then((all) => {
          const i = all.find((x) => x.id === id)
          if (i) {
            items.value = all
            openResult(i)
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
  align-items: center;
}
.r-select {
  width: 140px;
}
.f-hint {
  font-size: 12px;
  margin-left: auto;
}
@media (max-width: 860px) {
  .f-hint {
    width: 100%;
    margin-left: 0;
  }
}

.groups {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.group {
  padding: 18px 20px;
}
.g-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.g-app {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 13.5px;
  font-weight: 650;
  color: var(--ink);
}
.g-jump {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  border: none;
  background: none;
  color: var(--accent-strong);
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
}
.g-note {
  margin-left: auto;
  font-size: 11.5px;
  color: var(--ink-3);
}

.g-timeline {
  display: flex;
  flex-direction: column;
}
.g-row {
  display: flex;
  gap: 14px;
}
.g-track {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 10px;
  flex-shrink: 0;
}
.g-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--line-strong);
  margin-top: 22px;
  flex-shrink: 0;
}
.g-dot.done {
  background: var(--ok);
}
.g-dot.upcoming {
  background: var(--accent);
}
.g-dot.cancelled {
  background: var(--ink-4);
}
.g-line {
  flex: 1;
  width: 1.5px;
  background: var(--line);
  margin: 4px 0;
}
.g-row.last .g-line {
  display: none;
}

.interview {
  flex: 1;
  min-width: 0;
  padding: 14px 0 18px;
}
.i-head {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.i-time {
  margin-left: auto;
  font-size: 12px;
  color: var(--ink-2);
}
.i-body {
  margin-top: 10px;
  padding: 0 0 0 4px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.i-link a {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
  color: var(--accent-strong);
  text-decoration: none;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.i-prep {
  font-size: 12.5px;
  color: var(--ink-2);
  display: flex;
  align-items: center;
  gap: 6px;
}
.i-intro p {
  margin: 4px 0 0;
  font-size: 12.5px;
  color: var(--ink-2);
  white-space: pre-line;
  line-height: 1.7;
}
.i-label {
  font-size: 11px;
  color: var(--ink-3);
  letter-spacing: 0.06em;
}
.i-ops {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}
.op {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: 7px;
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
.op.danger:hover {
  color: var(--danger);
  background: var(--danger-soft);
}

.f-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 14px;
}
.prep-editor {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.prep-line {
  display: flex;
  align-items: center;
  gap: 8px;
}
.prep-empty {
  font-size: 12px;
}
.audio-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.audio-name {
  font-size: 12px;
  color: var(--ok);
}
.hidden {
  display: none;
}
@media (max-width: 640px) {
  .f-row {
    grid-template-columns: 1fr;
  }
}
</style>