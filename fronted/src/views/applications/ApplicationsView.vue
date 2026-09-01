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
    <div class="filter-panel panel">
      <div class="filter-main">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索公司 / 岗位 / 城市 / 备注"
          clearable
          :prefix-icon="Search"
          class="f-keyword"
          @input="onSearch"
        />
        <el-select v-model="filters.channel" placeholder="全部渠道" clearable class="f-select" @change="load(1)">
          <el-option v-for="(v, k) in APPLICATION_CHANNELS" :key="k" :label="v.label" :value="k" />
        </el-select>
        <el-select v-model="filters.job_type_id" placeholder="全部岗位类型" clearable class="f-select wide" @change="load(1)">
          <el-option v-for="jt in jobTypes" :key="jt.id" :label="jt.name" :value="jt.id" />
        </el-select>
        <el-select v-model="sortValue" class="f-select wide" aria-label="投递记录排序" @change="onSortChange">
          <el-option label="投递时间从近到远" value="apply_time:desc" />
          <el-option label="投递时间从远到近" value="apply_time:asc" />
          <el-option label="最近更新" value="updated_at:desc" />
          <el-option label="公司名称" value="company:asc" />
        </el-select>
        <el-button v-if="hasFilters" class="reset-btn" @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon>&nbsp;重置
        </el-button>
        <span class="f-total mono">{{ total }} 条结果</span>
      </div>

      <div class="filter-section" role="group" aria-label="按投递状态筛选">
        <span class="filter-label">进度</span>
        <div class="status-chips">
          <button
            v-for="(meta, key) in APPLICATION_STATUS_GROUPS"
            :key="key"
            type="button"
            class="status-chip"
            :class="{ active: filters.status_group === key }"
            :aria-pressed="filters.status_group === key"
            @click="setStatusGroup(key)"
          >
            <span class="status-chip-main">{{ meta.label }} <b class="mono">{{ facets[key] ?? 0 }}</b></span>
            <span class="status-chip-sub">{{ meta.subtitle }}</span>
          </button>
        </div>
      </div>

      <div class="filter-section date-section" role="group" aria-label="按投递时间筛选">
        <span class="filter-label">投递时间</span>
        <div class="date-chips">
          <button
            v-for="option in DATE_FILTERS"
            :key="option.value"
            type="button"
            class="date-chip-filter"
            :class="{ active: filters.apply_time_range === option.value && !customDateRange }"
            :aria-pressed="filters.apply_time_range === option.value && !customDateRange"
            @click="setDateRange(option.value)"
          >
            {{ option.label }}
          </button>
          <el-date-picker
            v-model="customDateRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            unlink-panels
            class="custom-date"
            @change="onCustomDateChange"
          />
        </div>
      </div>
    </div>

    <!-- 表格 -->
    <el-alert
      v-if="loadError"
      :title="loadError"
      type="error"
      :closable="false"
      show-icon
      class="load-error"
    >
      <template #default><el-button size="small" @click="load(page)">重新加载</el-button></template>
    </el-alert>
    <el-skeleton v-if="loading" :rows="8" animated class="panel" style="padding: 20px" />
    <EmptyState
      v-else-if="!items.length"
      icon="Promotion"
      :title="hasFilters ? '没有匹配的投递' : '还没有投递记录'"
      :desc="hasFilters ? '换个公司、状态或时间范围试试。' : '新增第一条投递，让每一次申请都有迹可循。'"
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
                <button type="button" class="op" aria-label="流转状态" :disabled="isTerminal(row.status)" @click="openStatus(row)">
                  <el-icon><Switch /></el-icon>
                </button>
              </el-tooltip>
              <el-tooltip content="编辑" placement="top">
                <button type="button" class="op" aria-label="编辑投递" @click="openEdit(row)"><el-icon><Edit /></el-icon></button>
              </el-tooltip>
              <el-tooltip content="删除" placement="top">
                <button type="button" class="op danger" aria-label="删除投递" @click="remove(row)"><el-icon><Delete /></el-icon></button>
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
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          :page-size="pageSize"
          :page-sizes="[12, 24, 48]"
          :current-page="page"
          @current-change="load"
          @size-change="onPageSizeChange"
        />
      </div>
    </div>

    <!-- 表单 -->
    <el-dialog
      v-model="formVisible"
      :title="editing ? '编辑投递' : '新增投递'"
      width="min(680px, calc(100vw - 24px))"
      class="viewport-dialog"
      append-to-body
      destroy-on-close
      top="2vh"
    >
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
          <el-form-item v-if="!editing && form.status === 'ended'" label="结束原因" required>
            <el-select v-model="form.close_reason" style="width: 100%" placeholder="选择结束原因">
              <el-option v-for="(v, k) in APPLICATION_CLOSE_REASONS" :key="k" :label="v.label" :value="k" />
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
    <el-dialog v-model="statusVisible" title="流转投递状态" width="min(460px, calc(100vw - 24px))" destroy-on-close>
      <div class="status-flow">
        <div class="flow-current">
          <span class="muted">当前状态</span>
          <StatusTag :dict="APPLICATION_STATUS" :value="currentApp?.status" />
        </div>
        <el-form-item v-if="nextStatus === 'ended'" label="结束原因" required>
          <el-select v-model="statusCloseReason" placeholder="请选择真实原因" style="width: 100%">
            <el-option v-for="(v, k) in APPLICATION_CLOSE_REASONS" :key="k" :label="v.label" :value="k" />
          </el-select>
        </el-form-item>
        <el-alert
          v-else-if="nextStatus === 'resume_rejected' || nextStatus === 'rejected'"
          :title="nextStatus === 'resume_rejected' ? '将记录为「简历未通过」' : '将记录为「我拒绝了 Offer」'"
          type="info"
          :closable="false"
          class="reason-hint"
        />
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
        <el-button type="primary" :disabled="!nextStatus || (nextStatus === 'ended' && !statusCloseReason)" :loading="statusSaving" @click="saveStatus">确认流转</el-button>
      </template>
    </el-dialog>

    <!-- 详情抽屉 -->
    <ApplicationDetailDrawer v-model="detailVisible" :application-id="detailId" :reload-key="reloadKey" @changed="load(page)" />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
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
import type { Application, ApplicationFacets } from '@/types'
import {
  APPLICATION_CHANNELS,
  APPLICATION_CLOSE_REASONS,
  APPLICATION_STATUS,
  APPLICATION_STATUS_GROUPS,
  STATUS_TRANSITIONS,
  labelOf,
} from '@/constants'
import { fmtDate, fmtSalary } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const dict = useDictStore()
const jobTypes = computed(() => dict.jobTypes)

