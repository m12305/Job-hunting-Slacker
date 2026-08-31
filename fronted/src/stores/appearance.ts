/* ============================================================
   外观设置 Store：主题风格（原始 / 线条小狗 / 蜡笔小新）
   + 配色（预设色板 / 自定义颜色）+ 壁纸 / 透明度（localStorage 持久化）
   ============================================================ */
import { defineStore } from 'pinia'

/* ---------- 配色预设：只提供强调色，柔和色由 CSS color-mix 派生 ---------- */
export interface AccentPreset {
  key: string
  name: string
  accent: string
}

export const ACCENT_PRESETS: AccentPreset[] = [
  { key: 'tangerine', name: '秋柿橙', accent: '#b45309' },
  { key: 'matcha', name: '抹茶绿', accent: '#4d7c0f' },
  { key: 'peach', name: '桃子汽水', accent: '#d63d7a' },
  { key: 'butter', name: '黄油曲奇', accent: '#a16207' },
  { key: 'sky', name: '雪山青', accent: '#0369a1' },
  { key: 'grape', name: '葡萄果冻', accent: '#6d28d9' },
  { key: 'tomato', name: '番茄锅底', accent: '#c2352f' },
  { key: 'shinred', name: '小新红', accent: '#d63b30' },
]

/* ---------- 主题风格：决定吉祥物 / 涂鸦 / 字体 / 默认配色 ---------- */
export type ThemeKindKey = 'original' | 'linedog' | 'shinchan'

export interface ThemeKindMeta {
  key: ThemeKindKey
  name: string
  desc: string
  mascot: 'none' | 'dog' | 'shin'
  bg: string
  bgSoft: string
  accent2: string
  defaultPreset: string
}

export const THEME_KINDS: ThemeKindMeta[] = [
  {
    key: 'original',
    name: '原始主题',
    desc: '清爽克制的经典界面，无吉祥物与涂鸦',
    mascot: 'none',
    bg: '#f4f3ef',
    bgSoft: '#faf9f6',
    accent2: '#0f766e',
    defaultPreset: 'tangerine',
  },
  {
    key: 'linedog',
    name: '线条小狗',
    desc: '大头垂耳 ω 嘴的软萌小狗陪你摆烂',
    mascot: 'dog',
    bg: '#f6f3ee',
    bgSoft: '#fbf9f5',
    accent2: '#d63d7a',
    defaultPreset: 'tangerine',
  },
  {
    key: 'shinchan',
    name: '蜡笔小新',
    desc: '粗眉毛红 T 恤黄短裤的快乐时光',
    mascot: 'shin',
    bg: '#faf3e8',
    bgSoft: '#fdf8f0',
    accent2: '#ffbe2e',
    defaultPreset: 'shinred',
  },
]

interface AppearanceState {
  themeKind: ThemeKindKey
  accentMode: 'preset' | 'custom'
  accentPresetKey: string
  customAccent: string
  /** 壁纸：压缩后的 dataURL */
  bgImage: string | null
  /** 壁纸不透明度 0-100 */
  bgOpacity: number
}

const STORAGE_KEY = 'qzy.appearance.v2'

function loadState(): AppearanceState {
  const fallback: AppearanceState = {
    themeKind: 'linedog',
    accentMode: 'preset',
    accentPresetKey: 'tangerine',
    customAccent: '#b45309',
    bgImage: null,
    bgOpacity: 72,
  }
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) {
      // 迁移旧版 v1（只有 themeKey 配色）
      const old = localStorage.getItem('qzy.appearance.v1')
      if (old) {
        try {
          const p = JSON.parse(old)
          return {
            themeKind: 'linedog',
            accentMode: 'preset',
            accentPresetKey: ACCENT_PRESETS.some((x) => x.key === p.themeKey) ? p.themeKey : 'tangerine',
            customAccent: '#b45309',
            bgImage: typeof p.bgImage === 'string' ? p.bgImage : null,
            bgOpacity: typeof p.bgOpacity === 'number' ? p.bgOpacity : 72,
          }
        } catch {
          /* 忽略旧数据 */
        }
      }
      return fallback
    }
    const p = JSON.parse(raw) as Partial<AppearanceState>
    return {
      themeKind: THEME_KINDS.some((k) => k.key === p.themeKind) ? p.themeKind! : fallback.themeKind,
      accentMode: p.accentMode === 'custom' ? 'custom' : 'preset',
      accentPresetKey: ACCENT_PRESETS.some((x) => x.key === p.accentPresetKey) ? p.accentPresetKey! : 'tangerine',
      customAccent: typeof p.customAccent === 'string' && /^#[0-9a-fA-F]{6}$/.test(p.customAccent) ? p.customAccent : '#b45309',
      bgImage: typeof p.bgImage === 'string' ? p.bgImage : null,
      bgOpacity: typeof p.bgOpacity === 'number' ? Math.max(0, Math.min(100, p.bgOpacity)) : 72,
    }
  } catch {
    return fallback
  }
}

