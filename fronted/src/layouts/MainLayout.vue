<template>
  <div class="layout" :class="{ 'sidebar-collapsed': sidebarCollapsed && !isMobile, 'mobile-open': mobileSidebarOpen }">
    <button
      v-if="isMobile && mobileSidebarOpen"
      type="button"
      class="sidebar-scrim"
      aria-label="关闭侧边栏"
      @click="mobileSidebarOpen = false"
    />
    <!-- =============== 侧边栏 =============== -->
    <aside id="main-sidebar" class="sidebar">
      <!-- 背景小涂鸦（卡通主题显示） -->
      <svg v-if="appearance.mascot !== 'none'" class="sb-doodle d-star1" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 2l2.4 7.6L22 12l-7.6 2.4L12 22l-2.4-7.6L2 12l7.6-2.4z" fill="#f59e0b" opacity="0.5" />
      </svg>
      <svg v-if="appearance.mascot !== 'none'" class="sb-doodle d-star2" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 4l1.8 5.4L19 11l-5.2 1.6L12 18l-1.8-5.4L5 11l5.2-1.6z" fill="#d63d7a" opacity="0.35" />
      </svg>
      <svg v-if="appearance.mascot !== 'none'" class="sb-doodle d-spiral" viewBox="0 0 32 32" aria-hidden="true">
        <path
          d="M26 12c0 8-7 14-14 14C6 26 2 21 2 15 2 8 8 3 15 3c5 0 8 3 8 7"
          fill="none"
          stroke="#0f766e"
          stroke-width="2.4"
          stroke-linecap="round"
          opacity="0.4"
        />
      </svg>
      <!-- 蜡笔小新主题专属：粗眉毛小涂鸦 -->
      <svg v-if="appearance.themeKind === 'shinchan'" class="sb-doodle d-brow" viewBox="0 0 48 20" aria-hidden="true">
        <path d="M6 6 q10 10 22 2 M26 4 q10 10 22 2" stroke="#d63b30" stroke-width="6" stroke-linecap="round" fill="none" opacity="0.5" />
      </svg>

      <div class="brand dog-wiggle">
        <div class="brand-logo">
          <ThemeMascot v-if="appearance.mascot !== 'none'" pose="sit" :size="40" />
          <span v-else class="plain-mark fun">局</span>
        </div>
        <div class="brand-text">
          <div class="brand-name fun">求职摆烂管理局</div>
          <div class="brand-sub">SLACK BUREAU / 人事处</div>
        </div>
      </div>

      <div v-if="!isMobile" class="sidebar-collapse-row">
        <button
          type="button"
          class="sidebar-collapse-button"
          :title="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
          :aria-label="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
          :aria-expanded="!sidebarCollapsed"
          aria-controls="main-sidebar"
          @click="toggleSidebar"
        >
          <el-icon><component :is="sidebarCollapsed ? 'Expand' : 'Fold'" /></el-icon>
          <span>{{ sidebarCollapsed ? '展开' : '收起侧栏' }}</span>
        </button>
      </div>

      <nav class="nav">
        <template v-for="(section, sectionIndex) in sections" :key="section.title">
          <div v-if="section.items.length" class="nav-section">
            <button
              type="button"
              class="nav-section-title"
              :aria-expanded="isSectionOpen(section.title)"
              :aria-controls="`nav-section-${sectionIndex}`"
              @click="toggleSection(section.title)"
            >
              <span class="nst-dot" />
              <span class="nav-section-label">{{ section.title }}</span>
              <el-icon class="nav-section-chevron" :class="{ open: isSectionOpen(section.title) }"><ArrowRight /></el-icon>
            </button>
            <Transition name="nav-fold">
              <div
                v-show="isSectionOpen(section.title) || (sidebarCollapsed && !isMobile)"
                :id="`nav-section-${sectionIndex}`"
                class="nav-section-items"
              >
                <RouterLink
                  v-for="item in section.items"
                  :key="item.path"
                  :to="item.path"
                  class="nav-item"
                  :class="{ active: route.path === item.path || (item.path === '/offers' && route.path.startsWith('/offers')) }"
                  :title="sidebarCollapsed && !isMobile ? item.title : undefined"
                  :aria-label="item.title"
                  @click="mobileSidebarOpen = false"
                >
                  <span class="nav-indicator" />
                  <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
                  <span class="nav-label">{{ item.title }}</span>
                  <span v-if="item.badge && item.badge > 0" class="nav-badge">{{ item.badge }}</span>
                </RouterLink>
              </div>
            </Transition>
          </div>
        </template>
      </nav>

      <div class="sidebar-foot">
        <div v-if="appearance.mascot !== 'none'" class="foot-mascot dog-wiggle">
          <ThemeMascot pose="zzz" :size="96" />
          <div class="foot-note">
            <b>{{ appearance.themeKind === 'shinchan' ? '小新今日值班' : '小狗今日陪班' }}</b>
            <span>摆烂可以，删数据不行。</span>
          </div>
        </div>
        <div class="health">
          <span class="dot" :style="{ background: healthOk ? '#1a7f5c' : '#b3402f' }" />
          <span>{{ healthOk ? `后端已连接 · v${version}` : '后端未连接 :8000' }}</span>
        </div>
        <button class="foot-btn" @click="onExport">
          <el-icon><Download /></el-icon>
          <span>备份全部数据</span>
        </button>
      </div>
    </aside>

    <!-- =============== 主区 =============== -->
    <div class="main">
      <div v-if="appearance.mascot !== 'none'" class="ambient-mascot" aria-hidden="true">
        <ThemeMascot pose="sit" :size="390" />
      </div>
      <header class="topbar">
        <div class="topbar-start">
          <button
            v-if="isMobile"
            type="button"
            class="nav-toggle"
            :aria-label="isMobile ? (mobileSidebarOpen ? '关闭侧边栏' : '打开侧边栏') : (sidebarCollapsed ? '展开侧边栏' : '收起侧边栏')"
            :aria-expanded="isMobile ? mobileSidebarOpen : !sidebarCollapsed"
            aria-controls="main-sidebar"
            @click="toggleSidebar"
          >
            <el-icon :size="17"><component :is="isMobile ? 'Menu' : (sidebarCollapsed ? 'Expand' : 'Fold')" /></el-icon>
          </button>
          <div class="topbar-title">
            <h1>{{ route.meta.title }}</h1>
            <p v-if="route.meta.section">{{ route.meta.section }} · 本地单机上班摸鱼工具</p>
          </div>
        </div>
        <div class="topbar-actions">
          <!-- 快捷换肤 -->
          <el-popover placement="bottom-end" :width="252" trigger="click" popper-class="theme-pop">
            <template #reference>
              <button class="palette-btn" title="外观设置">
                <el-icon :size="15"><Brush /></el-icon>
                <span class="palette-dot" :style="{ background: appearance.accent }" />
              </button>
            </template>
            <div class="theme-quick">
              <div class="tq-title">主题风格</div>
              <div class="tq-kinds">
                <button
                  v-for="k in THEME_KINDS"
                  :key="k.key"
                  class="tq-kind"
                  :class="{ on: appearance.themeKind === k.key }"
                  @click="appearance.setThemeKind(k.key)"
                >
                  {{ k.name }}
                </button>
              </div>
              <div class="tq-title" style="margin-top: 10px">配色</div>
              <div class="tq-grid">
                <button
                  v-for="p in ACCENT_PRESETS"
                  :key="p.key"
                  class="tq-swatch"
                  :class="{ on: appearance.accentMode === 'preset' && appearance.accentPresetKey === p.key }"
                  :style="{ background: p.accent }"
                  :title="p.name"
                  @click="appearance.setAccentPreset(p.key)"
                >
                  <el-icon v-if="appearance.accentMode === 'preset' && appearance.accentPresetKey === p.key"><Check /></el-icon>
                </button>
                <button
                  class="tq-swatch custom"
                  :class="{ on: appearance.accentMode === 'custom' }"
                  :style="{ background: appearance.customAccent }"
                  title="应用自定义颜色"
                  @click="appearance.setCustomAccent(appearance.customAccent)"
                >
                  <el-icon v-if="appearance.accentMode === 'custom'"><Brush /></el-icon>
                </button>
              </div>
              <RouterLink to="/appearance" class="tq-more">
                主题 / 自定义色板 / 壁纸 / 透明度 →
              </RouterLink>
            </div>
          </el-popover>

          <div class="date-chip">
            <el-icon><Clock /></el-icon>
            <span class="mono">{{ todayStr }}</span>
          </div>
          <div v-if="streak !== null" class="streak-chip" :class="{ hot: streak >= 3 }">
            <el-icon><Fire /></el-icon>
            <span>连续打卡 <b class="mono">{{ streak }}</b> 天</span>
          </div>
        </div>
      </header>

      <main class="content">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" :key="route.path" />
          </Transition>
        </RouterView>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { exportBackup, getHealth } from '@/api'
