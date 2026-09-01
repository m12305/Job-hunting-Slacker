<template>
  <div class="page">
    <PageHeader
      kicker="SETTINGS · 偏好与维护"
      title="设置"
      desc="配置 Offer 打分偏好与权重、管理数据备份。所有数据仅保存在本机。"
    />

    <el-skeleton v-if="loading" :rows="8" animated class="panel" style="padding: 20px" />

    <div v-else class="settings">
      <!-- 打分偏好 -->
      <section class="panel block">
        <div class="block-head">
          <div>
            <div class="block-title">Offer 打分偏好</div>
            <div class="block-sub">薪资维度按理想年薪区间线性映射到 0-100 分；城市命中首选城市得满分，否则 60 分</div>
          </div>
        </div>

        <div class="setting-row">
          <div class="s-label">理想年薪区间（K/年）</div>
          <div class="s-control">
            <div class="range-inputs">
              <el-input-number v-model="salaryLo" :min="0" :max="3000" :step="10" controls-position="right" style="width: 140px" />
              <span class="range-sep">—</span>
              <el-input-number v-model="salaryHi" :min="0" :max="3000" :step="10" controls-position="right" style="width: 140px" />
              <el-button type="primary" plain @click="saveRange">保存区间</el-button>
            </div>
            <div class="form-hint">低于区间底部的年薪得 0 分，超出顶部得 100 分，区间内线性插值</div>
          </div>
        </div>

        <div class="setting-row">
          <div class="s-label">首选城市</div>
          <div class="s-control">
            <TagInput v-model="preferredCities" placeholder="+ 城市，如 北京" />
            <div class="range-actions">
              <el-button type="primary" plain @click="saveCities">保存城市</el-button>
            </div>
          </div>
        </div>
      </section>

      <!-- 权重配置 -->
      <section class="panel block">
        <div class="block-head">
          <div>
            <div class="block-title">打分维度与权重</div>
            <div class="block-sub">总分 = Σ(维度得分 × 权重) / Σ(权重)；关闭的维度不参与评分</div>
          </div>
          <el-button type="primary" :loading="savingWeights" @click="saveWeights">保存权重</el-button>
        </div>

        <div class="weight-table">
          <div class="wt-head">
            <span>维度</span>
            <span>权重</span>
            <span>参与</span>
            <span></span>
          </div>
          <div v-for="(w, i) in weights" :key="w.dimension_key" class="wt-row">
            <div class="wt-name">
              <span class="w-name">{{ w.dimension_name }}</span>
              <span class="mono w-key">{{ w.dimension_key }}</span>
            </div>
            <el-input-number v-model="w.weight" :min="0" :max="1" :step="0.05" :precision="2" size="small" controls-position="right" style="width: 130px" />
            <el-switch v-model="w.enabled" />
            <button v-if="isCustom(w)" class="op danger" @click="weights.splice(i, 1)"><el-icon><Delete /></el-icon></button>
          </div>
        </div>

        <div class="add-weight">
          <el-input v-model="customName" placeholder="自定义维度名，如 离家距离" style="width: 180px" />
          <el-input v-model="customKey" placeholder="英文 key，如 distance" style="width: 180px" />
          <el-button @click="addCustom"><el-icon><Plus /></el-icon>&nbsp;添加维度</el-button>
          <span class="form-hint">自定义维度需在 Offer 的「其他备注」之外单独维护：暂存于 Offer.extra_scores 字段</span>
        </div>
      </section>

      <!-- 数据备份 -->
      <section class="panel block">
        <div class="block-head">
          <div>
            <div class="block-title">数据备份与恢复</div>
            <div class="block-sub">ZIP 备份同时包含业务数据和上传文件；恢复前会自动保留当前数据快照</div>
          </div>
        </div>

        <div class="backup-actions">
          <el-button type="primary" plain :loading="exporting" @click="doExport">
            <el-icon><Download /></el-icon>&nbsp;导出完整 ZIP 备份
          </el-button>
          <el-button :loading="importing" @click="pickImportFile">
            <el-icon><Upload /></el-icon>&nbsp;导入备份
          </el-button>
          <input ref="importInput" type="file" accept=".zip,application/zip,.json,application/json" class="hidden" @change="doImport" />
          <span v-if="health" class="health-info">
            <span class="dot" style="background: #1a7f5c" />
            后端 v{{ health.version }} · {{ health.app }}
          </span>
        </div>
        <el-alert
          title="完整备份包含数据库记录与简历、素材、录音等上传文件。旧版 JSON 仍可导入，但不包含文件。"
          type="info"
          :closable="false"
          class="tip"
        />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import TagInput from '@/components/TagInput.vue'
