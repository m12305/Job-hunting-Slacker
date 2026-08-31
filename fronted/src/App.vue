<template>
  <div class="app-root">
    <!-- 壁纸层（外观设置上传的背景图；透明底主题色始终在 body 上） -->
    <div
      v-if="appearance.bgImage"
      class="wallpaper"
      :style="{
        backgroundImage: `url(${appearance.bgImage})`,
        opacity: appearance.bgOpacity / 100,
      }"
    />
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAppearanceStore } from '@/stores/appearance'

const appearance = useAppearanceStore()

onMounted(() => {
  appearance.apply()
})
</script>

<style>
.app-root {
  height: 100%;
}
</style>