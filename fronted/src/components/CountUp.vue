<template>
  <span class="countup">{{ display }}</span>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    to: number
    decimals?: number
    suffix?: string
    duration?: number
  }>(),
  { decimals: 0, suffix: '', duration: 700 },
)

const current = ref(0)
let raf = 0

function animate() {
  cancelAnimationFrame(raf)
  const start = performance.now()
  const from = 0
  const delta = props.to - from
  const step = (now: number) => {
    const t = Math.min(1, (now - start) / props.duration)
    const eased = 1 - Math.pow(1 - t, 3)
    current.value = from + delta * eased
    if (t < 1) raf = requestAnimationFrame(step)
  }
  raf = requestAnimationFrame(step)
}

watch(
  () => props.to,
  () => animate(),
  { immediate: true },
)

onBeforeUnmount(() => cancelAnimationFrame(raf))

const display = computed(() => {
  const v = current.value.toFixed(props.decimals)
  return props.decimals === 0 ? Number(v).toLocaleString('zh-CN') + props.suffix : v + props.suffix
})
</script>

<style scoped>
.countup {
  font-variant-numeric: tabular-nums;
}
</style>