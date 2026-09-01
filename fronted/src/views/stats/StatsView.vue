<template>
  <div class="page">
    <PageHeader
      kicker="求职数据全景"
      title="数据看板"
      desc="实时聚合投递、笔试、面试和 Offer 数据，看清总盘面，也看清每个岗位方向的转化短板。"
    >
      <template #actions>
        <el-button @click="loadAll"><el-icon><Refresh /></el-icon>&nbsp;刷新数据</el-button>
      </template>
    </PageHeader>

    <!-- KPI 行 -->
    <el-skeleton v-if="loading" :rows="3" animated class="panel" style="padding: 20px" />
    <div v-else-if="overview" class="kpi-layout">
      <div class="kpi-primary">
        <KpiCard label="总投递数" :value="overview.total_applications" note="含待投递的全部记录" tone="default" />
        <KpiCard label="有效投递数" :value="overview.effective_applications" note="已投出及后续状态" tone="accent" />
      </div>
      <div class="kpi-rates">
        <KpiCard label="挂简历率" :value="overview.resume_rejected_rate" :decimals="1" suffix="%" tone="warn" hint="挂简历数 / 有效投递数" />
        <KpiCard label="笔试通过率" :value="overview.exam_pass_rate" :decimals="1" suffix="%" tone="ok" hint="通过复盘数 / 已复盘笔试数" />
        <KpiCard label="面试率" :value="overview.interview_rate" :decimals="1" suffix="%" tone="default" hint="进入面试数 / 有效投递数" />
        <KpiCard label="Offer 率" :value="overview.offer_rate" :decimals="1" suffix="%" tone="danger" hint="Offer 数 / 有效投递数" />
      </div>
    </div>
    <EmptyState v-else-if="!loading" icon="TrendCharts" title="暂无统计数据" desc="录入投递与笔面试数据后，这里会自动生成指标与图表。" />

    <div v-if="!loading && (jobStats.length || timeItems.length)" class="charts">
      <!-- 岗位维度 -->
      <section class="panel chart-card chart-wide">
        <div class="chart-head">
          <div>
            <div class="chart-title">岗位维度转化</div>
            <div class="chart-sub">各岗位类型的投递规模（柱）与环节通过率（线）</div>
          </div>
        </div>
        <div ref="jobChartEl" class="chart" v-if="jobStats.length" />
        <EmptyState v-else icon="DataLine" title="暂无岗位维度数据" desc="投递记录关联岗位类型后即可统计。" />
      </section>

      <!-- 时间维度 -->
      <section class="panel chart-card">
        <div class="chart-head">
          <div>
            <div class="chart-title">投递节奏</div>
            <div class="chart-sub">按时间粒度统计投递量</div>
          </div>
          <el-radio-group v-model="granularity" size="small" @change="loadTime">
            <el-radio-button value="day">日</el-radio-button>
            <el-radio-button value="week">周</el-radio-button>
            <el-radio-button value="month">月</el-radio-button>
          </el-radio-group>
        </div>
        <div ref="timeChartEl" class="chart" v-if="timeItems.length" />
        <EmptyState v-else icon="Timer" title="暂无时间维度数据" desc="填写投递时间后，这里会按真实投递日期统计。" />
      </section>
    </div>

    <section v-else-if="!loading && overview" class="panel stats-empty">
      <div class="stats-empty-copy">
        <span class="empty-label">还没有形成数据曲线</span>
        <h3>先记下第一份投递，趋势会从这里长出来</h3>
        <p>岗位类型和投递日期完整后，系统会自动生成转化漏斗与投递节奏。</p>
        <div class="empty-actions">
          <el-button type="primary" @click="router.push('/applications')">去录入投递</el-button>
          <el-button @click="router.push('/dashboard')">返回今日看板</el-button>
        </div>
        <div class="empty-checks">
          <span><el-icon><Check /></el-icon>公司与岗位</span>
          <span><el-icon><Check /></el-icon>岗位类型</span>
          <span><el-icon><Check /></el-icon>投递日期</span>
        </div>
      </div>
      <div class="stats-empty-art" aria-hidden="true">
        <ThemeMascot pose="wave" :size="260" />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { EChartsOption } from 'echarts'
