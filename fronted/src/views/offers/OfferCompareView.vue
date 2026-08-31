<template>
  <div class="page">
    <PageHeader
      kicker="MODULE 02 · Offer 决策"
      title="Offer 对比决策"
      desc="勾选多个 Offer，按可调权重自动打分排序并生成雷达图；权重可临时调整，也可保存为全局配置。"
    >
      <template #actions>
        <el-button @click="router.push('/offers')"><el-icon><Back /></el-icon>&nbsp;返回 Offer 管理</el-button>
      </template>
    </PageHeader>

    <div class="compare-layout">
      <!-- 左：选择与权重 -->
      <aside class="side panel">
        <div class="side-title">
          选择对比的 Offer
          <el-button size="small" text type="primary" :disabled="!selected.length" @click="selected = []">清空</el-button>
        </div>

        <div class="offer-check-list">
          <button
            v-for="o in offers"
            :key="o.id"
            class="check-row"
            :class="{ checked: selected.includes(o.id) }"
            @click="toggle(o.id)"
          >
            <span class="box"><el-icon v-if="selected.includes(o.id)"><Check /></el-icon></span>
            <span class="co">{{ o.company }}</span>
            <span v-if="o.salary_base != null" class="mono cb">{{ o.salary_base }}K×{{ o.salary_months || 12 }}</span>
          </button>
          <div v-if="!offers.length" class="side-empty muted">
            暂无 Offer，请先到「Offer 管理」录入。
          </div>
        </div>

        <el-divider />

        <div class="side-title">维度权重（本页临时调整）</div>
        <div class="weight-list">
          <div v-for="w in weights" :key="w.dimension_key" class="weight-row">
            <div class="w-head">
              <el-switch v-model="w.enabled" size="small" />
              <span class="w-name" :class="{ off: !w.enabled }">{{ w.dimension_name }}</span>
              <span class="mono w-val">{{ w.weight.toFixed(2) }}</span>
            </div>
            <el-slider
              v-model="w.weight"
              :min="0"
              :max="1"
              :step="0.05"
              :disabled="!w.enabled"
              size="small"
            />
          </div>
          <div v-if="!weights.length" class="side-empty muted">
            权重配置异常，请到设置页检查。
          </div>
        </div>

        <div class="side-actions">
          <el-button type="primary" :loading="comparing" :disabled="selected.length < 2" class="go-btn" @click="runCompare">
            <el-icon><DataAnalysis /></el-icon>&nbsp;开始对比（已选 {{ selected.length }} 个）
          </el-button>
          <el-button :loading="savingWeights" @click="saveWeights">保存权重</el-button>
        </div>
      </aside>

      <!-- 右：结果 -->
      <main class="result">
        <el-skeleton v-if="comparing" :rows="8" animated class="panel" style="padding: 20px" />

        <div v-else-if="!result" class="panel idle">
          <EmptyState
            icon="DataAnalysis"
            title="还没有对比结果"
            desc="在左侧勾选至少 2 个 Offer，调整每个维度的权重大小，点击「开始对比」生成推荐排序与雷达图。"
          />
        </div>

        <div v-else class="result-wrap">
          <!-- 推荐排序 -->
          <section class="panel rank-panel">
            <div class="section-title">推荐排序</div>
            <div class="rank-list">
              <div
                v-for="r in sortedResults"
                :key="r.offer_id"
                class="rank-row"
                :class="{ top: r.recommended }"
              >
                <span class="mono rank-no">{{ r.rank }}</span>
                <div class="rank-main">
                  <div class="rank-head">
                    <span class="rank-company">{{ r.company }}</span>
                    <el-tag v-if="r.recommended" type="warning" size="small" effect="dark">最优推荐</el-tag>
                  </div>
                  <div class="rank-sub muted">{{ r.position || '—' }}<template v-if="r.city"> · {{ r.city }}</template></div>
                  <div class="rank-bars">
                    <div v-for="(v, key) in r.scores" :key="key" class="bar-line">
                      <span class="bar-label">{{ dimName(key) }}</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: v + '%' }" /></div>
                      <span class="mono bar-val">{{ v }}</span>
                    </div>
                  </div>
                </div>
                <div class="rank-total">
                  <span class="mono total-num">{{ r.total }}</span>
                  <span class="total-label">综合分</span>
                </div>
              </div>
            </div>
          </section>

          <!-- 雷达图 -->
          <section class="panel chart-panel">
            <div class="section-title">维度得分雷达</div>
            <div ref="radarEl" class="radar" />
            <div v-if="!radarKeys.length" class="radar-empty muted">所选 Offer 的得分维度不足以绘制雷达图</div>
          </section>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { EChartsOption } from 'echarts'