import { getDashboardStreak, getDashboardToday } from '@/api'
import { todayLabel } from '@/utils/format'
import { useAppearanceStore, ACCENT_PRESETS, THEME_KINDS } from '@/stores/appearance'
import ThemeMascot from '@/components/ThemeMascot.vue'

const appearance = useAppearanceStore()

interface NavItem {
  title: string
  path: string
  icon: string
  badge?: number
}

/* 趣味分区名 */
const sections = computed<{ title: string; items: NavItem[] }[]>(() => {
  const pendingBadge = pendingCount.value
  const raw: { title: string; items: { title: string; path: string; icon: string; badge?: number }[] }[] = [
    {
      title: '摆烂日常',
      items: [
        { title: '今日看板', path: '/dashboard', icon: 'Calendar' },
        { title: '数据看板', path: '/stats', icon: 'TrendCharts' },
      ],
    },
    {
      title: '简历资产',
      items: [
        { title: '简历版本', path: '/resumes', icon: 'Document' },
        { title: '素材库', path: '/materials', icon: 'Notebook' },
        { title: '资产归档', path: '/assets', icon: 'FolderOpened' },
      ],
    },
    {
      title: '投递战场',
      items: [
        { title: '投递管理', path: '/applications', icon: 'Promotion', badge: pendingBadge },
        { title: 'Offer 管理', path: '/offers', icon: 'Medal' },
        { title: 'Offer 对比', path: '/offers/compare', icon: 'DataAnalysis' },
      ],
    },
    {
      title: '笔面现场',
      items: [
        { title: '笔试管理', path: '/exams', icon: 'EditPen' },
        { title: '面试管理', path: '/interviews', icon: 'ChatLineSquare' },
        { title: '题库', path: '/questions', icon: 'Reading' },
      ],
    },
    {
      title: '摸鱼工具箱',
      items: [
        { title: '话术库', path: '/scripts', icon: 'MagicStick' },
        { title: '避雷库', path: '/blacklist', icon: 'Warning' },
        { title: '外观设置', path: '/appearance', icon: 'Brush' },
        { title: '设置', path: '/settings', icon: 'Setting' },
      ],
    },
  ]
  return raw
})

