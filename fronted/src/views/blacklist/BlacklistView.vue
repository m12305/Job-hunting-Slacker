<template>
  <div class="page">
    <PageHeader
      kicker="MODULE 05 · 工具箱"
      title="避雷库"
      desc="记录加班严重、薪资虚假、无偿试岗等避雷信息——投递录入时命中会弹出提醒。"
    >
      <template #actions>
        <el-button type="primary" @click="openCreate"><el-icon><Plus /></el-icon>&nbsp;新增避雷记录</el-button>
      </template>
    </PageHeader>

    <div class="filter-row">
      <el-input v-model="filters.company" placeholder="搜索公司名" clearable :prefix-icon="Search" class="b-search" @input="debouncedLoad" />
      <el-select v-model="filters.issue_type" placeholder="全部类型" clearable class="b-select" @change="load()">
        <el-option v-for="(v, k) in BLACKLIST_TYPES" :key="k" :label="v.label" :value="k" />
      </el-select>
      <span class="muted b-hint mono">共 {{ items.length }} 条避雷信息</span>
    </div>

    <el-skeleton v-if="loading" :rows="6" animated class="panel" style="padding: 20px" />
    <EmptyState
      v-else-if="!items.length"
      icon="Warning"
      title="避雷库是空的"
      desc="把踩过的坑记下来（加班文化、薪资货不对板、无偿试岗…），避免下一次重蹈覆辙。"
    >
      <template #action>
        <el-button type="primary" @click="openCreate">新增避雷记录</el-button>
      </template>
    </EmptyState>

    <div v-else class="list">
      <article v-for="b in items" :key="b.id" class="b-item panel card-hover">
        <div class="b-head">
          <div class="b-company">
            <h3>{{ b.company }}</h3>
            <span v-if="b.position" class="b-pos">{{ b.position }}</span>
          </div>
          <StatusTag v-if="b.issue_type" :dict="BLACKLIST_TYPES" :value="b.issue_type" />
        </div>
        <p v-if="b.detail" class="b-detail">{{ b.detail }}</p>
        <div v-if="b.source" class="b-source muted">来源：{{ b.source }}</div>
        <div class="b-foot">
          <span class="mono muted-sm">{{ fmtDate(b.created_at) }}</span>
          <div class="b-ops">
            <button class="op" @click="openEdit(b)"><el-icon><Edit /></el-icon></button>
            <button class="op danger" @click="remove(b)"><el-icon><Delete /></el-icon></button>
          </div>
        </div>
      </article>
    </div>

    <!-- 表单 -->
    <el-dialog
      v-model="formVisible"
      :title="editing ? '编辑避雷记录' : '新增避雷记录'"
      width="min(540px, calc(100vw - 24px))"
      class="viewport-dialog"
      append-to-body
      destroy-on-close
      top="2vh"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <div class="f-row">
          <el-form-item label="公司" prop="company">
            <el-input v-model="form.company" maxlength="200" />
          </el-form-item>
          <el-form-item label="岗位（可选）">
            <el-input v-model="form.position" maxlength="200" />
          </el-form-item>
        </div>
        <el-form-item label="避雷类型">
          <el-select v-model="form.issue_type" style="width: 100%">
            <el-option v-for="(v, k) in BLACKLIST_TYPES" :key="k" :label="v.label" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="详细描述">
          <el-input v-model="form.detail" type="textarea" :rows="4" placeholder="发生了什么、哪些信息与宣传不符…" />
        </el-form-item>
        <el-form-item label="来源">
          <el-input v-model="form.source" placeholder="个人经历 / 他人分享" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import { createBlacklist, deleteBlacklist, listBlacklist, updateBlacklist } from '@/api'
import type { BlacklistItem } from '@/types'
import { BLACKLIST_TYPES } from '@/constants'
import { fmtDate } from '@/utils/format'

const items = ref<BlacklistItem[]>([])
const loading = ref(false)
const filters = reactive({ company: '', issue_type: '' })
let timer: ReturnType<typeof setTimeout> | null = null

function debouncedLoad() {
  if (timer) clearTimeout(timer)
  timer = setTimeout(load, 350)
}
async function load() {
  loading.value = true
  try {
    items.value = await listBlacklist({ company: filters.company || undefined, issue_type: filters.issue_type || undefined })
  } finally {
    loading.value = false
  }
}

/* ---- 表单 ---- */
const formVisible = ref(false)
const editing = ref<BlacklistItem | null>(null)
const saving = ref(false)
const formRef = ref<FormInstance>()
const form = reactive<Record<string, unknown>>({ company: '', position: '', issue_type: null, detail: '', source: '' })
const rules: FormRules = {
  company: [{ required: true, message: '请填写公司名', trigger: 'blur' }],
}

function openCreate() {
  editing.value = null
  Object.assign(form, { company: filters.company || '', position: '', issue_type: null, detail: '', source: '' })
  formVisible.value = true
}
function openEdit(b: BlacklistItem) {
  editing.value = b
  Object.assign(form, { company: b.company, position: b.position ?? '', issue_type: b.issue_type, detail: b.detail ?? '', source: b.source ?? '' })
  formVisible.value = true
}
async function save() {
  await formRef.value?.validate()
  saving.value = true
  try {
    if (editing.value) await updateBlacklist(editing.value.id, form)
    else await createBlacklist(form)
    ElMessage.success('已保存')
    formVisible.value = false
    load()
  } finally {
    saving.value = false
  }
}
async function remove(b: BlacklistItem) {
  await ElMessageBox.confirm(`确定删除「${b.company}」的避雷记录？`, '删除记录', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteBlacklist(b.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.filter-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
  align-items: center;
}
.b-search {
  width: 240px;
}
.b-select {
  width: 150px;
}
.b-hint {
  margin-left: auto;
  font-size: 12px;
}
@media (max-width: 860px) {
  .b-search,
  .b-select {
    width: 100%;
  }
  .b-hint {
    margin-left: 0;
  }
}

.list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.b-item {
  padding: 16px 18px;
}
.b-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.b-company h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
}
.b-pos {
  margin-left: 8px;
  font-size: 12.5px;
  color: var(--ink-2);
}
.b-detail {
  margin: 10px 0 0;
  font-size: 13px;
  color: var(--ink-2);
  line-height: 1.75;
  white-space: pre-line;
}
.b-source {
  margin-top: 8px;
  font-size: 12px;
}
.b-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px dashed var(--line);
}
.muted-sm {
  font-size: 11.5px;
  color: var(--ink-3);
}
.b-ops {
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
@media (max-width: 640px) {
  .f-row {
    grid-template-columns: 1fr;
  }
}
</style>