import PageHeader from '@/components/PageHeader.vue'
import EmptyState from '@/components/EmptyState.vue'
import { useEcharts } from '@/composables/useEcharts'
import { useAppearanceStore } from '@/stores/appearance'
import { compareOffers, getWeightConfig, listOffers, updateWeightConfig } from '@/api'
import type { Offer, OfferCompareResult, OfferWeight } from '@/types'
import { DIMENSION_NAMES } from '@/constants'

const appearance = useAppearanceStore()
const router = useRouter()

const offers = ref<Offer[]>([])
const selected = ref<number[]>([])
const weights = ref<OfferWeight[]>([])
const result = ref<OfferCompareResult | null>(null)
const comparing = ref(false)
const savingWeights = ref(false)

const radarEl = ref<HTMLDivElement | null>(null)

const dimName = (key: string) => DIMENSION_NAMES[key] ?? key

const sortedResults = computed(() => (result.value ? [...result.value.results].sort((a, b) => a.rank - b.rank) : []))

const radarKeys = computed(() => {
  if (!result.value) return []
  const keys = new Set<string>()
  for (const r of result.value.results) {
    for (const k of Object.keys(r.scores)) keys.add(k)
  }
  return [...keys].map((k) => dimName(k))
})

function toggle(id: number) {
  const i = selected.value.indexOf(id)
  if (i >= 0) selected.value.splice(i, 1)
  else selected.value.push(id)
}

function buildOverrides() {
  const overrides: Record<string, { weight: number; enabled: boolean }> = {}
  for (const w of weights.value) {
    overrides[w.dimension_key] = { weight: Number(w.weight.toFixed(2)), enabled: w.enabled }
  }
  return overrides
}

async function runCompare() {
  if (selected.value.length < 2) {
    ElMessage.warning('至少选择 2 个 Offer 才能对比')
    return
  }
  comparing.value = true
  try {
    result.value = await compareOffers({ offer_ids: [...selected.value], weight_overrides: buildOverrides() })
  } finally {
    comparing.value = false
  }
}

async function saveWeights() {
  savingWeights.value = true
  try {
    await updateWeightConfig(
      weights.value.map((w, i) => ({
        dimension_key: w.dimension_key,
        dimension_name: w.dimension_name,
        weight: Number(w.weight.toFixed(2)),
        enabled: w.enabled,
        sort_order: i,
      })),
    )
    ElMessage.success('权重配置已保存')
  } finally {
    savingWeights.value = false
  }
}

/* 雷达图 */
useEcharts(
  radarEl,
  (): EChartsOption => {
    const keys = radarKeys.value
    const series = sortedResults.value.map((r, i) => ({
      name: r.company,
      value: keys.map((k) => {
        const entry = Object.entries(r.scores).find(([key]) => dimName(key) === k)
        return entry ? entry[1] : 0
      }),
      lineStyle: { width: 2 },
      areaStyle: { opacity: 0.08 },
      itemStyle: { opacity: 0.9 },
    }))
    return {
      tooltip: { trigger: 'item' },
      legend: { bottom: 0, textStyle: { color: '#57524c', fontFamily: 'Noto Sans SC' } },
      radar: {
        indicator: keys.map((k) => ({ name: k, max: 100 })),
        radius: '64%',
        center: ['50%', '46%'],
        axisName: { color: '#57524c', fontFamily: 'Noto Sans SC', fontSize: 11 },
        splitArea: { areaStyle: { color: ['#fbfaf7', '#f5f3ee'] } },
        splitLine: { lineStyle: { color: '#e6e3dc' } },
        axisLine: { lineStyle: { color: '#d7d3ca' } },
      },
      series: [{ type: 'radar', data: series }],
      color: [appearance.accent, appearance.accent2, '#0369a1', '#6d28d9', '#b7791f', '#9f1239', '#1a7f5c', '#57534e'],
    }
  },
)

onMounted(async () => {
  offers.value = await listOffers()
  weights.value = await getWeightConfig()
})
</script>