const route = useRoute()
const todayStr = todayLabel()
const healthOk = ref(false)
const version = ref('')
const streak = ref<number | null>(null)
const pendingCount = ref(0)
const SIDEBAR_STORAGE_KEY = 'qiuzhao-sidebar-collapsed'
const NAV_GROUPS_STORAGE_KEY = 'qiuzhao-sidebar-groups-collapsed'
const isMobile = ref(window.innerWidth <= 860)
const sidebarCollapsed = ref(localStorage.getItem(SIDEBAR_STORAGE_KEY) === '1')
const mobileSidebarOpen = ref(false)
const collapsedNavGroups = ref<string[]>(loadCollapsedNavGroups())

function loadCollapsedNavGroups(): string[] {
  try {
    const saved = JSON.parse(localStorage.getItem(NAV_GROUPS_STORAGE_KEY) ?? '[]')
    return Array.isArray(saved) ? saved.filter((item): item is string => typeof item === 'string') : []
  } catch {
    return []
  }
}

function isSectionOpen(title: string) {
  return !collapsedNavGroups.value.includes(title)
}

function toggleSection(title: string) {
  collapsedNavGroups.value = isSectionOpen(title)
    ? [...collapsedNavGroups.value, title]
    : collapsedNavGroups.value.filter((item) => item !== title)
  localStorage.setItem(NAV_GROUPS_STORAGE_KEY, JSON.stringify(collapsedNavGroups.value))
}

