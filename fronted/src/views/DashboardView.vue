<template>
  <div class="page">
    <div class="hero">
      <div class="hero-left">
        <div v-if="appearance.mascot !== 'none'" class="hero-mascot dog-wiggle">
          <ThemeMascot pose="wave" :size="74" />
          <div class="speech">{{ heroLine }}</div>
        </div>
        <div>
          <div class="hero-kicker">求职摆烂管理局 · 今日值班 {{ fmtDate(today.date || new Date().toISOString()) }}</div>
          <h1 class="hero-title fun">{{ greeting }}</h1>
          <p class="hero-desc">
            待投递 {{ today.apply_todo?.length || 0 }} 项 · 待复盘 {{ today.review_todo?.length || 0 }} 项 ·
            待刷题 {{ today.question_todo?.length || 0 }} 题 · 今日任务 {{ doneCount }}/{{ today.tasks?.length || 0 }}
          </p>
        </div>
      </div>
      <div class="hero-action">
        <el-button type="primary" size="large" @click="openTask"><el-icon><Plus /></el-icon>&nbsp;添加今日任务</el-button>
      </div>
    </div>

    <el-skeleton v-if="loading" :rows="9" animated class="panel" style="padding: 20px" />

    <div v-else class="dash-grid">
      <!-- 左列 -->
      <div class="col-main">
        <!-- 今日任务 -->
        <section class="panel block">
          <div class="block-head">
            <div>
              <div class="block-title">今日任务 · 打卡闭环</div>
              <div class="block-sub">每完成一项就打卡，连续天数会显示在右上角</div>
            </div>
            <div class="block-progress">
              <span class="mono">{{ doneCount }} / {{ today.tasks?.length || 0 }}</span>
              <div class="mini-bar">
                <div class="mini-fill" :style="{ width: progressPct + '%' }" />
              </div>
            </div>
          </div>

          <div v-if="!today.tasks?.length" class="task-empty">
            <EmptyState icon="Checked" title="今天还没有安排任务" desc="添加投递、复盘、刷题等打卡项，让秋招节奏可视化。" />
          </div>
          <div v-else class="task-list">
            <div v-for="t in today.tasks" :key="t.id" class="task-row" :class="{ done: t.done }">
              <button class="task-check" :class="{ checked: t.done }" @click="toggleTask(t)">
                <el-icon v-if="t.done"><Check /></el-icon>
              </button>
              <div class="task-main">
                <span class="task-title">{{ t.title }}</span>
                <span v-if="t.task_type" class="task-type">{{ labelOf(TASK_TYPES, t.task_type) }}</span>
              </div>
              <span v-if="t.done_at" class="mono task-done-at muted">{{ fmtDateTime(t.done_at) }} 打卡</span>
              <button class="op danger" @click="removeTask(t)"><el-icon><Delete /></el-icon></button>
            </div>
          </div>
        </section>

        <!-- 待投递 -->
        <section class="panel block">
          <div class="block-head">
            <div>
              <div class="block-title">待投递岗位</div>
              <div class="block-sub">状态仍为「待投递」的记录，别让它们停在草稿里</div>
            </div>
            <el-button size="small" text type="primary" @click="router.push('/applications?status=pending')">全部 →</el-button>
          </div>
          <div v-if="!today.apply_todo?.length" class="mini-empty muted">没有待投递的岗位，今天可以专注复盘与刷题。</div>
          <div v-else class="todo-list">
            <button v-for="a in today.apply_todo" :key="a.id" class="todo-row" @click="goApp(a.id)">
              <div class="todo-main">
                <span class="todo-company">{{ a.company }}</span>
                <span class="todo-pos">{{ a.position }}</span>
                <span v-if="a.city" class="todo-city">{{ a.city }}</span>
              </div>
              <span class="go-chip">去投递 <el-icon><ArrowRight /></el-icon></span>
            </button>
          </div>
        </section>

        <!-- 待复盘 -->
        <section class="panel block">
          <div class="block-head">
            <div>
              <div class="block-title">待复盘</div>
              <div class="block-sub">已结束但还没写复盘 / 结果的笔面试</div>
            </div>
          </div>
          <div v-if="!today.review_todo?.length" class="mini-empty muted">太棒了，所有已结束的笔面试都复盘完了。</div>
          <div v-else class="todo-list">
            <button v-for="r in today.review_todo" :key="`${r.type}-${r.id}`" class="todo-row" @click="goReview(r)">
              <div class="todo-rev-icon" :class="r.type">
                <el-icon><component :is="r.type === 'exam' ? 'EditPen' : 'ChatLineSquare'" /></el-icon>
              </div>
              <div class="todo-main">
                <span class="todo-company">{{ r.title }}</span>
              </div>
              <span class="go-chip">{{ r.type === 'exam' ? '写复盘' : '记结果' }} <el-icon><ArrowRight /></el-icon></span>
            </button>
          </div>
        </section>

        <!-- 待刷题 -->
        <section class="panel block">
          <div class="block-head">
            <div>
              <div class="block-title">待刷题库</div>
              <div class="block-sub">标记为「新 / 待刷」的题目，每天滚动复习几道</div>
            </div>
            <el-button size="small" text type="primary" @click="router.push('/questions')">全部 →</el-button>
          </div>
          <div v-if="!today.question_todo?.length" class="mini-empty muted">题库已清空或全部掌握，去收录新题吧。</div>
          <div v-else class="todo-list">
            <button v-for="q in today.question_todo" :key="q.id" class="todo-row" @click="router.push('/questions')">
              <div class="todo-main">
                <span class="todo-company">{{ q.title }}</span>
                <span v-if="q.category" class="q-tag">{{ labelOf(QUESTION_CATEGORIES, q.category) }}</span>
                <span v-if="q.difficulty" class="q-tag diff">{{ labelOf(QUESTION_DIFFICULTY, q.difficulty) }}</span>
              </div>
              <span class="go-chip">去刷 <el-icon><ArrowRight /></el-icon></span>
            </button>
          </div>
        </section>
      </div>

      <!-- 右列 -->
      <div class="col-side">
        <section class="panel block streak-card">
          <div class="streak-num mono">{{ today.streak || 0 }}<span>天</span></div>
          <div class="streak-label">连续打卡</div>
          <div class="week-progress">
            <div class="week-line">
              <div class="week-fill" :style="{ width: weekPct + '%' }" />
            </div>
            <div class="week-text">
              <span class="mono">本周 {{ today.week_done || 0 }}/{{ today.week_total || 0 }}</span>
              <span class="muted">任务完成</span>
            </div>
          </div>
          <div class="streak-tip">
            <el-icon><Opportunity /></el-icon>
            <span>{{ streakTip }}</span>
          </div>
        </section>

        <section class="panel block">
          <div class="block-title">快捷入口</div>
          <div class="quick-grid">
            <button v-for="q in quickLinks" :key="q.path" class="quick-btn" @click="router.push(q.path)">
              <el-icon><component :is="q.icon" /></el-icon>
              <span>{{ q.label }}</span>
            </button>
          </div>
        </section>
      </div>
    </div>

    <!-- 新增任务 -->
    <el-dialog v-model="taskVisible" title="添加今日任务" width="440px" destroy-on-close>
      <el-form :model="taskForm" label-position="top">
        <el-form-item label="任务内容" required>
          <el-input v-model="taskForm.title" maxlength="300" placeholder="如 投递字节后端 / 复盘阿里一面" />
        </el-form-item>
        <el-form-item label="任务类型">
          <el-select v-model="taskForm.task_type" style="width: 100%">
            <el-option v-for="(v, k) in TASK_TYPES" :key="k" :label="v.label" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="归属日期">
          <el-date-picker v-model="taskForm.due_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!taskForm.title.trim()" :loading="taskSaving" @click="saveTask">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import EmptyState from '@/components/EmptyState.vue'