import PageHeader from '@/components/PageHeader.vue'
import KpiCard from '@/components/KpiCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import ThemeMascot from '@/components/ThemeMascot.vue'
import { useEcharts, AXIS_LINE } from '@/composables/useEcharts'
import { useAppearanceStore } from '@/stores/appearance'
import { getStatsByJobType, getStatsByTime, getStatsOverview } from '@/api'
import type { JobTypeStat, StatsOverview } from '@/types'
import { fmtRate } from '@/utils/format'

const appearance = useAppearanceStore()
const router = useRouter()

const loading = ref(false)
const overview = ref<StatsOverview | null>(null)
const jobStats = ref<JobTypeStat[]>([])
const timeItems = ref<{ label: string; count: number }[]>([])
const granularity = ref<'day' | 'week' | 'month'>('week')

const jobChartEl = ref<HTMLDivElement | null>(null)
const timeChartEl = ref<HTMLDivElement | null>(null)

async function loadAll() {
  loading.value = true
  try {
    const [ov, jobs, time] = await Promise.all([
      getStatsOverview(),
      getStatsByJobType(),
      getStatsByTime({ granularity: granularity.value }),
    ])
    overview.value = ov
    jobStats.value = jobs
    timeItems.value = time.items
  } catch {
    /* 拦截器提示 */
  } finally {
    loading.value = false
  }
}

async function loadTime() {
  try {
    const time = await getStatsByTime({ granularity: granularity.value })
    timeItems.value = time.items
  } catch {
    /* 忽略 */
  }
}

/* 岗位维度：柱状（投递量） + 折线（通过率%） */
useEcharts(
  jobChartEl,
  (): EChartsOption => {
    const names = jobStats.value.map((j) => j.job_type)
    const rates = ['exam_rate', 'interview_rate', 'offer_rate'] as const
    const rateNames: Record<string, string> = { exam_rate: '笔试率', interview_rate: '面试率', offer_rate: 'Offer率' }
    return {
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['投递数', ...rates.map((r) => rateNames[r])],
        textStyle: { color: '#57524c', fontFamily: 'Noto Sans SC', fontSize: 11.5 },
        top: 0,
      },
      grid: { left: 40, right: 40, top: 40, bottom: 24 },
      xAxis: {
        type: 'category',
        data: names,
        ...AXIS_LINE,
        axisLabel: { color: '#57524c', fontFamily: 'Noto Sans SC' },
      },
      yAxis: [
        { type: 'value', name: '投递数', ...AXIS_LINE, axisLabel: { color: '#8f8a83' } },
        { type: 'value', name: '通过率 %', min: 0, max: 100, ...AXIS_LINE, axisLabel: { color: '#8f8a83', formatter: '{value}%' } },
      ],
      series: [
        {
          name: '投递数',
          type: 'bar',
          data: jobStats.value.map((j) => j.total_applications),
          barMaxWidth: 34,
          itemStyle: { color: appearance.accent, borderRadius: [6, 6, 0, 0] },
        },
        ...rates.map((r, i) => ({
          name: rateNames[r],
          type: 'line' as const,
          yAxisIndex: 1,
          smooth: true,
          symbol: 'circle',
          symbolSize: 7,
          lineStyle: { width: 2 },
          data: jobStats.value.map((j) => Math.round(j[r] * 1000) / 10),
        })),
      ],
      color: [appearance.accent2, '#0369a1', '#6d28d9', '#0f766e', '#9f1239', '#57534e'],
    }
  },
)

