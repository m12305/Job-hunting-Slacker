<template>
  <el-dialog
    :model-value="modelValue"
    title="管理岗位类型"
    width="560px"
    destroy-on-close
    @update:model-value="(v: boolean) => emit('update:modelValue', v)"
  >
    <p class="hint">岗位类型用于组织简历版本与投递数据；删除前需先迁移或删除该类型下的简历。</p>

    <div class="type-list">
      <div v-for="jt in list" :key="jt.id" class="type-row">
        <span class="dot" :style="{ background: jt.color || '#8f8a83' }" />
        <span class="tname">{{ jt.name }}</span>
        <span class="mono torder">#{{ jt.sort_order }}</span>
        <div class="tops">
          <button class="top" @click="openEdit(jt)"><el-icon><Edit /></el-icon></button>
          <button class="top danger" @click="remove(jt)"><el-icon><Delete /></el-icon></button>
        </div>
      </div>
      <EmptyState v-if="!list.length" icon="Collection" title="暂无岗位类型" desc="点击下方按钮创建第一个岗位类型。" />
    </div>

    <template #footer>
      <el-button @click="emit('update:modelValue', false)">关闭</el-button>
      <el-button type="primary" @click="openCreate"><el-icon><Plus /></el-icon>&nbsp;新增岗位类型</el-button>
    </template>

    <!-- 编辑窗口 -->
    <el-dialog
      v-model="editVisible"
      :title="editing ? '编辑岗位类型' : '新增岗位类型'"
      width="min(420px, calc(100vw - 24px))"
      class="viewport-dialog"
      append-to-body
      destroy-on-close
      top="2vh"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" maxlength="50" placeholder="如 数据岗 / 前端岗" />
        </el-form-item>
        <el-form-item label="标记色">
          <div class="colors">
            <button
              v-for="c in PRESET_COLORS"
              :key="c"
              class="color-dot"
              :class="{ active: form.color === c }"
              :style="{ background: c }"
              @click="form.color = c"
            />
          </div>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" :max="99" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import EmptyState from '@/components/EmptyState.vue'
import { createJobType, deleteJobType, listJobTypes, updateJobType } from '@/api'
import type { JobType } from '@/types'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void; (e: 'changed', force: boolean): void }>()

const PRESET_COLORS = ['#b45309', '#0369a1', '#0f766e', '#6d28d9', '#b7791f', '#1a7f5c', '#9f1239', '#57534e']

const list = ref<JobType[]>([])
const visible = ref(props.modelValue)

const editVisible = ref(false)
const editing = ref<JobType | null>(null)
const saving = ref(false)
const formRef = ref<FormInstance>()
const form = reactive<{ name: string; color: string | null; sort_order: number }>({
  name: '',
  color: PRESET_COLORS[0],
  sort_order: 0,
})
const rules: FormRules = {
  name: [{ required: true, message: '请填写名称', trigger: 'blur' }],
}

async function load() {
  list.value = await listJobTypes()
}
function openCreate() {
  editing.value = null
  Object.assign(form, { name: '', color: PRESET_COLORS[0], sort_order: list.value.length })
  editVisible.value = true
}
function openEdit(jt: JobType) {
  editing.value = jt
  Object.assign(form, { name: jt.name, color: jt.color ?? PRESET_COLORS[0], sort_order: jt.sort_order })
  editVisible.value = true
}
async function save() {
  await formRef.value?.validate()
  saving.value = true
  try {
    if (editing.value) await updateJobType(editing.value.id, form)
    else await createJobType(form)
    ElMessage.success('已保存')
    editVisible.value = false
    await load()
    emit('changed', true)
  } finally {
    saving.value = false
  }
}
async function remove(jt: JobType) {
  try {
    await ElMessageBox.confirm(`确定删除岗位类型「${jt.name}」？`, '删除岗位类型', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteJobType(jt.id)
    ElMessage.success('已删除')
    await load()
    emit('changed', true)
  } catch {
    /* 409 提示已由拦截器显示 */
  }
}

onMounted(() => {
  if (props.modelValue) load()
})
</script>

<style scoped>
.hint {
  font-size: 12.5px;
  color: var(--ink-3);
  margin: 0 0 14px;
}
.type-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 320px;
  overflow-y: auto;
}
.type-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--surface);
}
.tname {
  font-weight: 600;
  font-size: 13.5px;
  flex: 1;
}
.torder {
  font-size: 11.5px;
  color: var(--ink-3);
}
.tops {
  display: flex;
  gap: 2px;
}
.top {
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
.top:hover {
  color: var(--accent-strong);
  background: var(--accent-soft);
}
.top.danger:hover {
  color: var(--danger);
  background: var(--danger-soft);
}
.colors {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.color-dot {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: transform 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}
.color-dot:hover {
  transform: scale(1.12);
}
.color-dot.active {
  border-color: var(--ink);
  box-shadow: 0 0 0 2px var(--surface);
}
</style>
