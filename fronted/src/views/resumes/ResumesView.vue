<template>
  <div class="page">
    <PageHeader
      kicker="MODULE 01 · 简历与资产"
      title="简历版本"
      desc="每个岗位类型下维护多版简历，记录版本、文件与修改时间线；投递录入时自动带出默认版本。"
    >
      <template #actions>
        <el-button @click="openJobTypes"><el-icon><Setting /></el-icon>&nbsp;岗位类型</el-button>
        <el-button type="primary" :disabled="!jobTypes.length" @click="openCreate">
          <el-icon><Plus /></el-icon>&nbsp;新建简历
        </el-button>
      </template>
    </PageHeader>

    <!-- 岗位类型筛选 chips -->
    <div class="filter-row">
      <button class="chip" :class="{ active: filterType === null }" @click="filterType = null; reload()">
        全部 <span class="mono">{{ resumes.length }}</span>
      </button>
      <button
        v-for="jt in jobTypes"
        :key="jt.id"
        class="chip"
        :class="{ active: filterType === jt.id }"
        @click="filterType = jt.id; reload()"
      >
        <span class="dot" :style="{ background: jt.color || '#8f8a83' }" />
        {{ jt.name }}
      </button>
      <el-input
        v-model="keyword"
        class="filter-search"
        placeholder="搜索版本名 / 目标岗位 / 备注"
        clearable
        :prefix-icon="Search"
        @input="reload"
      />
    </div>

    <!-- 岗位类型分组列表 -->
    <el-skeleton v-if="loading" :rows="6" animated class="panel" style="padding: 20px" />
    <EmptyState
      v-else-if="!jobTypes.length"
      icon="Document"
      title="还没有岗位类型"
      desc="先创建岗位类型（算法 / 开发 / 测试 / 产品…），再为每种岗位维护简历版本。"
    >
      <template #action>
        <el-button type="primary" @click="openJobTypes">去创建岗位类型</el-button>
      </template>
    </EmptyState>
    <EmptyState
      v-else-if="!filtered.length"
      icon="Document"
      title="没有匹配的简历版本"
      desc="换个关键词或岗位类型试试，或直接新建一份简历。"
    />

    <div v-else class="groups">
      <section v-for="gt in filtered" :key="gt.jt?.id ?? 'none'" class="group">
        <div class="group-head">
          <span class="dot" :style="{ background: gt.jt?.color || '#8f8a83' }" />
          <h3>{{ gt.jt?.name || '未分类' }}</h3>
          <span class="mono count">{{ gt.items.length }} 版</span>
          <span v-if="gt.jt" class="default-line">默认版本：{{ defaultOf(gt) }}</span>
        </div>
        <div class="resume-grid">
          <article
            v-for="r in gt.items"
            :key="r.id"
            class="resume-card panel card-hover"
            @click="openPreview(r)"
          >
            <div class="card-top">
              <div class="version">
                <span class="vname">{{ r.version_name }}</span>
                <span v-if="r.is_default" class="default-badge">默认</span>
              </div>
              <StatusTag :dict="RESUME_STATUS" :value="r.status" />
            </div>
            <div class="position">{{ r.target_position || '未填写目标岗位' }}</div>

            <div class="file-line">
              <template v-if="r.file_name">
                <el-icon><Document /></el-icon>
                <span class="file-name">{{ r.file_name }}</span>
                <span class="mono file-meta">{{ r.file_type?.toUpperCase() }} · {{ fmtSize(r.file_size) }}</span>
              </template>
              <span v-else class="no-file">尚未上传文件</span>
            </div>

            <div v-if="r.remark" class="remark">{{ r.remark }}</div>

            <div class="card-foot">
              <span class="updated">{{ fmtRelative(r.updated_at) }} 更新</span>
              <div class="ops" @click.stop>
                <el-tooltip :content="r.file_path ? '预览' : '请先上传简历文件'" placement="top">
                  <button class="op" :class="{ disabled: !r.file_path }" @click="openPreview(r)">
                    <el-icon><View /></el-icon>
                  </button>
                </el-tooltip>
                <el-tooltip content="上传文件" placement="top">
                  <button class="op" @click="pickFile(r)"><el-icon><Upload /></el-icon></button>
                </el-tooltip>
                <el-tooltip v-if="!r.is_default && r.status !== 'archived'" content="设为默认" placement="top">
                  <button class="op" @click="setDefault(r)"><el-icon><Star /></el-icon></button>
                </el-tooltip>
                <el-tooltip content="编辑" placement="top">
                  <button class="op" @click="openEdit(r)"><el-icon><Edit /></el-icon></button>
                </el-tooltip>
                <el-tooltip content="删除" placement="top">
                  <button class="op danger" @click="remove(r)"><el-icon><Delete /></el-icon></button>
                </el-tooltip>
              </div>
            </div>
            <input
              :id="`file-${r.id}`"
              type="file"
              accept=".pdf,.doc,.docx"
              class="hidden-input"
              @change="(e) => onFilePick(r, e)"
            />
          </article>
        </div>
      </section>
    </div>

    <!-- 编辑 / 新增 -->
    <el-dialog
      v-model="formVisible"
      :title="editing ? '编辑简历版本' : '新建简历版本'"
      width="min(520px, calc(100vw - 24px))"
      class="viewport-dialog"
      append-to-body
      destroy-on-close
      top="2vh"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" class="form">
        <el-form-item label="岗位类型" prop="job_type_id">
          <el-select v-model="form.job_type_id" placeholder="选择岗位类型" style="width: 100%">
            <el-option v-for="jt in jobTypes" :key="jt.id" :label="jt.name" :value="jt.id">
              <span class="opt"><span class="dot" :style="{ background: jt.color || '#8f8a83' }" />{{ jt.name }}</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="版本名" prop="version_name">
          <el-input v-model="form.version_name" placeholder="如 v3.1 精简版" maxlength="100" />
        </el-form-item>
        <el-form-item label="目标岗位">
          <el-input v-model="form.target_position" placeholder="如 后端开发工程师" maxlength="100" />
        </el-form-item>
        <div class="form-row">
          <el-form-item label="状态">
            <el-select v-model="form.status" style="width: 100%">
              <el-option v-for="(v, k) in RESUME_STATUS" :key="k" :label="v.label" :value="k" />
            </el-select>
          </el-form-item>
          <el-form-item label="设为默认版本">
            <el-switch v-model="form.is_default" />
          </el-form-item>
        </div>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="适配方向 / 投递范围等" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <!-- 岗位类型管理 -->
    <JobTypesDialog v-model="jobTypesVisible" @changed="(force) => { reload(); dict.ensureJobTypes(force) }" />

    <!-- 预览抽屉 -->
    <ResumePreviewDrawer v-model="previewVisible" :resume="previewing" @uploaded="reload" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { useDictStore } from '@/stores/dict'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import JobTypesDialog from './JobTypesDialog.vue'
