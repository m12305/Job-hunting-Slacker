<template>
  <div class="page">
    <PageHeader
      kicker="MODULE 02 · Offer 决策"
      title="Offer 管理"
      desc="维护收到的 Offer 明细（薪资、奖金、股票、加班强度…），用可配置权重打分对比。"
    >
      <template #actions>
        <el-button @click="router.push('/offers/compare')"><el-icon><DataAnalysis /></el-icon>&nbsp;对比决策</el-button>
        <el-button type="primary" @click="openCreate"><el-icon><Plus /></el-icon>&nbsp;新增 Offer</el-button>
      </template>
    </PageHeader>

    <div class="filter-row">
      <button class="chip" :class="{ active: filterStatus === '' }" @click="filterStatus = ''; load()">
        全部 <span class="mono">{{ items.length }}</span>
      </button>
      <button
        v-for="(v, k) in OFFER_STATUS"
        :key="k"
        class="chip"
        :class="{ active: filterStatus === k }"
        @click="filterStatus = k; load()"
      >
        <span class="dot" :style="{ background: v.dot }" />{{ v.label }}
      </button>
    </div>

    <el-skeleton v-if="loading" :rows="5" animated class="panel" style="padding: 20px" />
    <EmptyState
      v-else-if="!items.length"
      icon="Medal"
      title="还没有 Offer"
      desc="拿到 Offer 后录入薪资与各项打分，去「对比决策」生成量化推荐。"
    >
      <template #action>
        <el-button type="primary" @click="openCreate">录入 Offer</el-button>
      </template>
    </EmptyState>

    <div v-else class="grid">
      <article v-for="o in items" :key="o.id" class="offer panel card-hover">
        <div class="o-top">
          <div class="o-company">
            <h3>{{ o.company }}</h3>
            <span v-if="o.position" class="o-pos">{{ o.position }}</span>
            <span v-if="o.city" class="o-city"><el-icon><Location /></el-icon>{{ o.city }}</span>
          </div>
          <StatusTag :dict="OFFER_STATUS" :value="o.status" />
        </div>

        <div class="o-salary">
          <template v-if="o.salary_base != null">
            <span class="mono base">{{ o.salary_base }}K</span>
            <span class="times">× {{ o.salary_months || 12 }} 薪</span>
            <span class="mono annual">≈ {{ annual }}K/年</span>
          </template>
          <span v-else class="muted">未填写薪资</span>
        </div>

        <div class="o-scores">
          <span v-if="o.work_intensity != null" class="score">
            加班 <b>{{ o.work_intensity }}</b>/5
          </span>
          <span v-if="o.industry_prospect != null" class="score">
            行业 <b>{{ o.industry_prospect }}</b>/5
          </span>
          <span v-if="o.position_development != null" class="score">
            发展 <b>{{ o.position_development }}</b>/5
          </span>
          <span v-if="o.company_scale" class="score">{{ o.company_scale }}</span>
        </div>

        <div v-if="o.housing_fund || o.stock_options" class="o-extra">
          <span v-if="o.housing_fund" class="extra-line">公积金：{{ o.housing_fund }}</span>
          <span v-if="o.stock_options" class="extra-line">期权：{{ o.stock_options }}</span>
        </div>

        <div v-if="o.other_notes" class="o-notes">{{ o.other_notes }}</div>

        <div class="o-foot">
          <span class="mono muted-sm">{{ fmtDate(o.updated_at) }} 更新</span>
          <div class="oops">
            <button class="op" @click="openEdit(o)"><el-icon><Edit /></el-icon></button>
            <button class="op danger" @click="remove(o)"><el-icon><Delete /></el-icon></button>
          </div>
        </div>
      </article>
    </div>

    <!-- 表单 -->
    <el-dialog
      v-model="formVisible"
      :title="editing ? '编辑 Offer' : '新增 Offer'"
      width="720px"
      destroy-on-close
      top="4vh"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <div class="f-grid">
          <el-form-item label="公司" prop="company">
            <el-input v-model="form.company" />
          </el-form-item>
          <el-form-item label="岗位">
            <el-input v-model="form.position" />
          </el-form-item>
          <el-form-item label="城市">
            <el-input v-model="form.city" />
          </el-form-item>
          <el-form-item label="关联投递">
            <el-select v-model="form.application_id" clearable filterable style="width: 100%" placeholder="可选">
              <el-option
                v-for="a in appOptions"
                :key="a.id"
                :label="`${a.company} · ${a.position}`"
                :value="a.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="月 base（K）">
            <el-input-number v-model="form.salary_base" :min="0" :max="999" style="width: 100%" />
          </el-form-item>
          <el-form-item label="发放月数">
            <el-input-number v-model="form.salary_months" :min="1" :max="24" style="width: 100%" />
          </el-form-item>
          <el-form-item label="绩效奖金（K）">
            <el-input-number v-model="form.bonus_performance" :min="0" :max="999" style="width: 100%" />
          </el-form-item>
          <el-form-item label="签字费（K）">
            <el-input-number v-model="form.signing_bonus" :min="0" :max="999" style="width: 100%" />
          </el-form-item>
          <el-form-item label="公积金比例 / 基数">
            <el-input v-model="form.housing_fund" placeholder="如 双边 12%，基数 20K" />
          </el-form-item>
          <el-form-item label="股票 / 期权">
            <el-input v-model="form.stock_options" placeholder="如 4年 10万股 RSU" />
          </el-form-item>
          <el-form-item label="公司规模">
            <el-input v-model="form.company_scale" placeholder="如 1000-5000人 / 上市公司" />
          </el-form-item>
          <el-form-item label="Offer 状态">
            <el-select v-model="form.status" style="width: 100%">
              <el-option v-for="(v, k) in OFFER_STATUS" :key="k" :label="v.label" :value="k" />
            </el-select>
          </el-form-item>
        </div>

        <div class="f-grid three">
          <el-form-item label="加班强度（1 清闲 — 5 很卷）">
            <el-rate v-model="form.work_intensity" :max="5" show-score score-template="{value} 分" />
          </el-form-item>
          <el-form-item label="行业前景（1-5）">
            <el-rate v-model="form.industry_prospect" :max="5" show-score score-template="{value} 分" />
          </el-form-item>
          <el-form-item label="岗位发展（1-5）">
            <el-rate v-model="form.position_development" :max="5" show-score score-template="{value} 分" />
          </el-form-item>
        </div>

        <el-form-item label="其他备注">
          <el-input v-model="form.other_notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import { createOffer, deleteOffer, listApplications, listOffers, updateOffer } from '@/api'
