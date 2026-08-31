<template>
  <div class="tag-input">
    <el-tag
      v-for="(t, i) in modelValue"
      :key="`${t}-${i}`"
      class="tag"
      effect="plain"
      closable
      @close="remove(i)"
    >
      {{ t }}
    </el-tag>
    <input
      v-if="editing"
      ref="inputRef"
      v-model="draft"
      class="tag-editor"
      :placeholder="placeholder"
      @keyup.enter="commit"
      @keyup.esc="cancel"
      @blur="commit"
    />
    <button v-else class="tag-add" @click="startEdit">
      <el-icon :size="12"><Plus /></el-icon>
      <span>{{ placeholder }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { nextTick, ref } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: string[]
    placeholder?: string
  }>(),
  { placeholder: '添加标签' },
)

const emit = defineEmits<{ (e: 'update:modelValue', v: string[]): void }>()

const editing = ref(false)
const draft = ref('')
const inputRef = ref<HTMLInputElement | null>(null)

function startEdit() {
  editing.value = true
  nextTick(() => inputRef.value?.focus())
}

function commit() {
  const val = draft.value.trim()
  if (val && !props.modelValue.includes(val)) {
    emit('update:modelValue', [...props.modelValue, val])
  }
  draft.value = ''
  editing.value = false
}

function cancel() {
  draft.value = ''
  editing.value = false
}

function remove(i: number) {
  const next = [...props.modelValue]
  next.splice(i, 1)
  emit('update:modelValue', next)
}
</script>

<style scoped>
.tag-input {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}
.tag {
  border-radius: 6px;
}
.tag-editor {
  border: 1px solid var(--line-strong);
  border-radius: 6px;
  padding: 3px 8px;
  font-size: 12.5px;
  font-family: inherit;
  width: 110px;
  outline: none;
  background: var(--surface);
  color: var(--ink);
}
.tag-editor:focus {
  border-color: var(--accent);
}
.tag-add {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px dashed var(--line-strong);
  border-radius: 6px;
  background: transparent;
  color: var(--ink-3);
  font-size: 12px;
  font-family: inherit;
  padding: 3px 9px;
  cursor: pointer;
  transition: all 0.2s;
}
.tag-add:hover {
  color: var(--accent-strong);
  border-color: var(--accent-line);
  background: var(--accent-soft);
}
</style>