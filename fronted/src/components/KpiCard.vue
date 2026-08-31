<template>
  <div class="kpi card-hover" :class="`tone-${tone}`">
    <div class="kpi-label">
      {{ label }}
      <el-tooltip v-if="hint" :content="hint" placement="top">
        <el-icon class="hint-icon"><QuestionFilled /></el-icon>
      </el-tooltip>
    </div>
    <div class="kpi-value">
      <CountUp v-if="typeof value === 'number'" :to="value" :decimals="decimals" :suffix="suffix" />
      <template v-else>{{ value }}<span v-if="suffix" class="kpi-suffix">{{ suffix }}</span></template>
    </div>
    <div v-if="note" class="kpi-note">{{ note }}</div>
  </div>
</template>

<script setup lang="ts">
import CountUp from './CountUp.vue'

withDefaults(
  defineProps<{
    label: string
    value: number | string
    suffix?: string
    decimals?: number
    hint?: string
    note?: string
    tone?: 'default' | 'accent' | 'ok' | 'warn' | 'danger'
  }>(),
  {
    suffix: '',
    decimals: 0,
    note: '',
    tone: 'default',
  },
)
</script>

<style scoped>
.kpi {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-lg);
  padding: 18px 20px 16px;
  position: relative;
  overflow: hidden;
}
.kpi::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--line);
}
.kpi.tone-accent::before {
  background: var(--accent);
}
.kpi.tone-ok::before {
  background: var(--ok);
}
.kpi.tone-warn::before {
  background: var(--warn);
}
.kpi.tone-danger::before {
  background: var(--danger);
}
.kpi-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12.5px;
  color: var(--ink-3);
  font-weight: 550;
}
.hint-icon {
  cursor: help;
  color: var(--ink-4);
}
.kpi-value {
  margin-top: 8px;
  font-family: var(--font-mono);
  font-size: 27px;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--ink);
  line-height: 1.15;
}
.kpi-suffix {
  font-size: 14px;
  color: var(--ink-2);
  margin-left: 2px;
}
.kpi-note {
  margin-top: 6px;
  font-size: 11.5px;
  color: var(--ink-3);
}
</style>