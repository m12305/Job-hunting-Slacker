<template>
  <el-drawer
    :model-value="modelValue"
    :size="drawerSize"
    :title="`问答复盘 · ${interview ? labelOf(INTERVIEW_ROUNDS, interview.round) : ''}`"
    destroy-on-close
    @update:model-value="(v: boolean) => emit('update:modelValue', v)"
  >
    <div class="qa-sub muted">
      <template v-if="interview?.application_id">
        真实提问 + 自己的回答 + 复盘改进，沉淀为可复用的面试经验。
      </template>
      已记录 {{ items.length }} 条
    </div>

    <!-- 新增 -->
    <div class="qa-compose panel">
      <el-form :model="draft" label-position="top">
        <el-form-item label="面试官提问" required>
          <el-input v-model="draft.question" type="textarea" :rows="2" placeholder="原样记录提问，越具体越好" />
        </el-form-item>
        <el-form-item label="我的回答（复盘记录）">
          <el-input v-model="draft.my_answer" type="textarea" :rows="2" placeholder="当时怎么答的 / 理想答案" />
        </el-form-item>
        <el-form-item label="回答复盘 / 改进点">
          <el-input v-model="draft.feedback" type="textarea" :rows="2" placeholder="哪里没答好、下次怎么答" />
        </el-form-item>
        <div class="compose-row">
          <el-select v-model="draft.category" placeholder="归类" style="width: 140px">
            <el-option v-for="(v, k) in QA_CATEGORIES" :key="k" :label="v" :value="k" />
          </el-select>
          <el-button type="primary" :disabled="!draft.question.trim()" @click="addQa">
            <el-icon><Plus /></el-icon>&nbsp;记录
          </el-button>
        </div>
      </el-form>
    </div>

    <el-skeleton v-if="loading" :rows="5" animated class="panel" style="padding: 20px; margin-top: 12px" />
    <EmptyState
      v-else-if="!items.length"
      icon="ChatLineSquare"
      title="还没有问答记录"
      desc="面试结束后趁记忆新鲜，把真实提问与复盘立即记下来。"
    />

    <div v-else class="qa-list">
      <article v-for="qa in items" :key="qa.id" class="qa-item panel">
        <div class="qa-head">
          <span class="qa-cat">{{ categoryLabel(qa.category) }}</span>
          <span class="mono qa-time">{{ fmtRelative(qa.created_at) }}</span>
          <div class="qa-ops" @click.stop>
            <button class="op" @click="startEdit(qa)"><el-icon><Edit /></el-icon></button>
            <button class="op danger" @click="removeQa(qa)"><el-icon><Delete /></el-icon></button>
          </div>
        </div>

        <template v-if="editingId === qa.id">
          <el-input v-model="editDraft.question" placeholder="提问" />
          <el-input v-model="editDraft.my_answer" type="textarea" :rows="2" placeholder="我的回答" class="mv" />
          <el-input v-model="editDraft.feedback" type="textarea" :rows="2" placeholder="复盘/改进" class="mv" />
          <div class="edit-ops">
            <el-select v-model="editDraft.category" style="width: 130px">
              <el-option v-for="(v, k) in QA_CATEGORIES" :key="k" :label="v" :value="k" />
            </el-select>
            <el-button type="primary" size="small" @click="saveEdit">保存</el-button>
            <el-button size="small" @click="editingId = null">取消</el-button>
          </div>
        </template>

        <template v-else>
          <div class="qa-question">{{ qa.question }}</div>
          <div v-if="qa.my_answer" class="qa-answer">
            <span class="qr-label">我的回答</span>
            <p>{{ qa.my_answer }}</p>
          </div>
          <div v-if="qa.feedback" class="qa-feedback">
            <span class="qr-label">复盘改进</span>
            <p>{{ qa.feedback }}</p>
          </div>
        </template>
      </article>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import EmptyState from '@/components/EmptyState.vue'
import { createInterviewQa, deleteInterviewQa, listInterviewQa, updateInterviewQa } from '@/api'
import type { Interview, InterviewQa } from '@/types'
import { INTERVIEW_ROUNDS, labelOf } from '@/constants'
import { fmtRelative } from '@/utils/format'

const QA_CATEGORIES: Record<string, string> = {
  tech: '技术',
  project: '项目',
  behavior: '行为',
  baguwen: '八股',
}

