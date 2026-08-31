<template>
  <span class="status-tag" :style="{ color: entry?.dot, background: tint }">
    <span class="dot" :style="{ background: entry?.dot }" />
    {{ entry?.label ?? (value || '—') }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DictEntry } from '@/constants'

const props = defineProps<{
  dict?: Record<string, DictEntry>
  value: string | null | undefined
}>()

const entry = computed(() => (props.dict && props.value ? props.dict[props.value] : undefined))

/* 语义色 → 10% 浅底 */
const tint = computed(() => {
  const c = entry.value?.dot
  if (!c) return 'transparent'
  return `${c}1a`
})
</script>

<style scoped>
.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 9px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 550;
  line-height: 1.6;
  white-space: nowrap;
}
</style>