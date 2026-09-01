<template>
  <div class="page">
    <PageHeader
      kicker="MODULE 03 · 题库"
      title="题库"
      desc="归档手撕代码、八股文、项目反问等题目，标注难度与掌握状态，形成自己的复习弹药库。"
    >
      <template #actions>
        <el-button type="primary" @click="openCreate"><el-icon><Plus /></el-icon>&nbsp;收录题目</el-button>
      </template>
    </PageHeader>

    <div class="filter-row">
      <button class="chip" :class="{ active: filters.category === '' }" @click="filters.category = ''; load()">
        全部 <span class="mono">{{ allCount }}</span>
      </button>
      <button v-for="(v, k) in QUESTION_CATEGORIES" :key="k" class="chip" :class="{ active: filters.category === k }" @click="filters.category = k; load()">
        <span class="dot" :style="{ background: v.dot }" />{{ v.label }}
      </button>
      <el-select v-model="filters.difficulty" placeholder="难度" clearable class="q-select" @change="load()">
        <el-option v-for="(v, k) in QUESTION_DIFFICULTY" :key="k" :label="v.label" :value="k" />
      </el-select>
      <el-select v-model="filters.review_status" placeholder="掌握状态" clearable class="q-select" @change="load()">
        <el-option v-for="(v, k) in QUESTION_REVIEW_STATUS" :key="k" :label="v.label" :value="k" />
      </el-select>
      <el-input v-model="filters.keyword" placeholder="搜索标题 / 内容 / 来源" clearable :prefix-icon="Search" class="q-search" @input="debouncedLoad" />
    </div>

    <el-skeleton v-if="loading" :rows="6" animated class="panel" style="padding: 20px" />
    <EmptyState
      v-else-if="!items.length"
      icon="Reading"
      title="题库还是空的"
      desc="把面试中遇到的真题、刷到的八股、项目反问收录进来，标注「待刷 / 已掌握」持续滚动复习。"
    >
      <template #action>
        <el-button type="primary" @click="openCreate">收录第一题</el-button>
      </template>
    </EmptyState>

    <div v-else class="q-list">
      <article v-for="q in items" :key="q.id" class="q-item panel card-hover" @click="expanded === q.id ? (expanded = null) : (expanded = q.id)">
        <div class="q-row">
          <div class="q-main">
            <div class="q-title-line">
              <span class="q-title">{{ q.title }}</span>
              <StatusTag v-if="q.category" :dict="QUESTION_CATEGORIES" :value="q.category" />
            </div>
            <div class="q-meta">
              <StatusTag v-if="q.difficulty" :dict="QUESTION_DIFFICULTY" :value="q.difficulty" />
              <StatusTag v-if="q.review_status" :dict="QUESTION_REVIEW_STATUS" :value="q.review_status" />
              <span v-if="q.source" class="q-source muted">来源：{{ q.source }}</span>
              <span class="mono muted q-time">{{ fmtRelative(q.updated_at) }}</span>
              <el-icon class="chev" :class="{ open: expanded === q.id }"><ArrowDown /></el-icon>
            </div>
          </div>
          <div class="q-ops" @click.stop>
            <el-button
              v-if="q.review_status !== 'todo'"
              size="small"
              plain
              type="warning"
              @click="setStatus(q, 'todo')"
            >待刷</el-button>
            <el-button
              v-if="q.review_status !== 'mastered'"
              size="small"
              plain
              type="success"
              @click="setStatus(q, 'mastered')"
            >已掌握</el-button>
            <el-tooltip content="编辑" placement="top">
              <button class="op" @click="openEdit(q)"><el-icon><Edit /></el-icon></button>
            </el-tooltip>
            <el-tooltip content="删除" placement="top">
              <button class="op danger" @click="remove(q)"><el-icon><Delete /></el-icon></button>
            </el-tooltip>
          </div>
        </div>

        <transition name="expand">
          <div v-if="expanded === q.id" class="q-detail">
            <div v-if="q.content" class="q-block">
              <div class="q-block-label">题目内容</div>
              <pre class="q-pre">{{ q.content }}</pre>
            </div>
            <div v-if="q.answer" class="q-block answer">
              <div class="q-block-label">参考答案 / 我的解法</div>
              <pre class="q-pre">{{ q.answer }}</pre>
            </div>
            <div v-if="q.tags?.length" class="q-tags">
              <el-tag v-for="t in q.tags" :key="t" size="small" effect="plain">{{
                t
              }}</el-tag>
            </div>
          </div>
        </transition>
      </article>
    </div>

    <!-- 表单 -->
    <el-dialog
      v-model="formVisible"
      :title="editing ? '编辑题目' : '收录题目'"
      width="min(640px, calc(100vw - 24px))"
      class="viewport-dialog"
      append-to-body
      destroy-on-close
      top="2vh"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="题目标题" prop="title">
          <el-input v-model="form.title" maxlength="300" placeholder="如 手写 LRU 缓存 / HTTP 缓存策略" />
        </el-form-item>
        <div class="f-row">
          <el-form-item label="分类">
            <el-select v-model="form.category" style="width: 100%">
              <el-option v-for="(v, k) in QUESTION_CATEGORIES" :key="k" :label="v.label" :value="k" />
            </el-select>
          </el-form-item>
          <el-form-item label="难度">
            <el-select v-model="form.difficulty" style="width: 100%">
              <el-option v-for="(v, k) in QUESTION_DIFFICULTY" :key="k" :label="v.label" :value="k" />
            </el-select>
          </el-form-item>
          <el-form-item label="掌握状态">
            <el-select v-model="form.review_status" style="width: 100%">
              <el-option v-for="(v, k) in QUESTION_REVIEW_STATUS" :key="k" :label="v.label" :value="k" />
            </el-select>
          </el-form-item>
          <el-form-item label="来源">
            <el-input v-model="form.source" placeholder="公司 / 面试 / 牛客" />
          </el-form-item>
        </div>
        <el-form-item label="题目内容">
          <el-input v-model="form.content" type="textarea" :rows="4" placeholder="完整题目描述" />
        </el-form-item>
        <el-form-item label="参考答案 / 解法">
          <el-input v-model="form.answer" type="textarea" :rows="4" placeholder="自己的解法或较好答案" />
        </el-form-item>
        <el-form-item label="考点标签">
          <TagInput v-model="form.tags" placeholder="+ 考点" />
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
import { createQuestion, deleteQuestion, listQuestions, setQuestionReviewStatus, updateQuestion } from '@/api'
import type { PageData, Question } from '@/types'
import { QUESTION_CATEGORIES, QUESTION_DIFFICULTY, QUESTION_REVIEW_STATUS } from '@/constants'
import { fmtRelative } from '@/utils/format'