import type { Application, Offer } from '@/types'
import { OFFER_STATUS, labelOf } from '@/constants'
import { annualSalary, fmtDate } from '@/utils/format'

const router = useRouter()
const items = ref<Offer[]>([])
const loading = ref(false)
const filterStatus = ref('')

const appOptions = ref<Application[]>([])

async function load() {
  loading.value = true
  try {
    items.value = await listOffers({ status: filterStatus.value || undefined })
  } finally {
    loading.value = false
  }
}

const annual = (o: Offer) => {
  const v = annualSalary(o)
  return v == null ? '—' : String(Math.round(v))
}

/* ---- 表单 ---- */
const formVisible = ref(false)
const editing = ref<Offer | null>(null)
const saving = ref(false)
const formRef = ref<FormInstance>()
const form = reactive<Record<string, unknown>>({
  application_id: null,
  company: '',
  position: '',
  city: '',
  salary_base: null,
  salary_months: null,
  bonus_performance: null,
  signing_bonus: null,
  housing_fund: '',
  stock_options: '',
  work_intensity: null,
  industry_prospect: null,
  company_scale: '',
  position_development: null,
  other_notes: '',
  status: 'pending',
})
const rules: FormRules = {
  company: [{ required: true, message: '请填写公司', trigger: 'blur' }],
}