import ResumePreviewDrawer from './ResumePreviewDrawer.vue'
import { createResume, deleteResume, listResumes, setResumeDefault, updateResume, uploadResumeFile } from '@/api'
import type { Resume } from '@/types'
import { RESUME_STATUS } from '@/constants'
import { fmtRelative, fmtSize } from '@/utils/format'

const dict = useDictStore()
const jobTypes = computed(() => dict.jobTypes)

const resumes = ref<Resume[]>([])
const loading = ref(false)
const filterType = ref<number | null>(null)
const keyword = ref('')

const filtered = computed(() => {
  const groups = new Map<number | null, Resume[]>()
  for (const r of resumes.value) {
    if (filterType.value !== null && r.job_type_id !== filterType.value) continue
    const key = r.job_type_id
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key)!.push(r)
  }
  const order = [...groups.keys()].sort((a, b) => {
    const ia = a == null ? 999 : (jobTypes.value.find((j) => j.id === a)?.sort_order ?? 99)
    const ib = b == null ? 999 : (jobTypes.value.find((j) => j.id === b)?.sort_order ?? 99)
    return ia - ib
  })
  return order.map((key) => ({
    jt: key == null ? null : jobTypes.value.find((j) => j.id === key),
    items: groups.get(key)!,
  }))
})

function defaultOf(group: { items: Resume[] }): string {
  const d = group.items.find((i) => i.is_default)
  return d ? d.version_name : '未设置'
}

function reload() {
  loading.value = true
  listResumes({ job_type_id: filterType.value ?? undefined, keyword: keyword.value || undefined })
    .then((rows) => (resumes.value = rows))
    .finally(() => (loading.value = false))
}

