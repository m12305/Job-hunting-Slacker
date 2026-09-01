# 秋招辅助管理软件 — 后端（backend）

> 依据《docs/》下 PRD / 数据库设计 / API 接口契约 / 技术架构与设计 实现。
> 技术栈：**FastAPI + SQLAlchemy 2.x + Pydantic v2 + SQLite + Alembic**，分层 API → Service → ORM。

---

## 1. 目录结构

```
backend/
├── app/
│   ├── main.py            # FastAPI 入口（CORS/异常处理/启动建表种子）
│   ├── config.py          # 配置（数据目录、CORS、上传上限）
│   ├── database.py        # Engine / Session / get_db / 目录初始化
│   ├── core/              # 常量（枚举+状态机）、统一响应、业务异常
│   ├── models/            # SQLAlchemy 模型（M1~M5 全部 19 张业务表）
│   ├── schemas/           # Pydantic 请求/响应模型
│   ├── crud/              # 通用数据访问（get_or_404）
│   ├── services/          # 业务逻辑：文件存储、状态机、Offer 打分、统计、种子
│   └── api/               # 路由（按模块组织，统一 /api 前缀）
├── alembic/               # 数据库迁移（versions/ 含初始迁移）
├── alembic.ini
├── data/                  # 运行时生成：app.db + files/（resumes/certificates/assets/audios/cache）
├── scripts/smoke_test.py  # 全接口冒烟测试（需服务已启动）
└── requirements.txt
```

## 2. 环境与启动

```bash
# 1) 安装依赖
pip install -r requirements.txt

# 2) 初始化数据库（首建表）
cd backend
alembic upgrade head

# 3) 启动服务（首次启动自动写入种子数据：岗位类型/权重/话术模板/默认设置）
uvicorn app.main:app --reload --port 8000

# 浏览器打开
#   API 文档：http://127.0.0.1:8000/docs
#   健康检查：http://127.0.0.1:8000/api/health
```

> 本机已采用 conda 环境：`D:\DL\anaconda3\envs\agent\python.exe`

种子数据（幂等，仅空表时写入）：

- 岗位类型：算法岗 / 开发岗 / 测试岗 / 产品岗
- Offer 打分权重：薪资/城市/加班强度/行业前景/公司规模/岗位发展（等权）
- 话术模板：自我介绍 / 优缺点 / 职业规划 / 为什么选择我们
- 设置：`salary_ideal_range=[240,800]`（年薪理想区间 K）、`preferred_cities=[]`

## 3. 接口总览（前缀 `/api`，统一响应 `{code, message, data}`）

| 模块 | 资源 | 主要端点 |
|------|------|----------|
| 一 | 岗位类型 | `GET/POST/PUT/DELETE /job-types`（删除有简历关联→409） |
| 一 | 简历版本 | `/resumes` CRUD、`POST /{id}/upload`、`/set-default`、`/file?disposition=`、`/preview` |
| 一 | 修改日志 | `GET /resumes/{id}/logs`、`POST /resume-logs` |
| 一 | 素材库 | `/materials` CRUD、`GET /materials/categories` |
| 一 | 资产归档 | `/assets` CRUD、`POST /assets/upload` |
| 二 | 投递 | `/applications` CRUD（筛选+分页）、`PUT /{id}/status`（状态机）、`GET /{id}/timeline`、详情含流水/笔试/面试/offer/黑名单提示 |
| 二 | Offer | `/offers` CRUD、`POST /offers/compare`（打分+排序+最优推荐）、`GET/PUT /offer-weight-config` |
| 三 | 笔试 | `/exams` CRUD、`GET/PUT /{id}/review`（复盘 upsert） |
| 三 | 面试 | `/interviews` CRUD、`GET/POST /{id}/qa`、`PUT/DELETE /interview-qa/{id}`、`GET/PUT /{id}/result`、`POST /{id}/audio` |
| 三 | 题库 | `/questions` CRUD、`PUT /{id}/review-status` |
| 四 | 统计 | `GET /stats/overview`、`/stats/by-job-type`、`/stats/by-time?granularity=day|week|month` |
| 五 | 话术库 | `/scripts` CRUD、`PUT /{id}/favorite`、`POST /{id}/use` |
| 五 | 黑名单 | `/blacklist` CRUD、`GET /blacklist/check?company=`（投递提示） |
| 五 | 任务/看板 | `/tasks` CRUD、`PUT /{id}/done`、`GET /dashboard/today`、`GET /dashboard/streak` |
| 系统 | 通用 | `GET /health`、`GET /settings`、`PUT /settings`（理想年薪区间等）、`GET /export`、`POST /import`（JSON 全量备份/恢复） |

错误码：`40000` 参数校验、`40400` 不存在、`40900` 冲突（关联删除/非法状态流转）、`50000` 服务器错误。

## 4. 核心业务说明

- **投递状态机**（`app/core/constants.py` 的 `STATUS_TRANSITIONS`）：

  ```
  pending → applied / ended
  applied → resume_screening / resume_rejected / exam / interview / ended
  resume_screening → resume_rejected / exam / interview / ended
  resume_rejected → ended
  exam → interview / ended
  interview → ended / offered / rejected
  ended → offered
  offered → rejected
  rejected →（终态）
  ```
  每次变更写入 `application_status_logs` 流水；非法流转返回 409。

- **Offer 打分**（`app/services/offer_service.py`）：

  - 薪资维度：年薪 = base×月数 + 绩效奖金 + 签字费，按「理想年薪区间」线性映射 0-100
  - 城市：命中 `preferred_cities` 100 分，否则 60 分
  - 加班强度反向映射、主观分 1-5 → ×20、公司规模文本粗粒度映射
  - 总分 = Σ(得分×权重)/Σ(权重)，权重默认等权、可整体覆盖配置、对比时可临时覆盖
  - 自定义维度：Offer 的 `extra_scores` JSON（key → 0-100 分）+ 权重配置中的 `custom_*` 维度

- **统计口径**（`app/services/stats_service.py`）：有效投递 = 非 pending；进入笔试/面试 = 状态流水为准（无流水时按当前状态近似）；笔试通过率 = 已复盘（passed 有值）中通过占比；Offer 率 = offer 数/有效投递。

- **文件存储**：上传落盘 `data/files/{分类}/{uuid}.{ext}`，数据库存相对路径；简历 PDF 直接内嵌预览，Word 需 LibreOffice（`soffice --headless`）转 PDF 并缓存，环境缺失时接口返回 409 提示前端降级为下载。

## 5. 与设计文档的少量实现偏差

1. `interview_results.result` 改为可空：允许先传录音、后补「通过/挂掉」结果。
2. `offers.extra_scores` 附加 JSON 列：承载自定义打分维度数据。
3. 时间统一存本地时间（设计文档建议的选项之二）。

## 6. 测试

```bash
# 先启动服务，再执行（环境变量 PYTHONIOENCODING=utf-8 避免控制台乱码）
python scripts/smoke_test.py
```

冒烟测试覆盖五大模块全部端点、状态机合法/非法流转、Offer 对比、导出→导入回环、文件上传下载预览。