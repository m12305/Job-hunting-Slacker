import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    icon?: string
    section?: string
  }
}

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/dashboard' },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      { path: 'dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue'), meta: { title: '今日看板', icon: 'Calendar', section: '总览' } },
      { path: 'stats', name: 'stats', component: () => import('@/views/stats/StatsView.vue'), meta: { title: '数据看板', icon: 'TrendCharts', section: '总览' } },
      { path: 'resumes', name: 'resumes', component: () => import('@/views/resumes/ResumesView.vue'), meta: { title: '简历版本', icon: 'Document', section: '简历与资产' } },
      { path: 'materials', name: 'materials', component: () => import('@/views/materials/MaterialsView.vue'), meta: { title: '素材库', icon: 'Notebook', section: '简历与资产' } },
      { path: 'assets', name: 'assets', component: () => import('@/views/assets/AssetsView.vue'), meta: { title: '资产归档', icon: 'FolderOpened', section: '简历与资产' } },
      { path: 'applications', name: 'applications', component: () => import('@/views/applications/ApplicationsView.vue'), meta: { title: '投递管理', icon: 'Promotion', section: '投递与 Offer' } },
      { path: 'offers', name: 'offers', component: () => import('@/views/offers/OffersView.vue'), meta: { title: 'Offer 管理', icon: 'Medal', section: '投递与 Offer' } },
      { path: 'offers/compare', name: 'offer-compare', component: () => import('@/views/offers/OfferCompareView.vue'), meta: { title: 'Offer 对比', icon: 'DataAnalysis', section: '投递与 Offer' } },
      { path: 'exams', name: 'exams', component: () => import('@/views/exams/ExamsView.vue'), meta: { title: '笔试管理', icon: 'EditPen', section: '笔试与面试' } },
      { path: 'interviews', name: 'interviews', component: () => import('@/views/interviews/InterviewsView.vue'), meta: { title: '面试管理', icon: 'ChatLineSquare', section: '笔试与面试' } },
      { path: 'questions', name: 'questions', component: () => import('@/views/questions/QuestionsView.vue'), meta: { title: '题库', icon: 'Reading', section: '笔试与面试' } },
      { path: 'scripts', name: 'scripts', component: () => import('@/views/scripts/ScriptsView.vue'), meta: { title: '话术库', icon: 'MagicStick', section: '工具箱' } },
      { path: 'blacklist', name: 'blacklist', component: () => import('@/views/blacklist/BlacklistView.vue'), meta: { title: '避雷库', icon: 'Warning', section: '工具箱' } },
      { path: 'appearance', name: 'appearance', component: () => import('@/views/appearance/AppearanceView.vue'), meta: { title: '外观设置', icon: 'Brush', section: '工具箱' } },
      { path: 'settings', name: 'settings', component: () => import('@/views/settings/SettingsView.vue'), meta: { title: '设置', icon: 'Setting', section: '工具箱' } },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · 求职摆烂管理局` : '求职摆烂管理局'
})

export default router