<template>
  <span
    v-if="resolvedKind !== 'none'"
    class="theme-mascot"
    :class="[`is-${resolvedKind}`, `pose-${pose}`, className]"
    :style="{ width: `${size}px`, height: `${Math.round(size * 0.76)}px` }"
  >
    <img :src="src" :alt="alt" draggable="false" />
    <span v-if="pose === 'zzz'" class="sleep-marks" aria-hidden="true"><i>Z</i><i>z</i></span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppearanceStore } from '@/stores/appearance'
import lineDogPair from '@/assets/themes/line-dog-pair.png'
import shinchanFace from '@/assets/themes/shinchan-face.png'

const props = withDefaults(
  defineProps<{
    pose?: 'sit' | 'wave' | 'zzz'
    size?: number
    className?: string
    /** 外观预览卡可指定角色；未传时跟随全局主题。 */
    kind?: 'none' | 'dog' | 'shin'
  }>(),
  { pose: 'sit', size: 88, className: '', kind: undefined },
)

const appearance = useAppearanceStore()
const resolvedKind = computed(() => props.kind ?? appearance.mascot)
const src = computed(() => (resolvedKind.value === 'shin' ? shinchanFace : lineDogPair))
const alt = computed(() => (resolvedKind.value === 'shin' ? '蜡笔小新' : '线条小狗'))

defineOptions({ name: 'ThemeMascot' })
</script>

<style scoped>
.theme-mascot {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transform-origin: 50% 85%;
}
.theme-mascot img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 8px 12px rgba(70, 51, 30, 0.08));
  user-select: none;
}
.theme-mascot.is-shin img {
  transform: scale(1.12);
}
.theme-mascot.pose-zzz {
  transform: rotate(-4deg) translateY(2px);
}
.sleep-marks {
  position: absolute;
  right: -4%;
  top: -10%;
  display: flex;
  align-items: flex-start;
  gap: 2px;
  color: var(--accent-strong);
  font-family: var(--font-mono);
  font-weight: 800;
  line-height: 1;
}
.sleep-marks i {
  font-style: normal;
  font-size: 12px;
}
.sleep-marks i + i {
  margin-top: -7px;
  font-size: 9px;
}
@media (prefers-reduced-motion: no-preference) {
  .theme-mascot.pose-wave {
    animation: mascot-hello 2.8s cubic-bezier(0.16, 1, 0.3, 1) infinite;
  }
}
@keyframes mascot-hello {
  0%,
  72%,
  100% {
    transform: rotate(0deg) translateY(0);
  }
  78% {
    transform: rotate(-3deg) translateY(-3px);
  }
  86% {
    transform: rotate(2deg) translateY(-1px);
  }
}
</style>