import {
  exportBackup,
  getHealth,
  getSettings,
  getWeightConfig,
  importBackup,
  importLegacyBackup,
  saveSettings,
  updateWeightConfig,
} from '@/api'
import type { HealthInfo, OfferWeight, SettingsMap } from '@/types'

const loading = ref(true)

/* ---- 打分偏好 ---- */
const salaryLo = ref(240)
const salaryHi = ref(800)
const preferredCities = ref<string[]>([])

async function saveRange() {
  if (salaryLo.value >= salaryHi.value) {
    ElMessage.warning('区间下限需小于上限')
    return
  }
  await saveSettings({ salary_ideal_range: [salaryLo.value, salaryHi.value] })
  ElMessage.success('理想年薪区间已保存')
}
async function saveCities() {
  await saveSettings({ preferred_cities: [...preferredCities.value] })
  ElMessage.success('首选城市已保存')
}

/* ---- 权重 ---- */
const weights = ref<OfferWeight[]>([])
const savingWeights = ref(false)
const customName = ref('')
const customKey = ref('')

const isCustom = (w: OfferWeight) => !['salary', 'city', 'work_intensity', 'industry', 'company_scale', 'position_dev'].includes(w.dimension_key)

async function saveWeights() {
  savingWeights.value = true
  try {
    await updateWeightConfig(
      weights.value.filter((w) => w.weight > 0 || w.enabled).map((w, i) => ({
        dimension_key: w.dimension_key,
        dimension_name: w.dimension_name,
        weight: Number(w.weight.toFixed(2)),
        enabled: w.enabled,
        sort_order: i,
      })),
    )
    ElMessage.success('权重已保存')
    weights.value = await getWeightConfig()
  } finally {
    savingWeights.value = false
  }
}
async function addCustom() {
  const name = customName.value.trim()
  const key = customKey.value.trim().toLowerCase().replace(/\s+/g, '_')
  if (!name || !key) {
    ElMessage.warning('请填写维度名与英文 key')
    return
  }
  if (weights.value.some((w) => w.dimension_key === key)) {
    ElMessage.warning('该 key 已存在')
    return
  }
  weights.value.push({ id: 0, dimension_key: key, dimension_name: name, weight: 0.2, enabled: true, sort_order: weights.value.length })
  customName.value = ''
  customKey.value = ''
  ElMessage.success('已添加，点击「保存权重」生效')
}

/* ---- 备份 ---- */
const exporting = ref(false)
const importing = ref(false)
const importInput = ref<HTMLInputElement | null>(null)
const health = ref<HealthInfo | null>(null)