/* 时间维度：柱状 */
useEcharts(
  timeChartEl,
  (): EChartsOption => ({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 16, top: 20, bottom: 30 },
    xAxis: {
      type: 'category',
      data: timeItems.value.map((t) => t.label),
      ...AXIS_LINE,
      axisLabel: {
        color: '#57524c',
        fontFamily: 'Noto Sans SC',
        ...(timeItems.value.length > 12 ? { interval: Math.ceil(timeItems.value.length / 12) } : {}),
      },
    },
    yAxis: { type: 'value', minInterval: 1, ...AXIS_LINE, axisLabel: { color: '#8f8a83' } },
    series: [
      {
        name: '投递量',
        type: 'bar',
        data: timeItems.value.map((t) => t.count),
        barMaxWidth: 26,
        itemStyle: { color: appearance.accent, opacity: 0.82, borderRadius: [5, 5, 0, 0] },
        emphasis: { itemStyle: { opacity: 1 } },
      },
    ],
  }),
)

onMounted(loadAll)
</script>

<style scoped>
.kpi-layout {
  display: grid;
  grid-template-columns: minmax(250px, 0.78fr) minmax(0, 1.5fr);
  gap: 14px;
  margin-bottom: 20px;
}
.kpi-primary,
.kpi-rates {
  display: grid;
  gap: 14px;
}
.kpi-primary {
  grid-template-columns: 1fr 1fr;
}
.kpi-rates {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.kpi-primary :deep(.kpi) {
  min-height: 138px;
  padding-top: 22px;
}
.kpi-primary :deep(.kpi-value) {
  font-size: 34px;
}
.charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  align-items: start;
}
@media (max-width: 1100px) {
  .charts {
    grid-template-columns: 1fr;
  }
}
.chart-card {
  padding: 18px 20px;
}
.chart-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}
.chart-title {
  font-size: 13.5px;
  font-weight: 650;
  color: var(--ink);
}
.chart-sub {
  font-size: 11.5px;
  color: var(--ink-3);
  margin-top: 2px;
}
.chart {
  height: 320px;
  width: 100%;
}
.stats-empty {
  min-height: 360px;
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
  align-items: center;
  overflow: hidden;
  padding: 42px 52px;
  position: relative;
  background:
    linear-gradient(112deg, var(--surface) 0 62%, transparent 62%),
    radial-gradient(circle at 84% 20%, color-mix(in srgb, var(--accent-2) 24%, transparent), transparent 34%),
    var(--accent-soft);
}
.stats-empty::after {
  content: '';
  position: absolute;
  right: -62px;
  bottom: -96px;
  width: 280px;
  height: 280px;
  border: 1px dashed var(--accent-line);
  border-radius: 50%;
}
.stats-empty-copy {
  position: relative;
  z-index: 1;
  max-width: 620px;
}
.empty-label {
  font-size: 12px;
  color: var(--accent-strong);
  font-weight: 700;
}
.stats-empty h3 {
  margin: 9px 0 0;
  max-width: 17ch;
  font-size: clamp(24px, 2.5vw, 36px);
  line-height: 1.25;
  letter-spacing: -0.035em;
}
.stats-empty p {
  margin: 12px 0 0;
  color: var(--ink-2);
  line-height: 1.75;
}
.empty-actions,
.empty-checks {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
.empty-actions {
  margin-top: 20px;
}
.empty-checks {
  margin-top: 22px;
  color: var(--ink-3);
  font-size: 11.5px;
}
.empty-checks span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.empty-checks .el-icon {
  color: var(--ok);
}
.stats-empty-art {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
}
@media (max-width: 1180px) {
  .kpi-layout {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 760px) {
  .kpi-primary,
  .kpi-rates {
    grid-template-columns: 1fr 1fr;
  }
  .stats-empty {
    grid-template-columns: 1fr;
    padding: 28px;
  }
  .stats-empty-art {
    display: none;
  }
}
@media (max-width: 520px) {
  .kpi-primary,
  .kpi-rates {
    grid-template-columns: 1fr;
  }
}
</style>
