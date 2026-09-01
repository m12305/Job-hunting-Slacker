<template>
  <div class="page-head">
    <div class="page-head-copy">
      <div v-if="kicker" class="kicker">{{ kicker }}</div>
      <h2 class="title">{{ title }}</h2>
      <p v-if="desc" class="desc">{{ desc }}</p>
    </div>
    <div v-if="appearance.mascot !== 'none'" class="page-head-art" aria-hidden="true">
      <span class="art-spark one" />
      <span class="art-spark two" />
      <ThemeMascot pose="wave" :size="106" />
    </div>
    <div v-if="$slots.actions" class="actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import ThemeMascot from './ThemeMascot.vue'
import { useAppearanceStore } from '@/stores/appearance'

defineProps<{
  title: string
  desc?: string
  kicker?: string
}>()

const appearance = useAppearanceStore()
</script>

<style scoped>
.page-head {
  display: flex;
  align-items: center;
  gap: 20px;
  min-height: 112px;
  margin-bottom: 22px;
  padding: 20px 22px;
  border: 1px solid var(--line);
  border-radius: var(--r-xl, 24px);
  background:
    radial-gradient(circle at 88% 20%, color-mix(in srgb, var(--accent) 10%, transparent), transparent 28%),
    color-mix(in srgb, var(--surface) 92%, var(--accent-soft));
  box-shadow: var(--shadow-1);
  overflow: hidden;
  position: relative;
}
.page-head::after {
  content: '';
  position: absolute;
  width: 180px;
  height: 180px;
  border: 1px dashed var(--accent-line);
  border-radius: 50%;
  right: 86px;
  top: -96px;
  opacity: 0.55;
  pointer-events: none;
}
.page-head-copy {
  flex: 1;
  min-width: 0;
}
.kicker {
  font-size: 11.5px;
  letter-spacing: 0.08em;
  color: var(--accent-strong);
  font-weight: 700;
  margin-bottom: 5px;
}
.title {
  margin: 0;
  font-size: clamp(22px, 2vw, 29px);
  font-weight: 760;
  letter-spacing: -0.03em;
  color: var(--ink);
  line-height: 1.2;
}
.desc {
  margin: 8px 0 0;
  font-size: 13px;
  color: var(--ink-2);
  max-width: 62ch;
  line-height: 1.7;
}
.page-head-art {
  width: 112px;
  height: 74px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
  z-index: 1;
}
.page-head-art::before {
  content: '';
  position: absolute;
  width: 92px;
  height: 62px;
  border-radius: 50%;
  background: var(--accent-soft);
  transform: rotate(-7deg);
}
.art-spark {
  position: absolute;
  width: 9px;
  height: 9px;
  background: var(--accent-2);
  clip-path: polygon(50% 0, 61% 39%, 100% 50%, 61% 61%, 50% 100%, 39% 61%, 0 50%, 39% 39%);
  z-index: 2;
}
.art-spark.one {
  top: 1px;
  right: 2px;
}
.art-spark.two {
  width: 6px;
  height: 6px;
  left: 0;
  bottom: 5px;
}
.actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  z-index: 1;
}
@media (max-width: 860px) {
  .page-head {
    min-height: 0;
    padding: 18px;
    flex-wrap: wrap;
    align-items: flex-start;
  }
  .page-head-art {
    position: absolute;
    right: 8px;
    top: 8px;
    opacity: 0.25;
  }
  .actions {
    width: 100%;
  }
}
</style>