watch(
  () => route.path,
  (path) => {
    const activeSection = sections.value.find((section) =>
      section.items.some((item) => path === item.path || path.startsWith(`${item.path}/`)),
    )
    if (activeSection && !isSectionOpen(activeSection.title)) {
      collapsedNavGroups.value = collapsedNavGroups.value.filter((item) => item !== activeSection.title)
      localStorage.setItem(NAV_GROUPS_STORAGE_KEY, JSON.stringify(collapsedNavGroups.value))
    }
  },
  { immediate: true },
)

function toggleSidebar() {
  if (isMobile.value) {
    mobileSidebarOpen.value = !mobileSidebarOpen.value
    return
  }
  sidebarCollapsed.value = !sidebarCollapsed.value
  localStorage.setItem(SIDEBAR_STORAGE_KEY, sidebarCollapsed.value ? '1' : '0')
}

function handleResize() {
  const mobile = window.innerWidth <= 860
  if (isMobile.value !== mobile) {
    isMobile.value = mobile
    mobileSidebarOpen.value = false
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && mobileSidebarOpen.value) mobileSidebarOpen.value = false
}

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  window.addEventListener('keydown', handleKeydown)
  try {
    const health = await getHealth()
    healthOk.value = true
    version.value = health.version
  } catch {
    healthOk.value = false
  }
  getDashboardStreak()
    .then((s) => (streak.value = s.streak))
    .catch(() => (streak.value = null))
  getDashboardToday()
    .then((d) => (pendingCount.value = d.apply_todo.length))
    .catch(() => {})
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('keydown', handleKeydown)
})

async function onExport() {
  try {
    await exportBackup()
    ElMessage.success('完整 ZIP 备份已导出')
  } catch {
    /* 已由拦截器提示 */
  }
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100dvh;
  height: 100dvh;
  overflow: hidden;
}

/* ---------- 侧边栏 ---------- */
.sidebar {
  position: relative;
  width: 252px;
  flex-shrink: 0;
  background: var(--surface);
  border-right: 1px solid var(--line-strong);
  display: flex;
  flex-direction: column;
  z-index: 5;
  overflow: hidden;
  transition: width 0.22s cubic-bezier(0.16, 1, 0.3, 1), transform 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}
.sidebar-scrim {
  display: none;
}

/* 角落小涂鸦 */
.sb-doodle {
  position: absolute;
  pointer-events: none;
  z-index: 0;
}
.d-star1 {
  width: 26px;
  top: 74px;
  right: 18px;
  animation: doodle-float 5s ease-in-out infinite;
}
.d-star2 {
  width: 18px;
  bottom: 120px;
  right: 26px;
  animation: doodle-float 7s ease-in-out infinite reverse;
}
.d-spiral {
  width: 34px;
  bottom: 170px;
  left: -6px;
  opacity: 0.8;
}
.d-brow {
  width: 44px;
  top: 120px;
  left: 12px;
  animation: doodle-float 6s ease-in-out infinite;
}

