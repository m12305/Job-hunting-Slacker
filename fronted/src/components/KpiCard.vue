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
  --kpi-tone: var(--line-strong);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-lg);
  padding: 20px 20px 18px 24px;
  position: relative;
  overflow: hidden;
}
.kpi::before {
  content: '';
  position: absolute;
  width: 88px;
  height: 88px;
  right: -42px;
  top: -42px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--kpi-tone) 16%, transparent);
}
.kpi::after {
  content: '';
  position: absolute;
  width: 4px;
  height: 34px;
  left: 11px;
  top: 20px;
  border-radius: 4px;
  background: var(--kpi-tone);
}
.kpi.tone-accent {
  --kpi-tone: var(--accent);
}
.kpi.tone-ok {
  --kpi-tone: var(--ok);
}
.kpi.tone-warn {
  --kpi-tone: var(--warn);
}
.kpi.tone-danger {
  --kpi-tone: var(--danger);
}
.kpi-label {
  position: relative;
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
  position: relative;
  margin-top: 8px;
  font-family: var(--font-mono);
  font-size: 30px;
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
  position: relative;
  margin-top: 6px;
  font-size: 11.5px;
  color: var(--ink-3);
}
</style>
