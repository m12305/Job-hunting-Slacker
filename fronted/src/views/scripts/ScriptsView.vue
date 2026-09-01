<template>
  <div class="page">
    <PageHeader
      kicker="MODULE 05 · 工具箱"
      title="话术库"
      desc="沉淀自我介绍、项目亮点、反问问题等面试话术，收藏高频片段，面试前快速取用。"
    >
      <template #actions>
        <el-button type="primary" @click="openCreate"><el-icon><Plus /></el-icon>&nbsp;新增话术</el-button>
      </template>
    </PageHeader>

    <div class="filter-row">
      <button class="chip" :class="{ active: filters.category === '' }" @click="filters.category = ''; load()">
        全部 <span class="mono">{{ count }}</span>
      </button>
      <button v-for="(v, k) in SCRIPT_CATEGORIES" :key="k" class="chip" :class="{ active: filters.category === k }" @click="filters.category = k; load()">
        <span class="dot" :style="{ background: v.dot }" />{{ v.label }}
      </button>
      <el-checkbox v-model="onlyFav" @change="load()">只看收藏</el-checkbox>
      <el-input v-model="filters.keyword" placeholder="搜索标题 / 内容" clearable :prefix-icon="Search" class="s-search" @input="debouncedLoad" />
    </div>

    <el-skeleton v-if="loading" :rows="6" animated class="panel" style="padding: 20px" />
    <EmptyState
      v-else-if="!items.length"
      icon="MagicStick"
      title="话术库还是空的"
      desc="把自己准备好的面试话术片段沉淀下来，面试前打开就能背。"
    >
      <template #action>
        <el-button type="primary" @click="openCreate">写下第一条话术</el-button>
      </template>
    </EmptyState>

    <div v-else class="grid">
      <article v-for="s in items" :key="s.id" class="script panel card-hover">
        <div class="s-head">
          <StatusTag :dict="SCRIPT_CATEGORIES" :value="s.category" />
          <div class="s-ops">
            <span class="mono used">{{ s.usage_count }} 次使用</span>
            <button class="star" :class="{ fav: s.is_favorite }" @click="toggleFav(s)">
              <el-icon><component :is="s.is_favorite ? 'StarFilled' : 'Star'" /></el-icon>
            </button>
            <button class="op" @click="openEdit(s)"><el-icon><Edit /></el-icon></button>
            <button class="op danger" @click="remove(s)"><el-icon><Delete /></el-icon></button>
          </div>
        </div>
        <h3 class="s-title">{{ s.title }}</h3>
        <p class="s-content">{{ s.content }}</p>
        <div v-if="s.tags?.length" class="s-tags">
          <el-tag v-for="t in s.tags" :key="t" size="small" effect="plain" type="info">{{ t }}</el-tag>
        </div>
        <div class="s-foot">
          <span class="muted sm">{{ fmtRelative(s.updated_at) }}</span>
          <el-button size="small" type="primary" plain @click="copy(s)">
            <el-icon><CopyDocument /></el-icon>&nbsp;复制
          </el-button>
        </div>
      </article>
    </div>

    <!-- 表单 -->
    <el-dialog
      v-model="formVisible"
      :title="editing ? '编辑话术' : '新增话术'"
      width="min(580px, calc(100vw - 24px))"
      class="viewport-dialog"
      append-to-body
      destroy-on-close
      top="2vh"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <div class="f-row">
          <el-form-item label="分类" prop="category">
            <el-select v-model="form.category" style="width: 100%">
              <el-option v-for="(v, k) in SCRIPT_CATEGORIES" :key="k" :label="v.label" :value="k" />
            </el-select>
          </el-form-item>
          <el-form-item label="标题" prop="title">
            <el-input v-model="form.title" maxlength="200" placeholder="如 项目难点话术 / 反问问题清单" />
          </el-form-item>
        </div>
        <el-form-item label="话术内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="7" placeholder="按条理写清楚，可多段落" />
        </el-form-item>
        <el-form-item label="标签">
          <TagInput v-model="form.tags" placeholder="+ 标签" />
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
import TagInput from '@/components/TagInput.vue'
import { createScript, deleteScript, listScripts, setScriptFavorite, updateScript, useScript } from '@/api'
import type { Script } from '@/types'
import { SCRIPT_CATEGORIES } from '@/constants'
import { fmtRelative } from '@/utils/format'