const categoryLabel = (cat: string | null | undefined) => (cat ? (QA_CATEGORIES[cat] ?? cat) : '未归类')

const props = defineProps<{
  modelValue: boolean
  interview: Interview | null
}>()
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void; (e: 'changed'): void }>()

const drawerSize = computed(() => (window.innerWidth < 860 ? '100%' : '60%'))

const items = ref<InterviewQa[]>([])
const loading = ref(false)
const draft = reactive({ question: '', my_answer: '', feedback: '', category: 'tech' })

const editingId = ref<number | null>(null)
const editDraft = reactive({ question: '', my_answer: '', feedback: '', category: 'tech' })

watch(
  () => [props.modelValue, props.interview?.id],
  ([open]) => {
    if (open && props.interview) {
      load()
      Object.assign(draft, { question: '', my_answer: '', feedback: '', category: 'tech' })
      editingId.value = null
    }
  },
  { immediate: true },
)

async function load() {
  if (!props.interview) return
  loading.value = true
  try {
    items.value = await listInterviewQa(props.interview.id)
  } finally {
    loading.value = false
  }
}

async function addQa() {
  if (!props.interview || !draft.question.trim()) return
  await createInterviewQa(props.interview.id, {
    question: draft.question.trim(),
    my_answer: draft.my_answer.trim() || undefined,
    feedback: draft.feedback.trim() || undefined,
    category: draft.category || undefined,
  })
  Object.assign(draft, { question: '', my_answer: '', feedback: '' })
  ElMessage.success('已记录')
  load()
  emit('changed')
}

function startEdit(qa: InterviewQa) {
  editingId.value = qa.id
  Object.assign(editDraft, { question: qa.question, my_answer: qa.my_answer ?? '', feedback: qa.feedback ?? '', category: qa.category ?? 'tech' })
}
async function saveEdit() {
  if (!editingId.value || !editDraft.question.trim()) return
  await updateInterviewQa(editingId.value, {
    question: editDraft.question.trim(),
    my_answer: editDraft.my_answer.trim() || undefined,
    feedback: editDraft.feedback.trim() || undefined,
    category: editDraft.category || undefined,
  })
  ElMessage.success('已保存')
  editingId.value = null
  load()
}
async function removeQa(qa: InterviewQa) {
  await ElMessageBox.confirm('确定删除这条问答记录？', '删除问答', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteInterviewQa(qa.id)
  ElMessage.success('已删除')
  load()
  emit('changed')
}
</script>

<style scoped>
.qa-sub {
  font-size: 12px;
  margin-bottom: 14px;
  display: flex;
  justify-content: space-between;
}
.qa-compose {
  padding: 14px 16px;
  margin-bottom: 14px;
}
.compose-row {
  display: flex;
  gap: 10px;
  align-items: center;
}
.qa-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.qa-item {
  padding: 14px 16px;
}
.qa-head {
  display: flex;
  align-items: center;
  gap: 10px;
}
.qa-cat {
  font-size: 11px;
  color: var(--accent-strong);
  background: var(--accent-soft);
  border: 1px solid var(--accent-line);
  padding: 1px 8px;
  border-radius: 999px;
  font-weight: 550;
}
.qa-time {
  font-size: 11px;
  color: var(--ink-3);
}
.qa-ops {
  margin-left: auto;
  display: flex;
  gap: 2px;
}
.op {
  width: 25px;
  height: 25px;
  border: none;
  background: transparent;
  color: var(--ink-3);
  cursor: pointer;
  border-radius: 6px;
}
.op:hover {
  color: var(--accent-strong);
  background: var(--accent-soft);
}
.op.danger:hover {
  color: var(--danger);
  background: var(--danger-soft);
}
.qa-question {
  margin-top: 10px;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink);
  line-height: 1.6;
}
.qr-label {
  display: block;
  font-size: 11px;
  color: var(--ink-3);
  letter-spacing: 0.06em;
  margin-top: 10px;
}
.qa-answer p,
.qa-feedback p {
  margin: 4px 0 0;
  font-size: 12.5px;
  color: var(--ink-2);
  white-space: pre-line;
  line-height: 1.7;
  background: var(--surface-2);
  border-radius: 8px;
  padding: 8px 10px;
}
.qa-feedback p {
  background: var(--warn-soft);
  color: #7a5a12;
}
.mv {
  margin-top: 8px;
}
.edit-ops {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  align-items: center;
}
</style>