import ThemeMascot from '@/components/ThemeMascot.vue'
import { useAppearanceStore } from '@/stores/appearance'
import { createTask, deleteTask, getDashboardToday, setTaskDone } from '@/api'
import type { DashboardToday, Task } from '@/types'
import { QUESTION_CATEGORIES, QUESTION_DIFFICULTY, TASK_TYPES, labelOf } from '@/constants'
import { fmtDate, fmtDateTime } from '@/utils/format'

const router = useRouter()
const appearance = useAppearanceStore()
const today = ref<DashboardToday>({
  date: new Date().toISOString(),
  apply_todo: [],
  review_todo: [],
  question_todo: [],
  tasks: [],
  streak: 0,
  week_done: 0,
  week_total: 0,
})
const loading = ref(false)

const hour = new Date().getHours()
const greeting = hour < 6 ? '夜深了，先睡，明天再摆' : hour < 11 ? '早上好，开工前先摆五分钟' : hour < 14 ? '中午好，吃饱才有力气摸鱼' : hour < 18 ? '下午好，进度条还差一截' : '晚上好，今日摆烂指标达标了吗'

/* 局长批示：根据今日数据生成趣味台词 */
const heroLine = computed(() => {
  const t = today.value
  const pend = t.apply_todo?.length || 0
  const rev = t.review_todo?.length || 0
  const ques = t.question_todo?.length || 0
  const tasks = t.tasks?.length || 0
  if (!pend && !rev && !ques && !tasks) return '今日无事可干，本局宣布：摆烂也要摆出仪式感。'
  if (t.streak >= 7) return `连续打卡 ${t.streak} 天，本局实名表扬，继续保持。`
  if (pend > 0) return `还有 ${pend} 个岗位没投，再懒下去就要烂在草稿箱了。`
  if (rev > 0) return `有 ${rev} 场笔面试等着复盘，回忆是会过期的。`
  if (ques > 0) return `还有 ${ques} 道题待刷，刷一道是一道。`
  return '今日任务都在手上，冲就完事了。'
})
const doneCount = computed(() => today.value.tasks?.filter((t) => t.done).length ?? 0)
const progressPct = computed(() =>
  today.value.tasks?.length ? Math.round((doneCount.value / today.value.tasks.length) * 100) : 0,
)
const weekPct = computed(() =>
  today.value.week_total ? Math.round((today.value.week_done / today.value.week_total) * 100) : 0,
)
const streakTip = computed(() => {
  if (today.value.streak >= 7) return '连续一整周，节奏保持得很好'
  if (today.value.streak >= 3) return '三连胜，离习惯只差一步'
  return '坚持每天打卡，把秋招变成例行公事'
})