const items = ref<Application[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(12)
const loading = ref(false)
const loadError = ref('')
const facets = ref<ApplicationFacets>({ all: 0, pending: 0, applied: 0, exam: 0, interview: 0, closed: 0, offered: 0 })

type StatusGroupKey = keyof typeof APPLICATION_STATUS_GROUPS
const STATUS_GROUP_KEYS = Object.keys(APPLICATION_STATUS_GROUPS) as StatusGroupKey[]
const DATE_FILTERS = [
  { label: '全部', value: '' },
  { label: '近 7 日', value: 'last_7_days' },
  { label: '近 30 日', value: 'last_30_days' },
  { label: '30 日前', value: 'older' },
  { label: '未填写', value: 'missing' },
] as const

const filters = reactive({
  keyword: '',
  status_group: 'all' as StatusGroupKey,
  channel: '',
  job_type_id: null as number | null,
  apply_time_range: '',
  apply_time_from: '',
  apply_time_to: '',
  sort_by: 'apply_time',
  sort_order: 'desc' as 'asc' | 'desc',
})
const customDateRange = ref<[string, string] | null>(null)
const sortValue = ref('apply_time:desc')
const hasFilters = computed(() => Boolean(
  filters.keyword
  || filters.status_group !== 'all'
  || filters.channel
  || filters.job_type_id
  || filters.apply_time_range
  || customDateRange.value,
))

let searchTimer: ReturnType<typeof setTimeout> | null = null
let latestRequest = 0

function onSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => load(1), 320)
}

async function load(p = page.value) {
  const requestId = ++latestRequest
  page.value = p
  loading.value = true
  loadError.value = ''
  try {
    const data = await listApplications({
      keyword: filters.keyword || undefined,
      status_group: filters.status_group === 'all' ? undefined : filters.status_group,
      channel: filters.channel || undefined,
      job_type_id: filters.job_type_id ?? undefined,
      apply_time_range: customDateRange.value ? undefined : filters.apply_time_range || undefined,
      apply_time_from: customDateRange.value?.[0] || undefined,
      apply_time_to: customDateRange.value?.[1] || undefined,
      sort_by: filters.sort_by,
      sort_order: filters.sort_order,
      page: p,
      page_size: pageSize.value,
    })
    if (requestId !== latestRequest) return
    if (!data.items.length && data.total > 0 && p > 1) {
      await load(Math.max(1, Math.ceil(data.total / pageSize.value)))
      return
    }
    items.value = data.items
    total.value = data.total
    facets.value = data.facets
    syncRouteQuery()
  } catch {
    if (requestId === latestRequest) loadError.value = '投递记录加载失败，请检查后端服务后重试'
  } finally {
    if (requestId === latestRequest) loading.value = false
  }
}

