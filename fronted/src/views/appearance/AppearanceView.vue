<template>
  <div class="page">
    <PageHeader
      kicker="外观设置 · 换皮肤时间"
      title="外观设置"
      desc="主题风格、配色、壁纸、透明度都可以自由搭配，设置会保存在本机浏览器。"
    >
      <template #actions>
        <el-button @click="appearance.resetAppearance">
          <el-icon><RefreshLeft /></el-icon>&nbsp;恢复默认外观
        </el-button>
      </template>
    </PageHeader>

    <!-- 主题风格 -->
    <section class="panel block">
      <div class="block-head">
        <div>
          <div class="block-title fun">主题风格</div>
          <div class="block-sub">决定吉祥物与整体气质；配色可在此基础上自由调整</div>
        </div>
        <span class="current-chip">{{ appearance.kindMeta.name }}</span>
      </div>

      <div class="kind-grid">
        <button
          v-for="k in THEME_KINDS"
          :key="k.key"
          class="kind-card"
          :class="{ on: appearance.themeKind === k.key }"
          @click="appearance.setThemeKind(k.key)"
        >
          <span class="kc-preview" :class="`preview-${k.key}`">
            <ThemeMascot v-if="k.mascot !== 'none'" pose="sit" :kind="k.mascot" :size="k.key === 'linedog' ? 148 : 132" />
            <template v-else>
              <span class="plain-logo fun">局</span>
              <span class="plain-lines">
                <i /><i /><i />
              </span>
            </template>
            <el-icon v-if="appearance.themeKind === k.key" class="kc-check"><Check /></el-icon>
          </span>
          <span class="kc-name">{{ k.name }}</span>
          <span class="kc-desc">{{ k.desc }}</span>
        </button>
      </div>
    </section>

    <!-- 界面配色 -->
    <section class="panel block">
      <div class="block-head">
        <div>
          <div class="block-title fun">界面配色</div>
          <div class="block-sub">强调色会同步到按钮、选中态、图表主色；柔和色自动派生</div>
        </div>
        <span class="current-chip accent-chip">
          <i class="accent-dot" :style="{ background: appearance.accent }" />
          {{ appearance.accentMode === 'custom' ? '自定义' : appearance.currentPresetName }}
        </span>
      </div>

      <div class="accent-label">预设色板</div>
      <div class="accent-grid">
        <button
          v-for="p in ACCENT_PRESETS"
          :key="p.key"
          class="accent-swatch"
          :class="{ on: appearance.accentMode === 'preset' && appearance.accentPresetKey === p.key }"
          :style="{ background: p.accent }"
          :title="p.name"
          @click="appearance.setAccentPreset(p.key)"
        >
          <el-icon v-if="appearance.accentMode === 'preset' && appearance.accentPresetKey === p.key"><Check /></el-icon>
          <span class="accent-name">{{ p.name }}</span>
        </button>
      </div>

      <div class="custom-line">
        <div class="accent-label" style="margin: 0">自定义色板</div>
        <div class="custom-controls">
          <el-color-picker v-model="customHex" :predefine="PREDEFINE_HEXS" />
          <el-button type="primary" @click="applyCustom"><el-icon><Brush /></el-icon>&nbsp;应用我的颜色</el-button>
          <el-button v-if="appearance.accentMode === 'custom'" text type="primary" @click="appearance.setAccentPreset('tangerine')">
            回到预设
          </el-button>
        </div>
        <div class="form-hint">在色板上任选一个颜色并点击「应用」，立即作为全局强调色生效并保留</div>
      </div>
    </section>

    <!-- 壁纸 -->
    <section class="panel block">
      <div class="block-head">
        <div>
          <div class="block-title fun">背景壁纸</div>
          <div class="block-sub">上传后会铺满整个界面，内容面板自动变为半透明毛玻璃以保持可读</div>
        </div>
      </div>

      <div class="wallpaper-row">
        <div class="wp-preview" :class="{ empty: !appearance.bgImage }">
          <div
            v-if="appearance.bgImage"
            class="wp-img"
            :style="{ backgroundImage: `url(${appearance.bgImage})`, opacity: appearance.bgOpacity / 100 }"
          />
          <template v-else>
            <ThemeMascot pose="wave" :size="66" />
            <span class="wp-empty-text">还没有壁纸，换张喜欢的图试试</span>
          </template>
        </div>

        <div class="wp-actions">
          <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onPick" />
          <el-button type="primary" @click="fileInput?.click()">
            <el-icon><Upload /></el-icon>&nbsp;上传壁纸
          </el-button>
          <el-button :disabled="!appearance.bgImage" @click="appearance.setBgImage(null)">
            <el-icon><Delete /></el-icon>&nbsp;移除壁纸
          </el-button>
          <div class="form-hint">
            图片会自动压缩到最长边 1920px 以内（JPEG 约 82% 质量）再存入浏览器本地。
          </div>
        </div>
      </div>
    </section>

    <!-- 透明度 -->
    <section class="panel block">
      <div class="block-head">
        <div>
          <div class="block-title fun">壁纸透明度</div>
          <div class="block-sub">透明度越高，壁纸越清晰；调低一点可以让文字更突出</div>
        </div>
        <span class="mono op-value">{{ appearance.bgOpacity }}%</span>
      </div>

      <div class="op-row">
        <el-slider
          v-model="opacity"
          :min="0"
          :max="100"
          :show-tooltip="false"
          :disabled="!appearance.bgImage"
          class="op-slider"
        />
        <div class="op-demo" :class="{ active: appearance.bgImage }">
          <div
            class="op-demo-img"
            :style="appearance.bgImage ? { backgroundImage: `url(${appearance.bgImage})` } : {}"
          >
            <div class="op-demo-card" :style="{ background: `rgba(255,255,255,${0.72 - appearance.bgOpacity / 100 * 0.35})` }">
              透明度 {{ appearance.bgOpacity }}%
            </div>
          </div>
        </div>
      </div>
      <div v-if="!appearance.bgImage" class="form-hint">上传壁纸后可调节透明度</div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import ThemeMascot from '@/components/ThemeMascot.vue'
