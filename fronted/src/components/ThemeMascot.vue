<!-- 主题吉祥物：随外观设置的主题风格自动切换（线条小狗 / 蜡笔小新） -->
<template>
  <LineDog v-if="kind === 'dog'" :pose="pose" :size="size" :className="className" />
  <ShinBoy v-else-if="kind === 'shin'" :pose="pose" :size="size" :className="className" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppearanceStore } from '@/stores/appearance'
import LineDog from './LineDog.vue'
import ShinBoy from './ShinBoy.vue'

const props = withDefaults(
  defineProps<{
    pose?: 'sit' | 'wave' | 'zzz'
    size?: number
    className?: string
  }>(),
  { pose: 'sit', size: 88 },
)

const appearance = useAppearanceStore()
const kind = computed(() => appearance.mascot)

defineOptions({ name: 'ThemeMascot' })
void props
</script>