function setStatusGroup(key: string | number) {
  const value = String(key) as StatusGroupKey
  if (!STATUS_GROUP_KEYS.includes(value) || filters.status_group === value) return
  filters.status_group = value
  void load(1)
}

function setDateRange(value: string) {
  filters.apply_time_range = value
  customDateRange.value = null
  filters.apply_time_from = ''
  filters.apply_time_to = ''
  void load(1)
}

function onCustomDateChange(value: [string, string] | null) {
  customDateRange.value = value
  filters.apply_time_range = ''
  filters.apply_time_from = value?.[0] ?? ''
  filters.apply_time_to = value?.[1] ?? ''
  void load(1)
}

function onSortChange(value: string | number | boolean | undefined) {
  const [sortBy, sortOrder] = String(value || 'apply_time:desc').split(':')
  filters.sort_by = sortBy
  filters.sort_order = sortOrder === 'asc' ? 'asc' : 'desc'
  void load(1)
}

function onPageSizeChange(size: number) {
  pageSize.value = size
  void load(1)
}

function resetFilters() {
  Object.assign(filters, {
    keyword: '',
    status_group: 'all',
    channel: '',
    job_type_id: null,
    apply_time_range: '',
    apply_time_from: '',
    apply_time_to: '',
  })
  customDateRange.value = null
  void load(1)
}

function hydrateFromRoute() {
  const q = route.query
  filters.keyword = typeof q.keyword === 'string' ? q.keyword : ''
  filters.channel = typeof q.channel === 'string' ? q.channel : ''
  const jobTypeId = Number(q.job_type_id)
  filters.job_type_id = jobTypeId > 0 ? jobTypeId : null
  const requestedGroup = typeof q.status_group === 'string' ? q.status_group : statusToGroup(String(q.status || ''))
  filters.status_group = STATUS_GROUP_KEYS.includes(requestedGroup as StatusGroupKey) ? requestedGroup as StatusGroupKey : 'all'
  filters.apply_time_range = typeof q.apply_time_range === 'string' ? q.apply_time_range : ''
  const from = typeof q.apply_time_from === 'string' ? q.apply_time_from : ''
  const to = typeof q.apply_time_to === 'string' ? q.apply_time_to : ''
  customDateRange.value = from && to ? [from, to] : null
  const sortBy = typeof q.sort_by === 'string' ? q.sort_by : 'apply_time'
  const sortOrder = q.sort_order === 'asc' ? 'asc' : 'desc'
  filters.sort_by = sortBy
  filters.sort_order = sortOrder
  sortValue.value = `${sortBy}:${sortOrder}`
  const size = Number(q.page_size)
  pageSize.value = [12, 24, 48].includes(size) ? size : 12
  const routePage = Number(q.page)
  page.value = routePage > 0 ? routePage : 1
}

function statusToGroup(status: string): StatusGroupKey {
  if (status === 'pending') return 'pending'
  if (status === 'applied' || status === 'resume_screening') return 'applied'
  if (status === 'exam') return 'exam'
  if (status === 'interview') return 'interview'
  if (status === 'offered') return 'offered'
  if (['resume_rejected', 'ended', 'rejected'].includes(status)) return 'closed'
  return 'all'
}

function syncRouteQuery() {
  const query: Record<string, string> = {}
  if (filters.keyword) query.keyword = filters.keyword
  if (filters.status_group !== 'all') query.status_group = filters.status_group
  if (filters.channel) query.channel = filters.channel
  if (filters.job_type_id) query.job_type_id = String(filters.job_type_id)
  if (filters.apply_time_range) query.apply_time_range = filters.apply_time_range
  if (customDateRange.value) {
    query.apply_time_from = customDateRange.value[0]
    query.apply_time_to = customDateRange.value[1]
  }
  if (filters.sort_by !== 'apply_time') query.sort_by = filters.sort_by
  if (filters.sort_order !== 'desc') query.sort_order = filters.sort_order
  if (page.value !== 1) query.page = String(page.value)
  if (pageSize.value !== 12) query.page_size = String(pageSize.value)
  void router.replace({ query })
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
  close_reason: null,
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
    close_reason: null,
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
    close_reason: a.close_reason,
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
  if (!editing.value && form.status === 'ended' && !form.close_reason) {
    ElMessage.warning('请选择结束原因')
    return
  }
  saving.value = true
  try {
    const data: Record<string, unknown> = { ...form }
    if (editing.value) {
      delete data.status
      delete data.close_reason
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
  load(items.value.length === 1 && page.value > 1 ? page.value - 1 : page.value)
}

/* ---- 状态流转 ---- */
const statusVisible = ref(false)
const statusSaving = ref(false)
const currentApp = ref<Application | null>(null)
const nextStatus = ref('')
const statusNote = ref('')
const statusCloseReason = ref('')

const nextOptions = computed(() => (currentApp.value ? (STATUS_TRANSITIONS[currentApp.value.status] ?? []) : []))

function openStatus(a: Application) {
  currentApp.value = a
  nextStatus.value = ''
  statusNote.value = ''
  statusCloseReason.value = ''
  statusVisible.value = true
}
async function saveStatus() {
  if (!currentApp.value || !nextStatus.value) return
  if (nextStatus.value === 'ended' && !statusCloseReason.value) {
    ElMessage.warning('请选择结束原因')
    return
  }
  statusSaving.value = true
  try {
    await changeApplicationStatus(currentApp.value.id, {
      to_status: nextStatus.value,
      note: statusNote.value || undefined,
      close_reason: statusCloseReason.value || undefined,
    })
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
        const { focus: _focus, ...rest } = route.query
        void router.replace({ query: rest })
      }
    }
  },
  { immediate: true },
)