const quickLinks = [
  { label: '新增投递', path: '/applications', icon: 'Promotion' },
  { label: '录入笔试', path: '/exams', icon: 'EditPen' },
  { label: '录入面试', path: '/interviews', icon: 'ChatLineSquare' },
  { label: '收录题目', path: '/questions', icon: 'Reading' },
  { label: '话术库', path: '/scripts', icon: 'MagicStick' },
  { label: 'Offer 对比', path: '/offers/compare', icon: 'DataAnalysis' },
]

async function load() {
  loading.value = true
  try {
    today.value = await getDashboardToday()
  } catch {
    /* 拦截器提示 */
  } finally {
    loading.value = false
  }
}

/* ---- 任务 ---- */
const taskVisible = ref(false)
const taskSaving = ref(false)
const taskForm = reactive({ title: '', task_type: 'custom', due_date: '' })

function openTask() {
  taskForm.title = ''
  taskForm.task_type = 'custom'
  taskForm.due_date = today.value.date
  taskVisible.value = true
}
async function saveTask() {
  taskSaving.value = true
  try {
    await createTask({ title: taskForm.title.trim(), task_type: taskForm.task_type, due_date: taskForm.due_date || today.value.date })
    ElMessage.success('任务已添加')
    taskVisible.value = false
    load()
  } finally {
    taskSaving.value = false
  }
}
async function toggleTask(t: Task) {
  await setTaskDone(t.id, !t.done)
  load()
}
async function removeTask(t: Task) {
  await ElMessageBox.confirm(`移除任务「${t.title}」？`, '删除任务', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteTask(t.id)
  load()
}

/* ---- 跳转 ---- */
function goApp(id: number) {
  router.push({ path: '/applications', query: { focus: id } })
}
function goReview(r: { type: string; id: number }) {
  router.push({ path: r.type === 'exam' ? '/exams' : '/interviews', query: { focus: r.id } })
}

onMounted(load)
</script>

<style scoped>
.hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}
.hero-left {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}
.hero-mascot {
  position: relative;
  flex-shrink: 0;
}
.speech {
  position: absolute;
  left: calc(100% - 6px);
  top: 8px;
  max-width: 300px;
  background: var(--surface);
  border: 1.5px solid var(--accent-line);
  border-radius: 14px;
  padding: 9px 13px;
  font-size: 12.5px;
  line-height: 1.6;
  color: var(--ink-2);
  box-shadow: var(--shadow-1);
  z-index: 2;
}
.speech::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 18px;
  border: 7px solid transparent;
  border-right-color: var(--accent-line);
}
.speech::after {
  content: '';
  position: absolute;
  left: -5px;
  top: 19px;
  border: 6px solid transparent;
  border-right-color: var(--surface);
}
@media (max-width: 640px) {
  .speech {
    position: static;
    margin-top: 6px;
    max-width: 100%;
  }
  .speech::before,
  .speech::after {
    display: none;
  }
}
.hero-kicker {
  font-size: 12px;
  letter-spacing: 0.08em;
  color: var(--accent);
  font-weight: 600;
}
.hero-title {
  margin: 6px 0 0;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 0.01em;
  color: var(--ink);
  line-height: 1.3;
}
.hero-desc {
  margin: 8px 0 0;
  font-size: 13px;
  color: var(--ink-3);
}
.hero-action {
  flex-shrink: 0;
}
@media (max-width: 860px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }
}

