<template>
  <div class="page">
    <PageHeader
      kicker="MODULE 01 · 简历与资产"
      title="素材库"
      desc="把项目 / 实习 / 校园经历结构化沉淀，随时取用拼装简历、准备面试。"
    >
      <template #actions>
        <el-button type="primary" @click="openCreate"><el-icon><Plus /></el-icon>&nbsp;新增素材</el-button>
      </template>
    </PageHeader>

    <div class="filter-row">
      <button class="chip" :class="{ active: filterCat === '' }" @click="filterCat = ''; load()">
        全部 <span class="mono">{{ all.length }}</span>
      </button>
      <button
        v-for="cat in categories"
        :key="cat"
        class="chip"
        :class="{ active: filterCat === cat }"
        @click="filterCat = cat; load()"
      >
        <span class="dot" :style="{ background: catColor(cat) }" />
        {{ labelOf(MATERIAL_CATEGORIES, cat) }}
      </button>
      <el-input
        v-model="keyword"
        class="filter-search"
        placeholder="搜索标题 / 单位 / 描述 / 亮点"
        clearable
        :prefix-icon="Search"
        @input="debouncedLoad"
      />
    </div>

    <el-skeleton v-if="loading" :rows="6" animated class="panel" style="padding: 20px" />
    <EmptyState
      v-else-if="!items.length"
      icon="Notebook"
      title="素材库还是空的"
      desc="把项目、实习、竞赛等经历按 STAR 结构录入，之后写简历和面试都能直接复用。"
    >
      <template #action>
        <el-button type="primary" @click="openCreate">录入第一条素材</el-button>
      </template>
    </EmptyState>

    <div v-else class="masonry">
      <article v-for="m in items" :key="m.id" class="material panel card-hover">
        <div class="m-top">
          <StatusTag :dict="MATERIAL_CATEGORIES" :value="m.category" />
          <div class="mops" @click.stop>
            <button class="op" @click="openEdit(m)"><el-icon><Edit /></el-icon></button>
            <button class="op danger" @click="remove(m)"><el-icon><Delete /></el-icon></button>
          </div>
        </div>

        <h3 class="m-title">{{ m.title }}</h3>

        <div v-if="m.organization || m.role" class="m-meta">
          <span v-if="m.organization">{{ m.organization }}</span>
          <span v-if="m.role"> · {{ m.role }}</span>
        </div>
        <div v-if="m.start_date" class="m-dates mono">
          {{ fmtDate(m.start_date) }}<template v-if="m.end_date"> — {{ fmtDate(m.end_date) }}</template>
        </div>

        <div v-if="m.highlights" class="m-highlights">
          <el-icon><TrendCharts /></el-icon>
          <span>{{ m.highlights }}</span>
        </div>

        <p v-if="m.description" class="m-desc">{{ m.description }}</p>

        <div v-if="m.tech_stack?.length" class="m-tags">
          <el-tag v-for="t in m.tech_stack" :key="t" size="small" effect="plain" type="primary">{{ t }}</el-tag>
        </div>
        <div v-if="m.tags?.length" class="m-tags custom">
          <el-tag v-for="t in m.tags" :key="t" size="small" effect="plain" type="info">{{ t }}</el-tag>
        </div>

        <div class="m-foot">
          <span class="mono">{{ fmtRelative(m.updated_at) }} 更新</span>
        </div>
      </article>
    </div>

    <!-- 表单 -->
    <el-dialog v-model="formVisible" :title="editing ? '编辑素材' : '新增素材'" width="600px" destroy-on-close top="6vh">
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" class="form">
        <div class="form-grid">
          <el-form-item label="素材分类" prop="category">
            <el-select v-model="form.category" style="width: 100%" filterable allow-create default-first-option>
              <el-option v-for="(v, k) in MATERIAL_CATEGORIES" :key="k" :label="v.label" :value="k" />
            </el-select>
          </el-form-item>
          <el-form-item label="标题" prop="title">
            <el-input v-model="form.title" maxlength="200" placeholder="如 基于大模型的校园二手交易平台" />
          </el-form-item>
          <el-form-item label="单位 / 学校 / 组织">
            <el-input v-model="form.organization" maxlength="200" />
          </el-form-item>
          <el-form-item label="角色 / 职位">
            <el-input v-model="form.role" maxlength="100" placeholder="如 后端负责人 / 核心成员" />
          </el-form-item>
          <el-form-item label="开始时间">
            <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
          <el-form-item label="结束时间">
            <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
        </div>
        <el-form-item label="亮点 / 量化成果">
          <el-input v-model="form.highlights" placeholder="如 日活提升 40%，接口 P99 延迟下降 65%" />
        </el-form-item>
        <el-form-item label="详细描述">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="建议按 STAR 结构：背景 → 任务 → 行动 → 结果" />
        </el-form-item>
        <el-form-item label="技术栈">
          <TagInput v-model="form.tech_stack" placeholder="+ 技术栈" />
        </el-form-item>
        <el-form-item label="自定义标签">
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
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { useDictStore } from '@/stores/dict'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import TagInput from '@/components/TagInput.vue'
import { createMaterial, deleteMaterial, listMaterials, updateMaterial } from '@/api'
import type { Material } from '@/types'
import { MATERIAL_CATEGORIES, labelOf } from '@/constants'
import { fmtDate, fmtRelative } from '@/utils/format'

