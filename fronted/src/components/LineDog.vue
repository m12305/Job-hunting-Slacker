<!-- ============================================================
   线条小狗（网上流行的形象：大头 + 长垂耳 + 圆点眼 + ω 嘴 + 小身体）
   黑色粗描边 + 白色填充；三种姿势：坐 / 挥手 / 呼呼大睡
   ============================================================ -->
<template>
  <svg
    :width="size"
    :height="size * 0.94"
    viewBox="0 0 140 132"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="line-dog"
    :class="className"
    role="img"
    aria-label="线条小狗"
  >
    <!-- 地面阴影 -->
    <ellipse cx="70" cy="120" rx="30" ry="5" fill="#1c1a17" opacity="0.07" />

    <!-- 尾巴 -->
    <path d="M96 98 C110 94 114 82 108 74" stroke="#1c1a17" stroke-width="3.5" stroke-linecap="round" />

    <!-- 身体（小巧） -->
    <path
      d="M50 92 C46 104 48 112 52 118 H88 C94 112 96 102 90 92 C82 86 58 86 50 92 Z"
      fill="#ffffff"
      stroke="#1c1a17"
      stroke-width="3.5"
      stroke-linejoin="round"
    />

    <!-- 小短腿 -->
    <rect x="56" y="111" width="11" height="10" rx="5" fill="#ffffff" stroke="#1c1a17" stroke-width="3.5" />
    <rect x="73" y="111" width="11" height="10" rx="5" fill="#ffffff" stroke="#1c1a17" stroke-width="3.5" />

    <!-- 大头 -->
    <circle cx="70" cy="56" r="34" fill="#ffffff" stroke="#1c1a17" stroke-width="3.5" />

    <!-- 长垂耳（煎饼耳） -->
    <path
      d="M46 32 C30 34 22 52 28 84 L38 80 C36 66 42 56 50 46 Z"
      fill="#ffffff"
      stroke="#1c1a17"
      stroke-width="3.5"
      stroke-linejoin="round"
    />
    <path
      d="M94 32 C110 34 118 52 112 84 L102 80 C104 66 98 56 90 46 Z"
      fill="#ffffff"
      stroke="#1c1a17"
      stroke-width="3.5"
      stroke-linejoin="round"
    />

    <!-- 头顶呆毛 -->
    <path d="M60 23 q3 -7 8 -4" stroke="#1c1a17" stroke-width="3.2" stroke-linecap="round" />

    <!-- 脸部 -->
    <template v-if="pose === 'zzz'">
      <path d="M56 53 q4 -5 8 0" stroke="#1c1a17" stroke-width="3" stroke-linecap="round" />
      <path d="M76 53 q4 -5 8 0" stroke="#1c1a17" stroke-width="3" stroke-linecap="round" />
      <text x="104" y="42" style="font-family: var(--font-mono)" font-size="17" font-weight="600" fill="#1c1a17">Z</text>
      <text x="117" y="31" style="font-family: var(--font-mono)" font-size="12" font-weight="600" fill="#1c1a17">Z</text>
      <text x="127" y="22" style="font-family: var(--font-mono)" font-size="9" font-weight="600" fill="#1c1a17">z</text>
    </template>
    <template v-else>
      <!-- 圆点眼 + 高光 -->
      <circle cx="60" cy="54" r="3.4" fill="#1c1a17" />
      <circle cx="58.6" cy="52.6" r="1.2" fill="#ffffff" />
      <circle cx="80" cy="54" r="3.4" fill="#1c1a17" />
      <circle cx="78.6" cy="52.6" r="1.2" fill="#ffffff" />
      <!-- ω 嘴 -->
      <path d="M62 68 q4 6 8 0 q4 6 8 0" stroke="#1c1a17" stroke-width="3" stroke-linecap="round" />
    </template>

    <!-- 小鼻子 -->
    <ellipse cx="70" cy="63" rx="3" ry="2.6" fill="#1c1a17" />

    <!-- 腮红小线 -->
    <path d="M52 64 q3 -2 5 0" stroke="#d63d7a" stroke-width="2.2" stroke-linecap="round" opacity="0.55" />
    <path d="M83 64 q3 -2 5 0" stroke="#d63d7a" stroke-width="2.2" stroke-linecap="round" opacity="0.55" />

    <!-- 挥手姿势：右前爪抬起 -->
    <g v-if="pose === 'wave'">
      <path
        d="M88 96 C96 88 104 78 102 64"
        fill="#ffffff"
        stroke="#1c1a17"
        stroke-width="3.5"
        stroke-linejoin="round"
      />
      <circle cx="103" cy="61" r="5.5" fill="#ffffff" stroke="#1c1a17" stroke-width="3" />
      <path d="M110 52 q8 5 10 13" stroke="#1c1a17" stroke-width="2.6" stroke-linecap="round" opacity="0.45" />
      <path d="M118 46 q8 5 9 12" stroke="#1c1a17" stroke-width="2.2" stroke-linecap="round" opacity="0.3" />
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
.line-dog {
  display: block;
  overflow: visible;
}
</style>