/* ---- 表单 ---- */
const formVisible = ref(false)
const editing = ref<Resume | null>(null)
const formRef = ref<FormInstance>()
const saving = ref(false)
const form = reactive<Record<string, unknown>>({
  job_type_id: null,
  version_name: '',
  target_position: '',
  status: 'active',
  is_default: false,
  remark: '',
})
const rules: FormRules = {
  job_type_id: [{ required: true, message: '请选择岗位类型', trigger: 'change' }],
  version_name: [{ required: true, message: '请填写版本名', trigger: 'blur' }],
}

function openCreate() {
  editing.value = null
  Object.assign(form, { job_type_id: filterType.value, version_name: '', target_position: '', status: 'active', is_default: false, remark: '' })
  formVisible.value = true
}
function openEdit(r: Resume) {
  editing.value = r
  Object.assign(form, {
    job_type_id: r.job_type_id,
    version_name: r.version_name,
    target_position: r.target_position,
    status: r.status,
    is_default: r.is_default,
    remark: r.remark,
  })
  formVisible.value = true
}
async function save() {
  await formRef.value?.validate()
  saving.value = true
  try {
    if (editing.value) {
      await updateResume(editing.value.id, form)
    } else {
      await createResume(form)
    }
    ElMessage.success(editing.value ? '已保存' : '已创建，接下来可上传简历文件')
    formVisible.value = false
    reload()
  } finally {
    saving.value = false
  }
}

/* ---- 文件上传 ---- */
function pickFile(r: Resume) {
  ;(document.getElementById(`file-${r.id}`) as HTMLInputElement).click()
}
async function onFilePick(r: Resume, e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  const msg = ElMessage({ message: `上传中：${file.name}`, duration: 0, showClose: true })
  try {
    await uploadResumeFile(r.id, file)
    msg.close()
    ElMessage.success('文件上传成功')
    reload()
  } catch {
    msg.close()
  }
}

/* ---- 操作 ---- */
async function setDefault(r: Resume) {
  await setResumeDefault(r.id)
  ElMessage.success(`已将「${r.version_name}」设为默认`)
  reload()
}
async function remove(r: Resume) {
  await ElMessageBox.confirm(
    `确定删除简历「${r.version_name}」？本地文件将一并移除。`,
    '删除简历版本',
    { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
  )
  await deleteResume(r.id)
  ElMessage.success('已删除')
  reload()
}

/* ---- 预览 ---- */
const previewVisible = ref(false)
const previewing = ref<Resume | null>(null)
function openPreview(r: Resume) {
  previewing.value = r
  previewVisible.value = true
}

/* ---- 岗位类型 ---- */
const jobTypesVisible = ref(false)
function openJobTypes() {
  jobTypesVisible.value = true
}

onMounted(() => {
  dict.ensureJobTypes().then(reload)
})
</script>

<style scoped>
.filter-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 18px;
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
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.chip:hover {
  border-color: var(--line-strong);
}
.chip.active {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: var(--accent-strong);
  font-weight: 600;
}
.filter-search {
  margin-left: auto;
  width: 240px;
}
@media (max-width: 860px) {
  .filter-search {
    width: 100%;
    margin-left: 0;
  }
}

.groups {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.group-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.group-head h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 650;
}
.count {
  font-size: 12px;
  color: var(--ink-3);
}
.default-line {
  font-size: 12px;
  color: var(--ink-3);
  margin-left: 8px;
}
.resume-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 14px;
}
.resume-card {
  padding: 16px;
  cursor: pointer;
}
.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.version {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}
.vname {
  font-size: 14.5px;
  font-weight: 650;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.default-badge {
  background: var(--accent-soft);
  color: var(--accent-strong);
  font-size: 10.5px;
  font-weight: 600;
  padding: 1px 7px;
  border-radius: 999px;
  border: 1px solid var(--accent-line);
  flex-shrink: 0;
}
.position {
  margin-top: 3px;
  font-size: 13px;
  color: var(--ink-2);
}
.file-line {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  font-size: 12px;
  color: var(--ink-2);
  background: var(--surface-2);
  border-radius: 8px;
  padding: 7px 10px;
}
.file-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.file-meta {
  margin-left: auto;
  color: var(--ink-3);
  font-size: 11px;
  flex-shrink: 0;
}
.no-file {
  color: var(--ink-3);
  font-size: 12px;
}
.remark {
  margin-top: 10px;
  font-size: 12px;
  color: var(--ink-3);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed var(--line);
}
.updated {
  font-size: 11.5px;
  color: var(--ink-3);
}
.ops {
  display: flex;
  gap: 2px;
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
.op.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.hidden-input {
  display: none;
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
.opt {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
</style>