.dash-grid {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 16px;
  align-items: start;
}
@media (max-width: 1080px) {
  .dash-grid {
    grid-template-columns: 1fr;
  }
}
.col-main,
.col-side {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

.block {
  padding: 18px 20px;
}
.block-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}
.block-title {
  font-size: 13.5px;
  font-weight: 650;
  color: var(--ink);
}
.block-sub {
  font-size: 11.5px;
  color: var(--ink-3);
  margin-top: 2px;
}
.block-progress {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: var(--ink-2);
}
.mini-bar {
  width: 90px;
  height: 6px;
  background: var(--surface-3);
  border-radius: 4px;
  overflow: hidden;
}
.mini-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), #d97706);
  border-radius: 4px;
  transition: width 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.task-list {
  display: flex;
  flex-direction: column;
}
.task-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 4px;
  border-bottom: 1px dashed var(--line);
}
.task-row:last-child {
  border-bottom: none;
}
.task-row.done .task-title {
  text-decoration: line-through;
  color: var(--ink-3);
}
.task-check {
  width: 20px;
  height: 20px;
  border-radius: 7px;
  border: 1.5px solid var(--line-strong);
  background: var(--surface);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.task-check:hover {
  border-color: var(--accent);
}
.task-check.checked {
  background: var(--ok);
  border-color: var(--ok);
}
.task-main {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}
.task-title {
  font-size: 13px;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.task-type {
  font-size: 10.5px;
  color: var(--accent-strong);
  background: var(--accent-soft);
  padding: 1px 7px;
  border-radius: 999px;
  flex-shrink: 0;
}
.task-done-at {
  font-size: 11px;
}
.task-empty {
  padding: 8px 0;
}

.todo-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.todo-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 14px;
  border: 1px solid var(--line);
  border-radius: 11px;
  background: var(--surface);
  font-family: inherit;
  text-align: left;
  cursor: pointer;
  transition: all 0.18s;
}
.todo-row:hover {
  border-color: var(--accent-line);
  background: var(--accent-soft);
}
.todo-main {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.todo-company {
  font-size: 13px;
  font-weight: 600;
  color: var(--ink);
}
.todo-pos {
  font-size: 12px;
  color: var(--ink-2);
}
.todo-city {
  font-size: 11px;
  color: var(--ink-3);
}
.todo-rev-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}
.todo-rev-icon.exam {
  background: var(--accent-soft);
  color: var(--accent-strong);
}
.todo-rev-icon.interview {
  background: var(--ok-soft);
  color: var(--ok);
}
.go-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11.5px;
  color: var(--accent-strong);
  flex-shrink: 0;
  font-weight: 550;
}
.q-tag {
  font-size: 10.5px;
  padding: 1px 7px;
  border-radius: 999px;
  background: var(--info-soft);
  color: var(--ink-2);
}
.q-tag.diff {
  background: var(--warn-soft);
  color: #7a5a12;
}
.mini-empty {
  font-size: 12.5px;
  padding: 10px 2px;
}

.streak-card {
  background: linear-gradient(180deg, #1f1d1a 0%, #2a2723 100%);
  color: #fff;
  border: none;
}
.streak-num {
  font-size: 42px;
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1;
}
.streak-num span {
  font-size: 16px;
  margin-left: 4px;
  color: #f59e0b;
  font-weight: 600;
}
.streak-label {
  margin-top: 4px;
  font-size: 12.5px;
  color: rgba(255, 255, 255, 0.55);
}
.week-progress {
  margin-top: 18px;
}
.week-line {
  height: 7px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 5px;
  overflow: hidden;
}
.week-fill {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
  border-radius: 5px;
  transition: width 0.5s;
}
.week-text {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
}
.week-text .muted {
  color: rgba(255, 255, 255, 0.45);
}
.streak-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.quick-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.quick-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 13px 8px;
  border: 1px solid var(--line);
  border-radius: 11px;
  background: var(--surface);
  color: var(--ink-2);
  font-size: 11.5px;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}
.quick-btn:hover {
  border-color: var(--accent-line);
  color: var(--accent-strong);
  background: var(--accent-soft);
}
.quick-btn .el-icon {
  font-size: 17px;
}
</style>