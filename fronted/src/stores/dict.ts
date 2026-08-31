/* 共享字典：岗位类型 / 素材分类等跨页引用数据 */
import { defineStore } from 'pinia'
import { listJobTypes, listMaterialCategories } from '@/api'
import type { JobType } from '@/types'

export const useDictStore = defineStore('dict', {
  state: () => ({
    jobTypes: [] as JobType[],
    materialCategories: [] as string[],
    jobTypesLoaded: false,
    materialCategoriesLoaded: false,
  }),
  getters: {
    jobTypeName: (state) => (id: number | null | undefined) => {
      if (!id) return '未分类'
      return state.jobTypes.find((j) => j.id === id)?.name ?? '未分类'
    },
    jobTypeColor: (state) => (id: number | null | undefined) => {
      if (!id) return '#8f8a83'
      return state.jobTypes.find((j) => j.id === id)?.color || '#8f8a83'
    },
  },
  actions: {
    async ensureJobTypes(force = false) {
      if (this.jobTypesLoaded && !force) return
      try {
        this.jobTypes = await listJobTypes()
        this.jobTypesLoaded = true
      } catch {
        /* 后端未就绪时静默，列表页各自兜底 */
      }
    },
    async ensureMaterialCategories(force = false) {
      if (this.materialCategoriesLoaded && !force) return
      try {
        this.materialCategories = await listMaterialCategories()
        this.materialCategoriesLoaded = true
      } catch {
        /* 忽略 */
      }
    },
  },
})