.brand {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 19px 18px 15px;
  border-bottom: 1px solid color-mix(in srgb, var(--line) 78%, transparent);
}
.brand-logo {
  width: 46px;
  height: 46px;
  border-radius: 15px;
  background: var(--accent-soft);
  border: 1.5px solid var(--accent-line);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.plain-mark {
  font-size: 19px;
  font-weight: 700;
  color: var(--accent-strong);
  line-height: 1;
}
.brand-name {
  font-size: 16px;
  font-weight: 760;
  color: var(--ink);
  line-height: 1.25;
}
.brand-sub {
  font-size: 10px;
  letter-spacing: 0.18em;
  color: var(--ink-4);
  font-family: var(--font-mono);
  margin-top: 2px;
}

.nav {
  position: relative;
  z-index: 1;
  flex: 1;
  overflow-y: auto;
  padding: 5px 13px 16px;
}
.sidebar-collapse-row {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: flex-end;
  padding: 8px 13px 0;
}
.sidebar-collapse-button {
  min-height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 4px 9px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--surface-2);
  color: var(--ink-3);
  font: inherit;
  font-size: 11.5px;
  cursor: pointer;
  transition: border-color 0.18s, background 0.18s, color 0.18s;
}
.sidebar-collapse-button:hover {
  border-color: var(--accent-line);
  background: var(--accent-soft);
  color: var(--accent-strong);
}
.nav-section-title {
  width: calc(100% - 10px);
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 4px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  font-family: inherit;
  font-size: 11px;
  letter-spacing: 0.06em;
  color: var(--ink-4);
  margin: 15px 9px 6px;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
  transition: color 0.18s, background 0.18s;
}
.nav-section-title:hover {
  color: var(--ink-2);
  background: var(--surface-2);
}
.nav-section-title:focus-visible {
  outline: 2px solid var(--accent-line);
  outline-offset: 1px;
}
.nav-section-label {
  flex: 1;
}
.nav-section-chevron {
  font-size: 12px;
  color: var(--ink-4);
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), color 0.18s;
}
.nav-section-chevron.open {
  transform: rotate(90deg);
  color: var(--accent-strong);
}
.nav-section-items {
  overflow: hidden;
}
.nav-fold-enter-active,
.nav-fold-leave-active {
  max-height: 240px;
  overflow: hidden;
  transition: max-height 0.22s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.16s ease, transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.nav-fold-enter-from,
.nav-fold-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-4px);
}
.nst-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
  opacity: 0.6;
}
.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 11px;
  border-radius: 13px;
  color: var(--ink-2);
  text-decoration: none;
  font-size: 13.5px;
  transition: background 0.2s cubic-bezier(0.16, 1, 0.3, 1), color 0.2s, transform 0.2s;
}
.nav-item:hover {
  background: var(--surface-2);
  color: var(--ink);
  transform: translateX(2px);
}
.nav-item:hover .nav-icon {
  transform: rotate(-8deg) scale(1.12);
}
.nav-item.active {
  background: color-mix(in srgb, var(--accent-soft) 82%, var(--surface));
  color: var(--accent-strong);
  font-weight: 600;
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--accent-line) 55%, transparent);
}
.nav-indicator {
  position: absolute;
  left: -4px;
  top: 50%;
  transform: translateY(-50%) scaleY(0);
  width: 4px;
  height: 20px;
  border-radius: 4px;
  background: var(--accent);
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
.nav-item.active .nav-indicator {
  transform: translateY(-50%) scaleY(1);
}
.nav-icon {
  font-size: 15.5px;
  flex-shrink: 0;
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
.nav-label {
  flex: 1;
}
.nav-badge {
  background: var(--accent);
  color: #fff;
  font-size: 10.5px;
  font-weight: 600;
  border-radius: 999px;
  padding: 1px 6px;
  font-family: var(--font-mono);
}

.sidebar-foot {
  position: relative;
  z-index: 1;
  padding: 12px 14px 14px;
  border-top: 1px solid var(--line);
  background: linear-gradient(180deg, color-mix(in srgb, var(--accent-soft) 26%, transparent), transparent 58%);
}
.foot-mascot {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 0 0 8px;
  margin-left: -6px;
}
.foot-note {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 11px;
  color: var(--ink-3);
  line-height: 1.5;
}
.foot-note b {
  font-size: 11.5px;
  color: var(--ink-2);
  font-weight: 700;
}
.foot-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  padding: 8px 10px;
  border: 1.5px dashed var(--accent-line);
  border-radius: 12px;
  background: var(--accent-soft);
  color: var(--accent-strong);
  font-size: 12.5px;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}
.foot-btn:hover {
  border-style: solid;
  border-color: var(--accent);
}
.health {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
  font-size: 11px;
  color: var(--ink-3);
  justify-content: center;
}

/* ---------- 主区 ---------- */
.main {
  position: relative;
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

/* ---------- 手动收起 ---------- */
.layout.sidebar-collapsed .sidebar {
  width: 72px;
}
.layout.sidebar-collapsed .brand-text,
.layout.sidebar-collapsed .nav-label,
.layout.sidebar-collapsed .nav-badge,
.layout.sidebar-collapsed .nav-section-title,
.layout.sidebar-collapsed .sidebar-foot,
.layout.sidebar-collapsed .sb-doodle {
  display: none;
}
.layout.sidebar-collapsed .brand {
  justify-content: center;
  padding: 14px 8px;
}
.layout.sidebar-collapsed .nav {
  padding: 8px 10px;
}
.layout.sidebar-collapsed .sidebar-collapse-row {
  justify-content: center;
  padding: 8px 10px 0;
}
.layout.sidebar-collapsed .sidebar-collapse-button {
  width: 100%;
  padding-inline: 0;
}
.layout.sidebar-collapsed .sidebar-collapse-button span {
  display: none;
}
.layout.sidebar-collapsed .nav-item {
  justify-content: center;
  padding: 10px;
}
.layout.sidebar-collapsed .nav-item:hover {
  transform: none;
}
.ambient-mascot {
  position: fixed;
  right: -76px;
  bottom: -44px;
  opacity: 0.035;
  filter: grayscale(1);
  pointer-events: none;
  z-index: 0;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 70px;
  padding: 12px clamp(20px, 2.2vw, 34px);
  background: color-mix(in srgb, var(--bg-soft) 88%, transparent);
  backdrop-filter: blur(14px) saturate(1.08);
  border-bottom: 1px solid var(--line);
  position: sticky;
  top: 0;
  z-index: 4;
}
.topbar-title h1 {
  margin: 0;
  font-size: 19px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--ink);
  line-height: 1.25;
}
.topbar-title p {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--ink-3);
}
.topbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.palette-btn {
  position: relative;
  width: 34px;
  height: 34px;
  border-radius: 11px;
  border: 1px solid var(--line);
  background: var(--surface);
  color: var(--ink-2);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.palette-btn:hover {
  border-color: var(--accent-line);
  background: var(--accent-soft);
  color: var(--accent-strong);
}
.palette-dot {
  position: absolute;
  right: 4px;
  bottom: 4px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 1.5px solid var(--surface);
}
.date-chip,
.streak-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--surface);
  border: 1px solid var(--line);
  font-size: 12.5px;
  color: var(--ink-2);
}
.streak-chip.hot {
  border-color: var(--accent-line);
  color: var(--accent-strong);
  background: var(--accent-soft);
}
.streak-chip b {
  font-weight: 600;
}