<style scoped>
.compare-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 16px;
  align-items: start;
}
@media (max-width: 980px) {
  .compare-layout {
    grid-template-columns: 1fr;
  }
}

.side {
  padding: 16px;
  position: sticky;
  top: 0;
}
.side-title {
  font-size: 12px;
  letter-spacing: 0.1em;
  color: var(--ink-3);
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.offer-check-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 260px;
  overflow-y: auto;
}
.check-row {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 8px 10px;
  border: 1px solid var(--line);
  border-radius: 9px;
  background: var(--surface);
  font-family: inherit;
  font-size: 12.5px;
  color: var(--ink-2);
  cursor: pointer;
  text-align: left;
  transition: all 0.18s;
}
.check-row:hover {
  border-color: var(--line-strong);
}
.check-row.checked {
  border-color: var(--accent-line);
  background: var(--accent-soft);
}
.box {
  width: 16px;
  height: 16px;
  border-radius: 5px;
  border: 1.5px solid var(--line-strong);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 11px;
  flex-shrink: 0;
  background: var(--surface);
}
.check-row.checked .box {
  background: var(--accent);
  border-color: var(--accent);
}
.co {
  flex: 1;
  font-weight: 550;
}
.cb {
  font-size: 11.5px;
  color: var(--ink-3);
}
.side-empty {
  font-size: 12px;
  padding: 8px 2px;
}

.weight-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.weight-row {
  padding: 6px 2px;
}
.w-head {
  display: flex;
  align-items: center;
  gap: 8px;
}
.w-name {
  flex: 1;
  font-size: 12.5px;
  color: var(--ink);
}
.w-name.off {
  color: var(--ink-4);
}
.w-val {
  font-size: 11.5px;
  color: var(--accent-strong);
}
.side-actions {
  display: flex;
  gap: 8px;
  margin-top: 14px;
  flex-direction: column;
}
.go-btn {
  width: 100%;
}

.result-wrap {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 16px;
  align-items: start;
}
@media (max-width: 980px) {
  .result-wrap {
    grid-template-columns: 1fr;
  }
}
.section-title {
  font-size: 12px;
  letter-spacing: 0.1em;
  color: var(--ink-3);
  font-weight: 600;
  margin-bottom: 12px;
}
.rank-panel,
.chart-panel {
  padding: 18px;
}
.idle {
  min-height: 380px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.rank-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 12px 14px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--surface);
  transition: all 0.2s;
}
.rank-row.top {
  border-color: var(--accent-line);
  background: linear-gradient(180deg, var(--accent-soft) 0%, var(--surface) 120%);
  box-shadow: var(--shadow-1);
}
.rank-no {
  font-size: 22px;
  font-weight: 700;
  color: var(--ink-4);
  min-width: 34px;
  padding-top: 2px;
}
.rank-row.top .rank-no {
  color: var(--accent);
}
.rank-main {
  flex: 1;
  min-width: 0;
}
.rank-head {
  display: flex;
  align-items: center;
  gap: 8px;
}
.rank-company {
  font-size: 14.5px;
  font-weight: 650;
  color: var(--ink);
}
.rank-sub {
  font-size: 12px;
  margin-top: 1px;
}
.rank-bars {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 4px 12px;
  margin-top: 10px;
}
.bar-line {
  display: flex;
  align-items: center;
  gap: 6px;
}
.bar-label {
  font-size: 11px;
  color: var(--ink-3);
  width: 48px;
  flex-shrink: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.bar-track {
  flex: 1;
  height: 5px;
  background: var(--surface-3);
  border-radius: 4px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 4px;
  transition: width 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
.rank-row.top .bar-fill {
  background: linear-gradient(90deg, var(--accent) 0%, #d97706 100%);
}
.bar-val {
  font-size: 10.5px;
  color: var(--ink-4);
  width: 24px;
  text-align: right;
}
.rank-total {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 62px;
}
.total-num {
  font-size: 24px;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.02em;
}
.rank-row.top .total-num {
  color: var(--accent-strong);
}
.total-label {
  font-size: 10.5px;
  color: var(--ink-3);
}

.radar {
  height: 360px;
  width: 100%;
}
.radar-empty {
  text-align: center;
  font-size: 12.5px;
  padding: 24px;
}
</style>