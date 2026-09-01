<template>
  <div class="page">
    <PageHeader
      kicker="MODULE 01 · 简历与资产"
      title="资产归档"
      desc="统一归档博客、项目、GitHub、成绩单与证书——链接一键跳转，文件本地归档。"
    >
      <template #actions>
        <el-button type="primary" @click="openCreate('link')"><el-icon><Plus /></el-icon>&nbsp;新增资产</el-button>
      </template>
    </PageHeader>

    <div class="filter-row">
      <button class="chip" :class="{ active: filterCat === '' }" @click="filterCat = ''; load()">
        全部 <span class="mono">{{ all.length }}</span>
      </button>
      <button
        v-for="(v, k) in ASSET_CATEGORIES"
        :key="k"
        class="chip"
        :class="{ active: filterCat === k }"
        @click="filterCat = k; load()"
      >
        <span class="dot" :style="{ background: v.dot }" />
        {{ v.label }}
      </button>
      <el-input
        v-model="keyword"
        class="filter-search"
        placeholder="搜索标题 / 描述"
        clearable
        :prefix-icon="Search"
        @input="debouncedLoad"
      />
    </div>

    <el-skeleton v-if="loading" :rows="6" animated class="panel" style="padding: 20px" />
    <EmptyState
      v-else-if="!items.length"
      icon="FolderOpened"
      title="还没有归档任何资产"
      desc="把博客链接、项目 Demo、GitHub 仓库、证明文件等统一放在这里，投简历和自我介绍时随取随用。"
    >
      <template #action>
        <el-button type="primary" @click="openCreate('link')">新增资产</el-button>
      </template>
    </EmptyState>

    <div v-else class="grid">
      <article v-for="a in items" :key="a.id" class="asset panel card-hover">
        <div class="a-top">
          <StatusTag :dict="ASSET_CATEGORIES" :value="a.category" />
          <div class="aops" @click.stop>
            <button class="op" @click="openEdit(a)"><el-icon><Edit /></el-icon></button>
            <button class="op danger" @click="remove(a)"><el-icon><Delete /></el-icon></button>
          </div>
        </div>

        <h3 class="a-title">{{ a.title }}</h3>
        <p v-if="a.description" class="a-desc">{{ a.description }}</p>

        <div v-if="a.url" class="a-link" @click="openUrl(a)">
          <el-icon><Link /></el-icon>
          <span class="a-url">{{ a.url }}</span>
          <el-icon class="go"><TopRight /></el-icon>
        </div>
        <div v-else-if="a.file_path" class="a-file">
          <el-icon><Document /></el-icon>
          <span>{{ baseName(a.file_path) }}</span>
          <span class="local">本地归档</span>
        </div>
        <div v-else class="a-none muted">未提供链接或文件</div>

        <div v-if="a.tags?.length" class="a-tags">
          <el-tag v-for="t in a.tags" :key="t" size="small" effect="plain" type="info">{{ t }}</el-tag>
        </div>

        <div class="a-foot">
          <span class="mono">{{ fmtRelative(a.updated_at) }} 更新</span>
        </div>
      </article>
    </div>

    <!-- 表单 -->
    <el-dialog
      v-model="formVisible"
      :title="editing ? '编辑资产' : '新增资产'"
      width="min(540px, calc(100vw - 24px))"
      class="viewport-dialog"
      append-to-body
      destroy-on-close
      top="2vh"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="资产分类" prop="category">
          <el-select v-model="form.category" style="width: 100%">
            <el-option v-for="(v, k) in ASSET_CATEGORIES" :key="k" :label="v.label" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题 / 名称" prop="title">
          <el-input v-model="form.title" maxlength="200" />
        </el-form-item>

        <!-- 新增时的类型切换 -->
        <el-form-item v-if="!editing" label="资产类型">
          <el-radio-group v-model="assetKind">
            <el-radio-button value="link">链接资产</el-radio-button>
            <el-radio-button value="file">文件资产</el-radio-button>
          </el-radio-group>
          <div class="form-hint">
            {{ assetKind === 'link' ? '填写博客 / 项目 / 仓库等可点击跳转的链接' : '上传成绩单、证书等文件到本地归档' }}
          </div>
        </el-form-item>

        <template v-if="(!editing && assetKind === 'link') || (editing && form.url)">
          <el-form-item label="链接地址">
            <el-input v-model="form.url" placeholder="https://…" />
          </el-form-item>
        </template>

        <template v-if="!editing && assetKind === 'file'">
          <el-form-item label="上传文件" required>
            <div class="upload-box" @click="pickFile">
              <input ref="fileInput" type="file" class="hidden" @change="onFilePick" />
              <el-icon :size="22"><UploadFilled /></el-icon>
              <span>{{ fileName || '点击选择文件（PDF / 图片 / 压缩包）' }}</span>
            </div>
          </el-form-item>
        </template>

        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
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
import { createAsset, deleteAsset, listAssets, updateAsset, uploadAsset } from '@/api'
import type { Asset } from '@/types'
import { ASSET_CATEGORIES } from '@/constants'
import { fmtRelative, baseName } from '@/utils/format'
import { openDownload } from '@/utils/download'

