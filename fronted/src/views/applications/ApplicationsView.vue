<template>
  <div class="page">
    <PageHeader
      kicker="MODULE 02 · 投递全流程"
      title="投递管理"
      desc="逐条录入投递并流转状态（待投递 → 已投递 → 简历筛选 → 笔试/面试 → Offer），全程留痕。"
    >
      <template #actions>
        <el-button type="primary" @click="openCreate"><el-icon><Plus /></el-icon>&nbsp;新增投递</el-button>
      </template>
    </PageHeader>

    <!-- 筛选 -->
    <div class="filter-bar panel">
      <el-input v-model="filters.keyword" placeholder="公司 / 岗位 / 备注" clearable :prefix-icon="Search" class="f-keyword" @input="onSearch" />
      <el-select v-model="filters.status" placeholder="全部状态" clearable class="f-select" @change="load(1)">
        <el-option v-for="(v, k) in APPLICATION_STATUS" :key="k" :label="v.label" :value="k" />
      </el-select>
      <el-select v-model="filters.channel" placeholder="全部渠道" clearable class="f-select" @change="load(1)">
        <el-option v-for="(v, k) in APPLICATION_CHANNELS" :key="k" :label="v.label" :value="k" />
      </el-select>
      <el-select v-model="filters.job_type_id" placeholder="全部岗位类型" clearable class="f-select" @change="load(1)">
        <el-option v-for="jt in jobTypes" :key="jt.id" :label="jt.name" :value="jt.id" />
      </el-select>
      <span class="f-total mono">共 {{ total }} 条</span>
    </div>

    <!-- 表格 -->
    <el-skeleton v-if="loading" :rows="8" animated class="panel" style="padding: 20px" />
    <EmptyState
      v-else-if="!items.length"
      icon="Promotion"
      title="还没有投递记录"
      desc="新增第一条投递，让每一次申请都有迹可循——从待投递开始流转。"
    >
      <template #action>
        <el-button type="primary" @click="openCreate">新增投递</el-button>
      </template>
    </EmptyState>

    <div v-else class="panel table-wrap">
      <el-table :data="items" class="app-table" @row-click="openDetail">
        <el-table-column label="公司 / 岗位" min-width="200">
          <template #default="{ row }">
            <div class="cell-company">
              <span class="cname">{{ row.company }}</span>
              <span class="cpos">{{ row.position }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="岗位类型" width="110">
          <template #default="{ row }">
            <span v-if="row.job_type_name" class="jt-chip">
              <span class="dot" :style="{ background: jtColor(row.job_type_id) }" />
              {{ row.job_type_name }}
            </span>
            <span v-else class="muted sep">—</span>
          </template>
        </el-table-column>
        <el-table-column label="城市" width="90">
          <template #default="{ row }">
            <span :class="{ muted: !row.city }">{{ row.city || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="薪资" width="110">
          <template #default="{ row }">
            <span class="mono salary">{{ fmtSalary(row.salary_min, row.salary_max, row.salary_currency) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="渠道" width="100">
          <template #default="{ row }">
            <span :class="{ muted: !row.channel }">{{ row.channel ? labelOf(APPLICATION_CHANNELS, row.channel) : '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="投递时间" width="140">
          <template #default="{ row }">
            <span class="mono muted sm">{{ fmtDate(row.apply_time) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <StatusTag :dict="APPLICATION_STATUS" :value="row.status" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <div class="row-ops" @click.stop>
              <el-tooltip content="流转状态" placement="top">
                <button class="op" :disabled="isTerminal(row.status)" @click="openStatus(row)">
                  <el-icon><Switch /></el-icon>
                </button>
              </el-tooltip>
              <el-tooltip content="编辑" placement="top">
                <button class="op" @click="openEdit(row)"><el-icon><Edit /></el-icon></button>
              </el-tooltip>
              <el-tooltip content="删除" placement="top">
                <button class="op danger" @click="remove(row)"><el-icon><Delete /></el-icon></button>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
        <template #empty>
          <EmptyState icon="Search" title="没有匹配的投递" desc="换个筛选条件试试。" />
        </template>
      </el-table>

      <div class="pager">
        <el-pagination
          layout="prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :current-page="page"
          @current-change="load"
        />
      </div>
    </div>

    <!-- 表单 -->
    <el-dialog v-model="formVisible" :title="editing ? '编辑投递' : '新增投递'" width="680px" destroy-on-close top="4vh">
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <div class="form-grid">
          <el-form-item label="公司" prop="company">
            <el-input v-model="form.company" maxlength="200" placeholder="公司全称" @blur="onCompanyBlur" />
          </el-form-item>
          <el-form-item label="岗位" prop="position">
            <el-input v-model="form.position" maxlength="200" placeholder="如 后端开发工程师" />
          </el-form-item>
          <el-form-item label="城市">
            <el-input v-model="form.city" maxlength="100" />
          </el-form-item>
          <el-form-item label="岗位类型">
            <el-select v-model="form.job_type_id" clearable style="width: 100%" placeholder="关联岗位类型">
              <el-option v-for="jt in jobTypes" :key="jt.id" :label="jt.name" :value="jt.id" />
            </el-select>
          </el-form-item>
        </div>

        <el-alert
          v-if="blacklistHits > 0"
          :title="`「${form.company}」在避雷库中有 ${blacklistHits} 条记录，投递前建议先查看。`"
          type="warning"
          :closable="false"
          show-icon
          class="bl-warn"
        />

        <div class="form-grid">
          <el-form-item label="薪资下限（K/月）">
            <el-input-number v-model="form.salary_min" :min="0" :max="999" controls-position="right" style="width: 100%" />
          </el-form-item>
          <el-form-item label="薪资上限（K/月）">
            <el-input-number v-model="form.salary_max" :min="0" :max="999" controls-position="right" style="width: 100%" />
          </el-form-item>
          <el-form-item label="投递渠道">
            <el-select v-model="form.channel" clearable style="width: 100%">
              <el-option v-for="(v, k) in APPLICATION_CHANNELS" :key="k" :label="v.label" :value="k" />
            </el-select>
          </el-form-item>
          <el-form-item label="投递时间">
            <el-date-picker v-model="form.apply_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
          </el-form-item>
          <el-form-item label="使用简历版本">
            <el-select v-model="form.resume_version_id" clearable filterable style="width: 100%" placeholder="默认版本自动带出">
              <el-option
                v-for="r in resumesForType"
                :key="r.id"
                :label="`${r.version_name}${r.is_default ? '（默认）' : ''}${r.job_type_name ? ' · ' + r.job_type_name : ''}`"
                :value="r.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item v-if="!editing" label="初始状态">
            <el-select v-model="form.status" style="width: 100%">
              <el-option v-for="(v, k) in APPLICATION_STATUS" :key="k" :label="v.label" :value="k" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="投递 / 职位链接">
          <el-input v-model="form.source_url" placeholder="https://…" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="内推人、JD 关键信息、注意事项…" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <!-- 状态流转 -->
    <el-dialog v-model="statusVisible" title="流转投递状态" width="460px" destroy-on-close>
      <div class="status-flow">
        <div class="flow-current">
          <span class="muted">当前状态</span>
          <StatusTag :dict="APPLICATION_STATUS" :value="currentApp?.status" />
        </div>
        <div class="flow-next">
          <span class="muted">流转到</span>
          <el-select v-model="nextStatus" placeholder="选择下一状态" style="width: 100%">
            <el-option v-for="s in nextOptions" :key="s" :label="labelOf(APPLICATION_STATUS, s)" :value="s" />
          </el-select>
          <div v-if="!nextOptions.length" class="flow-fail">
            当前状态不可再流转<el-icon><CircleClose /></el-icon>
          </div>
        </div>
        <el-form-item label="备注（选填）">
          <el-input v-model="statusNote" type="textarea" :rows="2" placeholder="如「笔试挂，算法题没做出来」" />
        </el-form-item>
      </div>
      <template #footer>
        <el-button @click="statusVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!nextStatus" :loading="statusSaving" @click="saveStatus">确认流转</el-button>
      </template>
    </el-dialog>

    <!-- 详情抽屉 -->
    <ApplicationDetailDrawer v-model="detailVisible" :application-id="detailId" :reload-key="reloadKey" @changed="load(page)" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { useDictStore } from '@/stores/dict'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import ApplicationDetailDrawer from './ApplicationDetailDrawer.vue'
import {
  changeApplicationStatus,
  checkBlacklist,
  createApplication,
  deleteApplication,
  listApplications,
  listResumes,
  updateApplication,
} from '@/api'
import type { Application } from '@/types'
import { APPLICATION_CHANNELS, APPLICATION_STATUS, STATUS_TRANSITIONS, labelOf } from '@/constants'
import { fmtDate, fmtSalary } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const dict = useDictStore()
const jobTypes = computed(() => dict.jobTypes)

const items = ref<Application[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 12
const loading = ref(false)

const filters = reactive({ keyword: '', status: '', channel: '', job_type_id: null as number | null })
let searchTimer: ReturnType<typeof setTimeout> | null = null

function onSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => load(1), 320)
}

async function load(p = page.value) {
  page.value = p
  loading.value = true
  try {
    const data = await listApplications({
      keyword: filters.keyword || undefined,
      status: filters.status || undefined,
      channel: filters.channel || undefined,
      job_type_id: filters.job_type_id ?? undefined,
      page: p,
      page_size: pageSize,
    })
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

const jtColor = (id: number | null) => dict.jobTypeColor(id)

const isTerminal = (status: string) => !(STATUS_TRANSITIONS[status]?.length)

/* ---- 表单 ---- */
const formVisible = ref(false)
const editing = ref<Application | null>(null)
const saving = ref(false)
const formRef = ref<FormInstance>()
const blacklistHits = ref(0)
const resumes = ref<Awaited<ReturnType<typeof listResumes>>>([])

const form = reactive<Record<string, unknown>>({
  company: '',
  position: '',
  city: '',
  salary_min: null,
  salary_max: null,
  channel: null,
  apply_time: null,
  resume_version_id: null,
  job_type_id: null,
  status: 'pending',
  source_url: '',
  remark: '',
})

const resumesForType = computed(() => {
  const typeId = form.job_type_id
  return typeId == null ? resumes.value : resumes.value.filter((r) => r.job_type_id === typeId)
})

const rules: FormRules = {
  company: [{ required: true, message: '请填写公司', trigger: 'blur' }],
  position: [{ required: true, message: '请填写岗位', trigger: 'blur' }],
}

function openCreate() {
  editing.value = null
  blacklistHits.value = 0
  Object.assign(form, {
    company: '',
    position: '',
    city: '',
    salary_min: null,
    salary_max: null,
    channel: null,
    apply_time: null,
    resume_version_id: null,
    job_type_id: null,
    status: 'pending',
    source_url: '',
    remark: '',
  })
  formVisible.value = true
}
function openEdit(a: Application) {
  editing.value = a
  blacklistHits.value = 0
  Object.assign(form, {
    company: a.company,
    position: a.position,
    city: a.city ?? '',
    salary_min: a.salary_min,
    salary_max: a.salary_max,
    channel: a.channel,
    apply_time: a.apply_time,
    resume_version_id: a.resume_version_id,
    job_type_id: a.job_type_id,
    status: a.status,
    source_url: a.source_url ?? '',
    remark: a.remark ?? '',
  })
  formVisible.value = true
}
async function onCompanyBlur() {
  const name = String(form.company).trim()
  if (!name || editing.value?.company === name) return
  try {
    const res = await checkBlacklist(name)
    blacklistHits.value = res.count
  } catch {
    blacklistHits.value = 0
  }
}
async function save() {
  await formRef.value?.validate()
  saving.value = true
  try {
    const data: Record<string, unknown> = { ...form }
    if (editing.value) {
      delete data.status
      await updateApplication(editing.value.id, data)
    } else {
      await createApplication(data)
    }
    ElMessage.success('已保存')
    formVisible.value = false
    load(editing.value ? page.value : 1)
    if (editing.value) {
      detailVisible.value = true
      detailId.value = editing.value.id
    }
  } catch {
    /* 拦截器提示 */
  } finally {
    saving.value = false
  }
}
async function remove(a: Application) {
  await ElMessageBox.confirm(`确定删除「${a.company} · ${a.position}」的投递记录？关联的笔面试、Offer 将一并删除。`, '删除投递', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteApplication(a.id)
  ElMessage.success('已删除')
  load(page.value)
}

/* ---- 状态流转 ---- */
const statusVisible = ref(false)
const statusSaving = ref(false)
const currentApp = ref<Application | null>(null)
const nextStatus = ref('')
const statusNote = ref('')

const nextOptions = computed(() => (currentApp.value ? (STATUS_TRANSITIONS[currentApp.value.status] ?? []) : []))

function openStatus(a: Application) {
  currentApp.value = a
  nextStatus.value = ''
  statusNote.value = ''
  statusVisible.value = true
}
async function saveStatus() {
  if (!currentApp.value || !nextStatus.value) return
  statusSaving.value = true
  try {
    await changeApplicationStatus(currentApp.value.id, { to_status: nextStatus.value, note: statusNote.value || undefined })
    ElMessage.success(`已流转为「${labelOf(APPLICATION_STATUS, nextStatus.value)}」`)
    statusVisible.value = false
    load(page.value)
    reloadKey.value++
  } catch {
    /* 409 已提示 */
  } finally {
    statusSaving.value = false
  }
}

/* ---- 详情抽屉 ---- */
const detailVisible = ref(false)
const detailId = ref<number | null>(null)
const reloadKey = ref(0)
function openDetail(a: Application) {
  detailId.value = a.id
  reloadKey.value++
  detailVisible.value = true
}

/* 深链：?focus=id（从看板 / 笔面试视图跳转而来） */
watch(
  () => route.query.focus,
  (focus) => {
    if (focus && typeof focus === 'string') {
      const id = Number(focus)
      if (id > 0) {
        detailId.value = id
        reloadKey.value++
        detailVisible.value = true
        router.replace({ query: {} })
      }
    }
  },
  { immediate: true },
)

onMounted(async () => {
  await dict.ensureJobTypes()
  load(1)
  listResumes().then((rows) => (resumes.value = rows))
})
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.f-keyword {
  width: 220px;
}
.f-select {
  width: 140px;
}
.f-total {
  margin-left: auto;
  font-size: 12px;
  color: var(--ink-3);
}
@media (max-width: 860px) {
  .f-keyword,
  .f-select {
    width: 100%;
  }
  .f-total {
    margin-left: 0;
  }
}

.table-wrap {
  overflow: hidden;
}
.cell-company {
  display: flex;
  flex-direction: column;
  line-height: 1.45;
}
.cname {
  font-weight: 650;
  color: var(--ink);
}
.cpos {
  font-size: 12px;
  color: var(--ink-3);
}
.jt-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--ink-2);
}
.salary {
  font-size: 12.5px;
  color: var(--ink-2);
}
.sm {
  font-size: 12px;
}
.row-ops {
  display: flex;
  gap: 2px;
}
.op {
  width: 27px;
  height: 27px;
  border: none;
  background: transparent;
  border-radius: 7px;
  color: var(--ink-3);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.18s;
}
.op:hover {
  color: var(--accent-strong);
  background: var(--accent-soft);
}
.op.danger:hover {
  color: var(--danger);
  background: var(--danger-soft);
}
.op:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.pager {
  display: flex;
  justify-content: flex-end;
  padding: 14px 16px;
  border-top: 1px solid var(--line);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 14px;
}
@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
.bl-warn {
  margin-bottom: 16px;
  border-radius: 8px;
}

.status-flow {
  padding: 6px 2px;
}
.flow-current,
.flow-next {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}
.flow-fail {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--ink-3);
  font-size: 12.5px;
}
</style>