const dict = useDictStore()
const items = ref<Material[]>([])
const all = ref<Material[]>([])
const loading = ref(false)
const filterCat = ref('')
const keyword = ref('')
let timer: ReturnType<typeof setTimeout> | null = null

const categories = computed(() => {
  const merged = Object.keys(MATERIAL_CATEGORIES)
  for (const m of all.value) {
    if (!merged.includes(m.category)) merged.push(m.category)
  }
  return merged
})

const catColor = (cat: string) => dict.jobTypes.length ? (MATERIAL_CATEGORIES[cat]?.dot ?? '#8f8a83') : '#8f8a83'

function debouncedLoad() {
  if (timer) clearTimeout(timer)
  timer = setTimeout(load, 350)
}

async function load() {
  loading.value = true
  try {
    const rows = await listMaterials({
      category: filterCat.value || undefined,
      keyword: keyword.value || undefined,
    })
    all.value = rows
    if (filterCat.value) {
      items.value = rows
    } else {
      items.value = rows
    }
  } finally {
    loading.value = false
  }
}

/* ---- 表单 ---- */
interface MaterialForm {
  category: string
  title: string
  organization: string
  role: string
  start_date: string | null
  end_date: string | null
  description: string
  highlights: string
  tech_stack: string[]
  tags: string[]
}

const formVisible = ref(false)
const editing = ref<Material | null>(null)
const saving = ref(false)
const formRef = ref<FormInstance>()
const form = reactive<MaterialForm>({
  category: 'project',
  title: '',
  organization: '',
  role: '',
  start_date: null,
  end_date: null,
  description: '',
  highlights: '',
  tech_stack: [],
  tags: [],
})
const rules: FormRules = {
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  title: [{ required: true, message: '请填写标题', trigger: 'blur' }],
}

function openCreate() {
  editing.value = null
  Object.assign(form, {
    category: filterCat.value || 'project',
    title: '',
    organization: '',
    role: '',
    start_date: null,
    end_date: null,
    description: '',
    highlights: '',
    tech_stack: [],
    tags: [],
  })
  formVisible.value = true
}
function openEdit(m: Material) {
  editing.value = m
  Object.assign(form, {
    category: m.category,
    title: m.title,
    organization: m.organization ?? '',
    role: m.role ?? '',
    start_date: m.start_date ?? null,
    end_date: m.end_date ?? null,
    description: m.description ?? '',
    highlights: m.highlights ?? '',
    tech_stack: m.tech_stack ?? [],
    tags: m.tags ?? [],
  })
  formVisible.value = true
}
async function save() {
  await formRef.value?.validate()
  saving.value = true
  try {
    if (editing.value) await updateMaterial(editing.value.id, form)
    else await createMaterial(form)
    ElMessage.success('已保存')
    formVisible.value = false
    load()
  } finally {
    saving.value = false
  }
}
async function remove(m: Material) {
  await ElMessageBox.confirm(`确定删除素材「${m.title}」？`, '删除素材', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteMaterial(m.id)
  ElMessage.success('已删除')
  load()
}

onMounted(() => {
  dict.ensureMaterialCategories()
  load()
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
.chip.active {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: var(--accent-strong);
  font-weight: 600;
}
.filter-search {
  margin-left: auto;
  width: 250px;
}
@media (max-width: 860px) {
  .filter-search {
    width: 100%;
    margin-left: 0;
  }
}

.masonry {
  columns: 3 320px;
  column-gap: 14px;
}
.material {
  break-inside: avoid;
  padding: 16px 18px;
  margin-bottom: 14px;
}
.m-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.mops {
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.2s;
}
.material:hover .mops {
  opacity: 1;
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
.m-title {
  margin: 10px 0 2px;
  font-size: 15px;
  font-weight: 650;
  color: var(--ink);
}
.m-meta {
  font-size: 12.5px;
  color: var(--ink-2);
}
.m-dates {
  font-size: 11.5px;
  color: var(--ink-3);
  margin-top: 2px;
}
.m-highlights {
  display: flex;
  gap: 7px;
  margin-top: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  background: var(--accent-soft);
  border: 1px solid var(--accent-line);
  color: var(--accent-strong);
  font-size: 12.5px;
  line-height: 1.6;
}
.m-desc {
  margin: 10px 0 0;
  font-size: 12.5px;
  color: var(--ink-2);
  line-height: 1.75;
  white-space: pre-line;
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.m-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}
.m-foot {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px dashed var(--line);
  font-size: 11.5px;
  color: var(--ink-3);
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
</style>