onMounted(async () => {
  await dict.ensureJobTypes()
  hydrateFromRoute()
  load(page.value)
  listResumes().then((rows) => (resumes.value = rows))
})

onBeforeUnmount(() => {
  if (searchTimer) clearTimeout(searchTimer)
  latestRequest++
})
</script>

<style scoped>
.filter-panel {
  display: flex;
  flex-direction: column;
  gap: 13px;
  padding: 14px;
  margin-bottom: 16px;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
}
.filter-main {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.f-keyword {
  width: min(340px, 100%);
}
.f-select {
  width: 140px;
}
.f-select.wide {
  width: 168px;
}
.f-total {
  margin-left: auto;
  font-size: 12px;
  color: var(--ink-3);
}
.filter-section {
  display: grid;
  grid-template-columns: 70px minmax(0, 1fr);
  gap: 10px;
  align-items: start;
  padding-top: 12px;
  border-top: 1px solid var(--line);
}
.filter-label {
  padding: 7px 0 0 4px;
  color: var(--ink-3);
  font-size: 12px;
  font-weight: 600;
}
.status-chips,
.date-chips {
  display: flex;
  gap: 7px;
  min-width: 0;
  flex-wrap: wrap;
  max-width: 100%;
}
.status-chip {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 114px;
  padding: 7px 10px;
  border: 1px solid var(--line);
  border-radius: 11px;
  background: var(--surface);
  color: var(--ink-2);
  font-family: inherit;
  cursor: pointer;
  transition: border-color 0.18s, background 0.18s, transform 0.18s;
}
.status-chip:hover {
  border-color: var(--accent-line);
  transform: translateY(-1px);
}
.status-chip.active {
  border-color: var(--accent-line);
  background: var(--accent-soft);
  color: var(--accent-strong);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--accent-line) 45%, transparent);
}
.status-chip-main {
  font-size: 12.5px;
  font-weight: 650;
  white-space: nowrap;
}
.status-chip-main b {
  margin-left: 2px;
  font-size: 11px;
}
.status-chip-sub {
  margin-top: 2px;
  max-width: 180px;
  color: var(--ink-3);
  font-size: 10.5px;
  line-height: 1.35;
  white-space: nowrap;
}
.status-chip.active .status-chip-sub {
  color: color-mix(in srgb, var(--accent-strong) 72%, var(--ink-3));
}
.date-chips {
  align-items: center;
}
.date-chip-filter {
  min-height: 32px;
  padding: 5px 11px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--surface);
  color: var(--ink-2);
  font: inherit;
  font-size: 12px;
  cursor: pointer;
}
.date-chip-filter:hover,
.date-chip-filter.active {
  border-color: var(--accent-line);
  background: var(--accent-soft);
  color: var(--accent-strong);
}
.custom-date {
  width: 260px;
  max-width: 100%;
  min-width: 0;
}
.load-error {
  margin-bottom: 12px;
}
@media (max-width: 860px) {
  .f-keyword,
  .f-select,
  .f-select.wide {
    width: 100%;
  }
  .reset-btn {
    flex: 1;
  }
  .f-total {
    margin-left: 0;
  }
  .filter-section {
    grid-template-columns: 1fr;
    gap: 7px;
  }
  .filter-label {
    padding-top: 0;
  }
  .status-chips {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 4px;
    scroll-snap-type: x proximity;
  }
  .status-chip {
    min-width: 150px;
    scroll-snap-align: start;
  }
  .custom-date {
    width: 100% !important;
    max-width: 100%;
    min-width: 0 !important;
  }
  .date-chips {
    width: 100%;
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
  overflow-x: auto;
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
.reason-hint {
  margin-bottom: 14px;
}
</style>