function openCreate() {
  editing.value = null
  Object.assign(form, {
    application_id: null,
    company: '',
    position: '',
    city: '',
    salary_base: null,
    salary_months: null,
    bonus_performance: null,
    signing_bonus: null,
    housing_fund: '',
    stock_options: '',
    work_intensity: null,
    industry_prospect: null,
    company_scale: '',
    position_development: null,
    other_notes: '',
    status: 'pending',
  })
  formVisible.value = true
}
function openEdit(o: Offer) {
  editing.value = o
  Object.assign(form, {
    application_id: o.application_id,
    company: o.company,
    position: o.position ?? '',
    city: o.city ?? '',
    salary_base: o.salary_base,
    salary_months: o.salary_months,
    bonus_performance: o.bonus_performance,
    signing_bonus: o.signing_bonus,
    housing_fund: o.housing_fund ?? '',
    stock_options: o.stock_options ?? '',
    work_intensity: o.work_intensity,
    industry_prospect: o.industry_prospect,
    company_scale: o.company_scale ?? '',
    position_development: o.position_development,
    other_notes: o.other_notes ?? '',
    status: o.status,
  })
  formVisible.value = true
}
async function save() {
  await formRef.value?.validate()
  saving.value = true
  try {
    if (editing.value) await updateOffer(editing.value.id, form)
    else await createOffer(form)
    ElMessage.success('已保存')
    formVisible.value = false
    load()
  } catch {
    /* 拦截器提示 */
  } finally {
    saving.value = false
  }
}
async function remove(o: Offer) {
  await ElMessageBox.confirm(`确定删除「${o.company}」的 Offer 记录？`, '删除 Offer', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteOffer(o.id)
  ElMessage.success('已删除')
  load()
}

onMounted(async () => {
  load()
  try {
    const apps = await listApplications({ page_size: 100 })
    appOptions.value = apps.items
  } catch {
    /* 忽略 */
  }
})
</script>

<style scoped>
.filter-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 18px;
}
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 13px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--surface);
  color: var(--ink-2);
  font-size: 12.5px;
  font-family: inherit;
  cursor: pointer;
}
.chip.active {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: var(--accent-strong);
  font-weight: 600;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
  gap: 14px;
}
.offer {
  padding: 18px;
  display: flex;
  flex-direction: column;
}
.o-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}
.o-company h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.o-pos {
  display: block;
  font-size: 12.5px;
  color: var(--ink-2);
  margin-top: 1px;
}
.o-city {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11.5px;
  color: var(--ink-3);
  margin-top: 2px;
}
.o-salary {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-top: 14px;
  background: var(--surface-2);
  border-radius: 10px;
  padding: 10px 12px;
}
.base {
  font-size: 19px;
  font-weight: 650;
  color: var(--ink);
}
.times {
  font-size: 12px;
  color: var(--ink-2);
}
.annual {
  margin-left: auto;
  font-size: 12.5px;
  color: var(--accent-strong);
  font-weight: 600;
}
.o-scores {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}
.score {
  font-size: 11.5px;
  color: var(--ink-2);
  background: var(--bg-soft);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 2px 8px;
}
.score b {
  font-family: var(--font-mono);
}
.o-extra {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin-top: 10px;
  font-size: 12px;
  color: var(--ink-2);
}
.o-notes {
  margin-top: 10px;
  font-size: 12px;
  color: var(--ink-3);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.o-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px dashed var(--line);
  margin-top: 14px;
}
.muted-sm {
  font-size: 11.5px;
  color: var(--ink-3);
}
.oops {
  display: flex;
  gap: 2px;
}
.op {
  width: 27px;
  height: 27px;
  border: none;
  background: transparent;
  border-radius: 7px;
  color: var(--ink-3);
  cursor: pointer;
}
.op:hover {
  color: var(--accent-strong);
  background: var(--accent-soft);
}
.op.danger:hover {
  color: var(--danger);
  background: var(--danger-soft);
}

.f-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 14px;
}
.f-grid.three {
  grid-template-columns: repeat(3, 1fr);
}
@media (max-width: 640px) {
  .f-grid,
  .f-grid.three {
    grid-template-columns: 1fr;
  }
}
</style>