<template>
  <div class="page-head">
    <div>
      <div v-if="kicker" class="kicker">{{ kicker }}</div>
      <h2 class="title">{{ title }}</h2>
      <p v-if="desc" class="desc">{{ desc }}</p>
    </div>
    <div v-if="$slots.actions" class="actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  desc?: string
  kicker?: string
}>()
</script>

<style scoped>
.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}
.kicker {
  font-size: 11px;
  letter-spacing: 0.16em;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 4px;
}
.title {
  margin: 0;
  font-size: 21px;
  font-weight: 700;
  letter-spacing: -0.015em;
  color: var(--ink);
  line-height: 1.3;
}
.desc {
  margin: 6px 0 0;
  font-size: 13px;
  color: var(--ink-3);
  max-width: 60ch;
}
.actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
@media (max-width: 860px) {
  .page-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>