import { useAppearanceStore, ACCENT_PRESETS, THEME_KINDS } from '@/stores/appearance'
import { fileToCompressedDataUrl } from '@/utils/image'

const appearance = useAppearanceStore()
const fileInput = ref<HTMLInputElement | null>(null)

const PREDEFINE_HEXS = ACCENT_PRESETS.map((p) => p.accent)
const customHex = ref(appearance.customAccent)

const opacity = computed({
  get: () => appearance.bgOpacity,
  set: (v: number) => appearance.setBgOpacity(v),
})

function applyCustom() {
  const hex = customHex.value
  if (!/^#[0-9a-fA-F]{6}$/.test(hex)) {
    ElMessage.warning('请选择一个有效的颜色')
    return
  }
  appearance.setCustomAccent(hex)
  ElMessage.success(`已应用自定义颜色 ${hex}`)
}

async function onPick(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  try {
    const dataUrl = await fileToCompressedDataUrl(file)
    appearance.setBgImage(dataUrl)
    ElMessage.success('壁纸已上传并生效')
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : '壁纸处理失败')
  }
}
</script>

<style scoped>
.block {
  padding: 22px 24px;
  margin-bottom: 18px;
  max-width: 1180px;
}
.block-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}
.block-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--ink);
}
.block-sub {
  font-size: 12px;
  color: var(--ink-3);
  margin-top: 3px;
}
.current-chip {
  font-size: 12px;
  color: var(--accent-strong);
  background: var(--accent-soft);
  border: 1px solid var(--accent-line);
  padding: 3px 12px;
  border-radius: 999px;
  font-weight: 550;
}
.accent-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.accent-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 1.5px solid var(--surface);
  box-shadow: 0 0 0 1px var(--line-strong);
}

