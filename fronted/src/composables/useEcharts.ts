/* ECharts 组合式封装：初始化 / 响应式更新 / 自适应尺寸 / 卸载释放 */
import { nextTick, onBeforeUnmount, onMounted, watch, type Ref } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

export function useEcharts(elRef: Ref<HTMLDivElement | null>, getOption: () => EChartsOption) {
  let chart: echarts.ECharts | null = null
  let observer: ResizeObserver | null = null
  let mounted = false

  function dispose() {
    observer?.disconnect()
    observer = null
    chart?.dispose()
    chart = null
  }

  async function init(el: HTMLDivElement | null) {
    dispose()
    if (!mounted || !el) return
    await nextTick()
    if (!mounted || elRef.value !== el) return
    chart = echarts.init(el)
    chart.setOption(getOption())
    observer = new ResizeObserver(() => chart?.resize())
    observer.observe(el)
  }

  onMounted(() => {
    mounted = true
    void init(elRef.value)
  })

  watch(elRef, (el) => void init(el), { flush: 'post' })

  watch(
    getOption,
    () => {
      if (chart) chart.setOption(getOption(), true)
    },
    { deep: true },
  )

  onBeforeUnmount(() => {
    mounted = false
    dispose()
  })

  return { resize: () => chart?.resize() }
}

/* 与「秋日档案」一致的图表色板 */
export const AXIS_LINE = {
  axisLine: { lineStyle: { color: '#d7d3ca' } },
  axisTick: { show: false },
  axisLabel: { color: '#8f8a83', fontFamily: 'Noto Sans SC, sans-serif' },
  splitLine: { lineStyle: { color: '#ece9e2' } },
}