const items = ref<Asset[]>([])
const all = ref<Asset[]>([])
const loading = ref(false)
const filterCat = ref('')
const keyword = ref('')
let timer: ReturnType<typeof setTimeout> | null = null

function debouncedLoad() {
  if (timer) clearTimeout(timer)
  timer = setTimeout(load, 350)
}
async function load() {
  loading.value = true
  try {
    all.value = await listAssets({ category: filterCat.value || undefined, keyword: keyword.value || undefined })
    items.value = all.value
  } finally {
    loading.value = false
  }
}

/* ---- 表单 ---- */
interface AssetForm {
  category: string
  title: string
  url: string
  description: string
  tags: string[]
}

const formVisible = ref(false)
const editing = ref<Asset | null>(null)
const saving = ref(false)
const formRef = ref<FormInstance>()
const assetKind = ref<'link' | 'file'>('link')
const fileName = ref('')
const fileInput = ref<HTMLInputElement | null>(null)
const form = reactive<AssetForm>({
  category: 'blog',
  title: '',
  url: '',
  description: '',
  tags: [],
})
const rules: FormRules = {
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  title: [{ required: true, message: '请填写标题', trigger: 'blur' }],
}

function openCreate(kind: 'link' | 'file') {
  editing.value = null
  assetKind.value = kind
  fileName.value = ''
  Object.assign(form, { category: filterCat.value || 'blog', title: '', url: '', description: '', tags: [] })
  formVisible.value = true
}
function openEdit(a: Asset) {
  editing.value = a
  Object.assign(form, { category: a.category, title: a.title, url: a.url ?? '', description: a.description ?? '', tags: a.tags ?? [] })
  formVisible.value = true
}
function pickFile() {
  fileInput.value?.click()
}
function onFilePick(e: Event) {
  const input = e.target as HTMLInputElement
  fileName.value = input.files?.[0]?.name ?? ''
}
async function save() {
  await formRef.value?.validate()
  saving.value = true
  try {
    if (editing.value) {
      await updateAsset(editing.value.id, { ...form, url: form.url || undefined, title: form.title, category: form.category })
    } else if (assetKind.value === 'link') {
      if (!String(form.url).trim()) {
        ElMessage.warning('链接资产需要填写链接地址')
        return
      }
      await createAsset(form as Partial<Asset>)
    } else {
      const file = fileInput.value?.files?.[0]
      if (!file) {
        ElMessage.warning('请选择要上传的文件')
        return
      }
      await uploadAsset({
        category: String(form.category),
        title: String(form.title),
        description: String(form.description || ''),
        tags: JSON.stringify(form.tags),
        file,
      })
    }
    ElMessage.success('已保存')
    formVisible.value = false
    load()
  } catch {
    /* 拦截器已提示 */
  } finally {
    saving.value = false
  }
}
async function remove(a: Asset) {
  await ElMessageBox.confirm(`确定删除资产「${a.title}」？本地文件会一并移除。`, '删除资产', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteAsset(a.id)
  ElMessage.success('已删除')
  load()
}

function openUrl(a: Asset) {
  if (a.url) openDownload(a.url, '_blank')
}

onMounted(load)
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

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 14px;
}
.asset {
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
}
.a-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.aops {
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.2s;
}
.asset:hover .aops {
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
}
.op:hover {
  color: var(--accent-strong);
  background: var(--accent-soft);
}
.op.danger:hover {
  color: var(--danger);
  background: var(--danger-soft);
}
.a-title {
  margin: 10px 0 2px;
  font-size: 15px;
  font-weight: 650;
  color: var(--ink);
}
.a-desc {
  margin: 4px 0 0;
  font-size: 12.5px;
  color: var(--ink-3);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.a-link {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  padding: 8px 10px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: 8px;
  cursor: pointer;
  color: var(--accent-strong);
  transition: border-color 0.2s, background 0.2s;
}
.a-link:hover {
  border-color: var(--accent-line);
  background: var(--accent-soft);
}
.a-url {
  flex: 1;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.go {
  flex-shrink: 0;
  font-size: 12px;
}
.a-file {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  padding: 8px 10px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 12.5px;
  color: var(--ink-2);
}
.local {
  margin-left: auto;
  font-size: 11px;
  color: var(--ink-3);
}
.a-none {
  margin-top: 10px;
  font-size: 12px;
}
.a-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}
.a-foot {
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px dashed var(--line);
  font-size: 11.5px;
  color: var(--ink-3);
  margin-top: 14px;
}
.upload-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 26px 16px;
  border: 1.5px dashed var(--line-strong);
  border-radius: 10px;
  color: var(--ink-3);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.upload-box:hover {
  border-color: var(--accent-line);
  color: var(--accent-strong);
  background: var(--accent-soft);
}
.hidden {
  display: none;
}
</style>