/* -------- 主题风格 -------- */
.kind-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}
.kind-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 9px;
  padding: 15px 15px 16px;
  border: 1.5px solid var(--line);
  border-radius: 16px;
  background: var(--surface);
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.kind-card:hover {
  border-color: var(--line-strong);
  transform: translateY(-2px);
  box-shadow: var(--shadow-1);
}
.kind-card.on {
  border-color: var(--accent);
  background: var(--accent-soft);
}
.kc-preview {
  position: relative;
  width: 100%;
  height: 132px;
  border-radius: 15px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.preview-linedog {
  background:
    radial-gradient(circle at 18% 18%, rgba(136, 205, 235, 0.42), transparent 28%),
    linear-gradient(160deg, #effaff, #fff8f1);
}
.kind-card.on .kc-preview {
  border-color: var(--accent-line);
  background: var(--bg-soft);
}
.preview-shinchan {
  background:
    radial-gradient(circle at 82% 16%, rgba(255, 190, 46, 0.52), transparent 24%),
    linear-gradient(160deg, #fff9bf, #fff0ec);
}
.kc-check {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  font-size: 13px;
  z-index: 2;
}
.plain-logo {
  font-size: 34px;
  font-weight: 750;
  color: var(--accent-strong);
  position: absolute;
  top: 12px;
}
.plain-lines {
  position: absolute;
  bottom: 20px;
  display: flex;
  gap: 5px;
}
.plain-lines i {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent);
  opacity: 0.45;
}
.kc-name {
  font-size: 13.5px;
  font-weight: 650;
  color: var(--ink);
}
.kc-desc {
  font-size: 11.5px;
  color: var(--ink-3);
  text-align: center;
  line-height: 1.5;
  min-height: 35px;
}

@media (max-width: 900px) {
  .kind-grid {
    grid-template-columns: 1fr;
  }
}

/* -------- 配色 -------- */
.accent-label {
  font-size: 12px;
  color: var(--ink-3);
  letter-spacing: 0.06em;
  font-weight: 600;
  margin-bottom: 10px;
}
.accent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(96px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}
.accent-swatch {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 7px;
  padding: 12px 8px 10px;
  border-radius: 13px;
  border: 1.5px solid var(--line);
  background: var(--surface);
  cursor: pointer;
  color: #fff;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.accent-swatch::before {
  content: '';
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: inherit;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.14);
}
.accent-swatch .el-icon {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 15px;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.35));
}
.accent-swatch:hover {
  border-color: var(--line-strong);
  transform: translateY(-2px);
}
.accent-swatch.on {
  border-color: var(--ink);
  box-shadow: 0 0 0 2px var(--surface), 0 0 0 3.5px var(--ink);
}
.accent-name {
  font-size: 11px;
  color: var(--ink-2);
  font-weight: 550;
}
.custom-line {
  border-top: 1px dashed var(--line);
  padding-top: 16px;
}
.custom-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

/* -------- 壁纸 -------- */
.wallpaper-row {
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}
.wp-preview {
  width: 260px;
  height: 150px;
  border-radius: 16px;
  border: 1.5px dashed var(--line-strong);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 8px;
  background: var(--surface-2);
  position: relative;
}
.wp-img {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
}
.wp-empty-text {
  font-size: 12px;
  color: var(--ink-3);
}
.wp-actions {
  flex: 1;
  min-width: 220px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}
.hidden {
  display: none;
}

/* -------- 透明度 -------- */
.op-row {
  display: flex;
  gap: 24px;
  align-items: center;
  flex-wrap: wrap;
}
.op-slider {
  flex: 1;
  min-width: 240px;
}
.op-value {
  font-size: 15px;
  font-weight: 650;
  color: var(--accent-strong);
}
.op-demo {
  width: 180px;
  height: 96px;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid var(--line);
}
.op-demo-img {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-color: var(--surface-2);
  display: flex;
  align-items: center;
  justify-content: center;
}
.op-demo-card {
  padding: 10px 16px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  font-size: 12px;
  font-weight: 600;
  color: #333;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}
</style>