function persist(state: AppearanceState) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch {
    /* 壁纸过大导致配额超限时静默（UI 层另有提示） */
  }
}

export const useAppearanceStore = defineStore('appearance', {
  state: (): AppearanceState => loadState(),
  getters: {
    kindMeta(state): ThemeKindMeta {
      return THEME_KINDS.find((k) => k.key === state.themeKind) ?? THEME_KINDS[1]
    },
    mascot(state): 'none' | 'dog' | 'shin' {
      return this.kindMeta.mascot
    },
    /** 有效强调色：自定义优先，否则取预设 */
    accent(state): string {
      if (state.accentMode === 'custom') return state.customAccent
      return ACCENT_PRESETS.find((p) => p.key === state.accentPresetKey)?.accent ?? '#b45309'
    },
    accent2(): string {
      return this.kindMeta.accent2
    },
    bg(): string {
      return this.kindMeta.bg
    },
    bgSoft(): string {
      return this.kindMeta.bgSoft
    },
    currentPresetName(state): string {
      return ACCENT_PRESETS.find((p) => p.key === state.accentPresetKey)?.name ?? '预设'
    },
    wallpaperVisible: (state) => !!state.bgImage && state.bgOpacity > 0,
  },
  actions: {
    /** 将主题风格与配色写入 CSS 变量与 data-theme，壁纸状态写入 body */
    apply() {
      const root = document.documentElement
      root.dataset.theme = this.themeKind
      root.style.setProperty('--accent', this.accent)
      root.style.setProperty('--accent-2', this.accent2)
      root.style.setProperty('--bg', this.bg)
      root.style.setProperty('--bg-soft', this.bgSoft)
      document.body.classList.toggle('has-wallpaper', this.wallpaperVisible)
    },
    setThemeKind(key: ThemeKindKey) {
      const meta = THEME_KINDS.find((k) => k.key === key)
      if (!meta) return
      this.themeKind = key
      // 预设模式下跟随新主题的默认配色；自定义配色保留用户选择
      if (this.accentMode === 'preset') {
        this.accentPresetKey = meta.defaultPreset
      }
      persist(this.$state)
      this.apply()
    },
    setAccentPreset(key: string) {
      if (!ACCENT_PRESETS.some((p) => p.key === key)) return
      this.accentMode = 'preset'
      this.accentPresetKey = key
      persist(this.$state)
      this.apply()
    },
    setCustomAccent(hex: string) {
      if (!/^#[0-9a-fA-F]{6}$/.test(hex)) return
      this.accentMode = 'custom'
      this.customAccent = hex.toLowerCase()
      persist(this.$state)
      this.apply()
    },
    setBgImage(dataUrl: string | null) {
      this.bgImage = dataUrl
      persist(this.$state)
      this.apply()
    },
    setBgOpacity(v: number) {
      this.bgOpacity = Math.max(0, Math.min(100, Math.round(v)))
      persist(this.$state)
      this.apply()
    },
    resetAppearance() {
      this.themeKind = 'linedog'
      this.accentMode = 'preset'
      this.accentPresetKey = 'tangerine'
      this.customAccent = '#b45309'
      this.bgImage = null
      this.bgOpacity = 72
      persist(this.$state)
      this.apply()
    },
  },
})