<template>
  <div class="empty" :class="{ row: showMascot }">
    <div v-if="showMascot" class="empty-mascot dog-wiggle">
      <ThemeMascot :pose="pose" :size="86" />
      <span class="dog-badge"><el-icon><component :is="icon" /></el-icon></span>
    </div>
    <div v-else class="empty-icon">
      <el-icon :size="26"><component :is="icon" /></el-icon>
    </div>
    <div class="empty-body">
      <div class="empty-title">{{ title }}</div>
      <div v-if="desc" class="empty-desc">{{ desc }}</div>
      <div v-if="$slots.action" class="empty-action">
        <slot name="action" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppearanceStore } from '@/stores/appearance'
import ThemeMascot from './ThemeMascot.vue'

const props = withDefaults(
  defineProps<{
    icon?: string
    title: string
    desc?: string
    /** 用主题吉祥物当空态插画（原始主题下自动回退为图标） */
    mascot?: boolean
    /** 吉祥物姿势；原始主题下自动忽略 */
    pose?: 'sit' | 'wave' | 'zzz'
  }>(),
  { icon: 'FolderOpened', mascot: true, pose: 'sit' },
)

const appearance = useAppearanceStore()
const showMascot = computed(() => props.mascot && appearance.mascot !== 'none')
</script>

<style scoped>
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 42px 24px;
  text-align: center;
}
.empty.row {
  flex-direction: row;
  gap: 22px;
  text-align: left;
}
.empty-mascot {
  position: relative;
  flex-shrink: 0;
}
.dog-badge {
  position: absolute;
  right: -6px;
  bottom: -4px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--accent-soft);
  border: 1.5px solid var(--accent-line);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-strong);
  font-size: 13px;
}
.empty-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--ink-3);
  margin-bottom: 14px;
}
.empty-body {
  min-width: 0;
}
.empty-title {
  font-size: 14.5px;
  font-weight: 600;
  color: var(--ink-2);
}
.empty-desc {
  font-size: 12.5px;
  color: var(--ink-3);
  margin-top: 6px;
  max-width: 40ch;
  line-height: 1.7;
}
.empty-action {
  margin-top: 14px;
}
@media (max-width: 640px) {
  .empty.row {
    flex-direction: column;
    text-align: center;
  }
}
</style>