.content {
  position: relative;
  z-index: 1;
  flex: 1;
  overflow-y: auto;
  padding: 26px clamp(20px, 2.2vw, 34px) 56px;
}
.topbar-start {
  display: flex;
  align-items: center;
  gap: 11px;
  min-width: 0;
}
.nav-toggle {
  width: 34px;
  height: 34px;
  flex: 0 0 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--line);
  border-radius: 11px;
  background: var(--surface);
  color: var(--ink-2);
  cursor: pointer;
  transition: border-color 0.18s, background 0.18s, color 0.18s, transform 0.18s;
}
.nav-toggle:hover {
  border-color: var(--accent-line);
  background: var(--accent-soft);
  color: var(--accent-strong);
}
.nav-toggle:active {
  transform: scale(0.96);
}

/* 路由切换过渡 */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.22s ease, transform 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}
.page-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (max-width: 860px) {
  .sidebar {
    position: fixed;
    inset: 0 auto 0 0;
    width: min(284px, 86vw);
    transform: translateX(-102%);
    box-shadow: var(--shadow-2);
    z-index: 30;
  }
  .layout.mobile-open .sidebar {
    transform: translateX(0);
  }
  .sidebar-scrim {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 29;
    border: 0;
    background: rgba(28, 26, 23, 0.28);
    backdrop-filter: blur(2px);
  }
  .content {
    padding: 16px;
  }
  .topbar {
    padding: 12px 16px;
  }
  .date-chip {
    display: none;
  }
  .ambient-mascot {
    display: none;
  }
}
@media (max-width: 640px) {
  .topbar-title p,
  .streak-chip {
    display: none;
  }
  .topbar-actions {
    gap: 6px;
  }
}
</style>
