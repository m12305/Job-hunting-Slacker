<!-- ============================================================
   蜡笔小新风吉祥物 · 小新狗（原创 Q 版：蘑菇头 + 粗眉毛 + 红 T 恤 + 黄短裤）
   自用非盈利项目形象参考；黑色描边 + 标志性粗眉
   三种姿势：坐 / 挥手 / 呼呼大睡
   ============================================================ -->
<template>
  <svg
    :width="size"
    :height="size * 0.94"
    viewBox="0 0 140 132"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="shin-boy"
    :class="className"
    role="img"
    aria-label="小新狗"
  >
    <!-- 地面阴影 -->
    <ellipse cx="70" cy="124" rx="30" ry="5" fill="#1c1a17" opacity="0.07" />

    <!-- 黄色短裤 -->
    <rect x="52" y="94" width="36" height="22" rx="8" fill="#ffbe2e" stroke="#1c1a17" stroke-width="3.5" />

    <!-- 小短腿 + 小脚 -->
    <rect x="58" y="112" width="10" height="12" rx="5" fill="#ffd9b0" stroke="#1c1a17" stroke-width="3" />
    <rect x="72" y="112" width="10" height="12" rx="5" fill="#ffd9b0" stroke="#1c1a17" stroke-width="3" />

    <!-- 红色 T 恤 -->
    <path
      d="M56 76 C56 66 62 62 70 62 C78 62 84 66 84 76 V94 C84 98 80 100 70 100 C60 100 56 98 56 94 Z"
      fill="#d63b30"
      stroke="#1c1a17"
      stroke-width="3.5"
      stroke-linejoin="round"
    />
    <!-- 白色圆领 -->
    <path d="M62 62 q8 -6 16 0" fill="#ffffff" stroke="#1c1a17" stroke-width="3" stroke-linejoin="round" />

    <!-- 左手 -->
    <path
      d="M56 78 C50 80 46 86 44 92"
      fill="#ffd9b0"
      stroke="#1c1a17"
      stroke-width="3.5"
      stroke-linecap="round"
    />

    <!-- 大头 -->
    <circle cx="70" cy="46" r="27" fill="#ffd9b0" stroke="#1c1a17" stroke-width="3.5" />

    <!-- 蘑菇头 -->
    <path
      d="M45 48 C45 22 95 22 95 48 C95 42 88 36 70 36 C52 36 45 42 45 48 Z"
      fill="#1f1d1a"
      stroke="#1c1a17"
      stroke-width="3.5"
      stroke-linejoin="round"
    />

    <!-- 标志性粗眉毛 -->
    <path d="M50 55 q9 8 18 0" stroke="#1c1a17" stroke-width="5.5" stroke-linecap="round" />
    <path d="M72 55 q9 8 18 0" stroke="#1c1a17" stroke-width="5.5" stroke-linecap="round" />

    <!-- 脸部 -->
    <template v-if="pose === 'zzz'">
      <path d="M56 66 q4 -4 8 0" stroke="#1c1a17" stroke-width="3" stroke-linecap="round" />
      <path d="M76 66 q4 -4 8 0" stroke="#1c1a17" stroke-width="3" stroke-linecap="round" />
      <text x="106" y="40" style="font-family: var(--font-mono)" font-size="17" font-weight="600" fill="#1c1a17">Z</text>
      <text x="119" y="29" style="font-family: var(--font-mono)" font-size="12" font-weight="600" fill="#1c1a17">Z</text>
      <text x="129" y="20" style="font-family: var(--font-mono)" font-size="9" font-weight="600" fill="#1c1a17">z</text>
    </template>
    <template v-else>
      <circle cx="60" cy="68" r="3.4" fill="#1c1a17" />
      <circle cx="58.8" cy="66.8" r="1.2" fill="#ffffff" />
      <circle cx="80" cy="68" r="3.4" fill="#1c1a17" />
      <circle cx="78.8" cy="66.8" r="1.2" fill="#ffffff" />
      <path d="M66 75 q4 5 8 0" stroke="#1c1a17" stroke-width="2.8" stroke-linecap="round" />
    </template>

    <!-- 腮红 -->
    <circle cx="52" cy="72" r="3.4" fill="#ff9d9d" opacity="0.55" />
    <circle cx="88" cy="72" r="3.4" fill="#ff9d9d" opacity="0.55" />

    <!-- 挥手姿势：右手抬起 -->
    <g v-if="pose === 'wave'">
      <path
        d="M90 84 C98 78 102 70 100 60"
        fill="#ffd9b0"
        stroke="#1c1a17"
        stroke-width="3.5"
        stroke-linejoin="round"
      />
      <circle cx="101" cy="56" r="5.5" fill="#ffd9b0" stroke="#1c1a17" stroke-width="3" />
      <path d="M110 48 q8 5 10 13" stroke="#1c1a17" stroke-width="2.6" stroke-linecap="round" opacity="0.45" />
      <path d="M118 42 q8 5 9 12" stroke="#1c1a17" stroke-width="2.2" stroke-linecap="round" opacity="0.3" />
    </g>
  </svg>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    pose?: 'sit' | 'wave' | 'zzz'
    size?: number
    className?: string
  }>(),
  { pose: 'sit', size: 88 },
)
</script>

<style scoped>
.shin-boy {
  display: block;
  overflow: visible;
}
</style>