const items = ref<Script[]>([])
const count = ref(0)
const loading = ref(false)
const onlyFav = ref(false)
const filters = reactive({ category: '', keyword: '' })
let timer: ReturnType<typeof setTimeout> | null = null

function debouncedLoad() {
  if (timer) clearTimeout(timer)
  timer = setTimeout(load, 350)
}
async function load() {
  loading.value = true
  try {
    items.value = await listScripts({
      category: filters.category || undefined,
      keyword: filters.keyword || undefined,
      favorite: onlyFav.value ? 1 : undefined,
    })
    count.value = items.value.length
  } finally {
    loading.value = false
  }
}

async function copy(s: Script) {
  try {
    await navigator.clipboard.writeText(s.content)
    await useScript(s.id)
    ElMessage.success('已复制并计入使用次数')
    load()
  } catch {
    ElMessage.warning('复制失败，请手动选择复制')
  }
}
async function toggleFav(s: Script) {
  await setScriptFavorite(s.id, !s.is_favorite)
  load()
}

/* ---- 表单 ---- */
interface ScriptForm {
  category: string
  title: string
  content: string
  tags: string[]
}

const formVisible = ref(false)
const editing = ref<Script | null>(null)
const saving = ref(false)
const formRef = ref<FormInstance>()
const form = reactive<ScriptForm>({ category: 'general', title: '', content: '', tags: [] })
const rules: FormRules = {
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  title: [{ required: true, message: '请填写标题', trigger: 'blur' }],
  content: [{ required: true, message: '请填写话术内容', trigger: 'blur' }],
}

function openCreate() {
  editing.value = null
  Object.assign(form, { category: filters.category || 'general', title: '', content: '', tags: [] })
  formVisible.value = true
}
function openEdit(s: Script) {
  editing.value = s
  Object.assign(form, { category: s.category, title: s.title, content: s.content, tags: s.tags ?? [] })
  formVisible.value = true
}
async function save() {
  await formRef.value?.validate()
  saving.value = true
  try {
    if (editing.value) await updateScript(editing.value.id, form)
    else await createScript(form)
    ElMessage.success('已保存')
    formVisible.value = false
    load()
  } finally {
    saving.value = false
  }
}
async function remove(s: Script) {
  await ElMessageBox.confirm(`确定删除话术「${s.title}」？`, '删除话术', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteScript(s.id)
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
.s-search {
  width: 220px;
  margin-left: auto;
}
@media (max-width: 860px) {
  .s-search {
    width: 100%;
    margin-left: 0;
  }
}

.grid {
  columns: 3 330px;
  column-gap: 14px;
}
.script {
  break-inside: avoid;
  padding: 16px 18px;
  margin-bottom: 14px;
  display: flex;
  flex-direction: column;
}
.s-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.s-ops {
  display: flex;
  align-items: center;
  gap: 4px;
}
.used {
  font-size: 10.5px;
  color: var(--ink-3);
  margin-right: 2px;
}
.star {
  border: none;
  background: transparent;
  color: var(--ink-4);
  cursor: pointer;
  font-size: 14px;
  display: inline-flex;
  padding: 3px;
}
.star.fav {
  color: #b7791f;
}
.op {
  width: 26px;
  height: 26px;
  border: none;
  background: transparent;
  border-radius: 6px;
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
.s-title {
  margin: 10px 0 6px;
  font-size: 14.5px;
  font-weight: 650;
  color: var(--ink);
}
.s-content {
  margin: 0;
  font-size: 12.5px;
  color: var(--ink-2);
  line-height: 1.75;
  white-space: pre-line;
  display: -webkit-box;
  -webkit-line-clamp: 6;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.s-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}
.s-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px dashed var(--line);
  margin-top: 12px;
}
.sm {
  font-size: 11.5px;
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