async function doExport() {
  exporting.value = true
  try {
    await exportBackup()
    ElMessage.success('备份已导出')
  } catch {
    /* 已提示 */
  } finally {
    exporting.value = false
  }
}
function pickImportFile() {
  importInput.value?.click()
}
async function doImport(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  try {
    if (file.name.toLowerCase().endsWith('.json')) {
      const parsed = JSON.parse(await file.text()) as Record<string, unknown>
      const data = parsed.data && typeof parsed.data === 'object' ? parsed.data as Record<string, unknown> : parsed
      const tables: Record<string, unknown> = data.tables && typeof data.tables === 'object'
        ? data.tables as Record<string, unknown>
        : data
      const rows = Object.values(tables).reduce<number>((n, arr) => n + (Array.isArray(arr) ? arr.length : 0), 0)
      await ElMessageBox.confirm(
        `这是旧版 JSON 备份，将覆盖当前业务数据（约 ${rows} 行），但不会恢复上传文件。确定继续？`,
        '导入旧版备份',
        { type: 'warning', confirmButtonText: '继续导入', cancelButtonText: '取消' },
      )
      importing.value = true
      const res = await importLegacyBackup({ tables })
      ElMessage.success(`旧版数据导入完成：${Object.keys(res.imported).length} 张表`)
      setTimeout(() => window.location.reload(), 800)
      return
    }

    await ElMessageBox.confirm(
      '恢复完整备份会覆盖当前业务数据和上传文件。系统会先自动生成恢复前快照，确定继续？',
      '恢复完整备份',
      { type: 'warning', confirmButtonText: '校验并恢复', cancelButtonText: '取消' },
    )
    importing.value = true
    const res = await importBackup(file)
    ElMessage.success(`恢复完成，已自动保留恢复前快照：${res.snapshot}`)
    setTimeout(() => window.location.reload(), 1000)
  } catch (err) {
    if (err === 'cancel' || err === 'close') return
    ElMessage.error(err instanceof Error ? `导入失败：${err.message}` : '导入失败')
  } finally {
    importing.value = false
  }
}

onMounted(async () => {
  try {
    const [settingsMap, weightsList, healthInfo] = await Promise.all([
      getSettings(),
      getWeightConfig(),
      getHealth().catch(() => null),
    ])
    applySettings(settingsMap)
    weights.value = weightsList
    health.value = healthInfo
  } finally {
    loading.value = false
  }
})

function applySettings(m: SettingsMap) {
  const range = m.salary_ideal_range
  if (Array.isArray(range) && range.length === 2) {
    salaryLo.value = Number(range[0]) || 240
    salaryHi.value = Number(range[1]) || 800
  }
  const cities = m.preferred_cities
  if (Array.isArray(cities)) preferredCities.value = cities.map(String)
}
</script>

<style scoped>
.settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 860px;
}
.block {
  padding: 20px 22px;
}
.block-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}
.block-title {
  font-size: 14px;
  font-weight: 650;
  color: var(--ink);
}
.block-sub {
  font-size: 12px;
  color: var(--ink-3);
  margin-top: 3px;
}

.setting-row {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px dashed var(--line);
}
.setting-row:last-child {
  border-bottom: none;
}
.s-label {
  font-size: 13px;
  font-weight: 550;
  color: var(--ink-2);
  padding-top: 6px;
}
.s-control {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-start;
}
.range-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}
.range-sep {
  color: var(--ink-4);
}
.range-actions {
  margin-top: 4px;
}
@media (max-width: 640px) {
  .setting-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
}

.weight-table {
  display: flex;
  flex-direction: column;
}
.wt-head,
.wt-row {
  display: grid;
  grid-template-columns: 1.4fr 160px 70px 40px;
  gap: 12px;
  align-items: center;
  padding: 9px 4px;
}
.wt-head {
  font-size: 11.5px;
  color: var(--ink-3);
  letter-spacing: 0.06em;
  border-bottom: 1px solid var(--line);
}
.wt-row {
  border-bottom: 1px dashed var(--line);
  font-size: 13px;
}
.wt-row:last-child {
  border-bottom: none;
}
.wt-name {
  display: flex;
  flex-direction: column;
}
.w-name {
  font-weight: 600;
  color: var(--ink);
}
.w-key {
  font-size: 10.5px;
  color: var(--ink-3);
}
.op {
  width: 26px;
  height: 26px;
  border: none;
  background: transparent;
  border-radius: 6px;
  color: var(--ink-3);
  cursor: pointer;
}
.op.danger:hover {
  color: var(--danger);
  background: var(--danger-soft);
}

.add-weight {
  display: flex;
  gap: 8px;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px dashed var(--line);
  align-items: center;
  flex-wrap: wrap;
}
.add-weight .form-hint {
  width: 100%;
}

.backup-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}
.health-info {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--ink-2);
  margin-left: auto;
}
.tip {
  margin-top: 14px;
  border-radius: 8px;
}
.hidden {
  display: none;
}
</style>