const items = ref<Question[]>([])
const allCount = ref(0)
const loading = ref(false)
const expanded = ref<number | null>(null)
const filters = reactive({ category: '', difficulty: '', review_status: '', keyword: '' })
let timer: ReturnType<typeof setTimeout> | null = null

function debouncedLoad() {
  if (timer) clearTimeout(timer)
  timer = setTimeout(load, 350)
}

async function load() {
  loading.value = true
  try {
    const data = await listQuestions({
      category: filters.category || undefined,
      difficulty: filters.difficulty || undefined,
      review_status: filters.review_status || undefined,
      keyword: filters.keyword || undefined,
    })
    if (Array.isArray(data)) {
      items.value = data
      allCount.value = data.length
    } else {
      const page = data as PageData<Question>
      items.value = page.items
      allCount.value = page.total
    }
  } finally {
    loading.value = false
  }
}

async function setStatus(q: Question, status: string) {
  await setQuestionReviewStatus(q.id, status)
  ElMessage.success(status === 'todo' ? '已标记为待刷' : '已标记为已掌握')
  load()
}

/* ---- 表单 ---- */
interface QuestionForm {
  category: string
  difficulty: string
  review_status: string
  title: string
  content: string
  answer: string
  source: string
  tags: string[]
}

const formVisible = ref(false)
const editing = ref<Question | null>(null)
const saving = ref(false)
const formRef = ref<FormInstance>()
const form = reactive<QuestionForm>({
  category: 'code',
  difficulty: 'medium',
  review_status: 'new',
  title: '',
  content: '',
  answer: '',
  source: '',
  tags: [],
})
const rules: FormRules = {
  title: [{ required: true, message: '请填写题目标题', trigger: 'blur' }],
}

function openCreate() {
  editing.value = null
  Object.assign(form, {
    category: filters.category || 'code',
    difficulty: 'medium',
    review_status: 'new',
    title: '',
    content: '',
    answer: '',
    source: '',
    tags: [],
  })
  formVisible.value = true
}
function openEdit(q: Question) {
  editing.value = q
  Object.assign(form, {
    category: q.category ?? 'code',
    difficulty: q.difficulty ?? 'medium',
    review_status: q.review_status,
    title: q.title,
    content: q.content ?? '',
    answer: q.answer ?? '',
    source: q.source ?? '',
    tags: q.tags ?? [],
  })
  formVisible.value = true
}
async function save() {
  await formRef.value?.validate()
  saving.value = true
  try {
    if (editing.value) await updateQuestion(editing.value.id, form)
    else await createQuestion(form)
    ElMessage.success('已保存')
    formVisible.value = false
    load()
  } finally {
    saving.value = false
  }
}
async function remove(q: Question) {
  await ElMessageBox.confirm(`确定删除题目「${q.title}」？`, '删除题目', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteQuestion(q.id)
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
.q-select {
  width: 120px;
}
.q-search {
  width: 220px;
  margin-left: auto;
}
@media (max-width: 860px) {
  .q-search {
    width: 100%;
    margin-left: 0;
  }
  .q-select {
    width: 100%;
  }
}

.q-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.q-item {
  padding: 14px 18px;
  cursor: pointer;
}
.q-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}
.q-main {
  min-width: 0;
}
.q-title-line {
  display: flex;
  align-items: center;
  gap: 10px;
}
.q-title {
  font-size: 14px;
  font-weight: 650;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.q-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
}
.q-source {
  font-size: 11.5px;
}
.q-time {
  font-size: 11px;
  margin-left: auto;
}
.chev {
  color: var(--ink-4);
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
.chev.open {
  transform: rotate(180deg);
}
.q-ops {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
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

.q-detail {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed var(--line);
}
.q-block {
  margin-bottom: 10px;
}
.q-block-label {
  font-size: 11px;
  color: var(--ink-3);
  letter-spacing: 0.06em;
  margin-bottom: 4px;
}
.q-pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12.5px;
  line-height: 1.75;
  color: var(--ink);
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: 9px;
  padding: 10px 12px;
  font-family: inherit;
}
.q-block.answer .q-pre {
  background: var(--ok-soft);
  border-color: #cfe8da;
}
.q-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.expand-enter-active,
.expand-leave-active {
  transition: opacity 0.22s ease, transform 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}
.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: translateY(-4px);
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
