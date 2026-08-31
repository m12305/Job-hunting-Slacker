# API 接口契约文档

> 后端 FastAPI，REST 风格。基础路径 `/api`。响应统一封装。

---

## 1. 通用约定

### 1.1 响应结构

```json
{ "code": 0, "message": "ok", "data": {} }
```

- `code = 0`：成功；非 0：业务错误（配合 HTTP 状态码）。
- 错误响应：`{ "code": 40001, "message": "..." , "data": null }`。

### 1.2 分页

请求：`?page=1&page_size=20`

```json
{ "items": [], "total": 123, "page": 1, "page_size": 20 }
```

### 1.3 枚举清单（与数据库一致，供前端映射）

- 简历状态：`draft / active / archived`
- 投递渠道：`boss / nowcoder / official / referral / other`
- 投递状态：`pending / applied / resume_screening / resume_rejected / exam / interview / ended / offered / rejected`
- 面试轮次：`first / second / third / hr / final / other`
- 素材分类：`project / internship / campus / award / other`
- 资产分类：`blog / project / github / transcript / certificate / other`
- 题库分类：`code / baguwen / project_ask / other`
- 话术分类：`general / tech / custom`
- 黑名单类型：`overtime / fake_salary / free_trial / trap_interview / other`

---

## 2. 模块一接口

### 2.1 岗位类型

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/job-types` | 列表（含排序） |
| POST | `/api/job-types` | 新增 `{name, color?, sort_order?}` |
| PUT | `/api/job-types/{id}` | 修改 |
| DELETE | `/api/job-types/{id}` | 删除（有关联简历时返回 409，带提示） |

### 2.2 简历版本

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/resumes` | 列表，支持 `?job_type_id=&keyword=` |
| GET | `/api/resumes/{id}` | 详情（含修改日志） |
| POST | `/api/resumes` | 新增（元数据） |
| PUT | `/api/resumes/{id}` | 修改元数据 |
| DELETE | `/api/resumes/{id}` | 删除（含本地文件，可配置） |
| POST | `/api/resumes/{id}/upload` | 上传文件（multipart，`file` 字段） |
| POST | `/api/resumes/{id}/set-default` | 设为岗位默认版本 |
| GET | `/api/resumes/{id}/file` | 下载/预览文件（`?disposition=inline\|attachment`） |
| GET | `/api/resumes/{id}/preview` | 预览（PDF 直接返回；Word 转 PDF 后返回，带缓存） |

### 2.3 修改日志

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/resumes/{id}/logs` | 简历的修改日志（时间倒序） |
| POST | `/api/resume-logs` | 新增 `{resume_version_id, change_desc, changed_at?}` |

### 2.4 素材库

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/materials` | 列表，`?category=&keyword=&tag=` |
| POST | `/api/materials` | 新增 |
| PUT | `/api/materials/{id}` | 修改 |
| DELETE | `/api/materials/{id}` | 删除 |
| GET | `/api/materials/categories` | 素材分类（含自定义） |

### 2.5 资产归档

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/assets` | 列表，`?category=&keyword=` |
| POST | `/api/assets` | 新增（链接或文件） |
| PUT | `/api/assets/{id}` | 修改 |
| DELETE | `/api/assets/{id}` | 删除 |
| POST | `/api/assets/upload` | 上传文件并创建资产 |

---

## 3. 模块二接口

### 3.1 投递

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/applications` | 列表，`?status=&company=&position=&city=&channel=&job_type_id=&page=` |
| GET | `/api/applications/{id}` | 详情（含状态流水、关联笔试/面试/offer） |
| POST | `/api/applications` | 新增 |
| PUT | `/api/applications/{id}` | 修改 |
| DELETE | `/api/applications/{id}` | 删除 |
| PUT | `/api/applications/{id}/status` | 变更状态 `{to_status, note?}`（校验流转合法性） |
| GET | `/api/applications/{id}/timeline` | 状态流水 |

### 3.2 Offer

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/offers` | 列表 `?status=` |
| POST | `/api/offers` | 新增 `{application_id?, ...}` |
| PUT | `/api/offers/{id}` | 修改 |
| DELETE | `/api/offers/{id}` | 删除 |
| GET | `/api/offers/{id}` | 详情 |

### 3.3 Offer 对比

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/offers/compare` | 入参 `{offer_ids: [], weight_overrides?}`，返回各维度得分+总分+排序+最优推荐 |
| GET | `/api/offer-weight-config` | 读取权重配置 |
| PUT | `/api/offer-weight-config` | 更新权重配置（整体覆盖） |
| GET | `/api/settings` / `PUT /api/settings` | 全局设置（理想年薪区间等） |

**compare 返回示例：**

```json
{
  "results": [
    {
      "offer_id": 1,
      "company": "A公司",
      "scores": { "salary": 80, "city": 70, "work_intensity": 60, "...": 75 },
      "total": 72.5,
      "recommended": true,
      "rank": 1
    }
  ],
  "dimensions": [ { "key": "salary", "name": "薪资", "weight": 0.3 } ]
}
```

---

## 4. 模块三接口

### 4.1 笔试

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/exams` | 列表 `?application_id=&status=` |
| POST | `/api/exams` | 新增 |
| PUT | `/api/exams/{id}` | 修改 |
| DELETE | `/api/exams/{id}` | 删除 |
| GET | `/api/exams/{id}/review` | 读复盘 |
| PUT | `/api/exams/{id}/review` | 写复盘（upsert） |

### 4.2 面试

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/interviews` | 列表 `?application_id=&status=&round=` |
| POST | `/api/interviews` | 新增 |
| PUT | `/api/interviews/{id}` | 修改 |
| DELETE | `/api/interviews/{id}` | 删除 |
| GET | `/api/interviews/{id}/qa` | 问答复盘列表 |
| POST | `/api/interviews/{id}/qa` | 新增问答 |
| PUT | `/api/interview-qa/{id}` | 修改问答 |
| DELETE | `/api/interview-qa/{id}` | 删除问答 |
| GET | `/api/interviews/{id}/result` | 读结果 |
| PUT | `/api/interviews/{id}/result` | 写结果（含录音上传） |
| POST | `/api/interviews/{id}/audio` | 上传面试录音 |

### 4.3 题库

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/questions` | 列表 `?category=&difficulty=&review_status=&keyword=&tag=` |
| POST | `/api/questions` | 新增 |
| PUT | `/api/questions/{id}` | 修改 |
| DELETE | `/api/questions/{id}` | 删除 |
| PUT | `/api/questions/{id}/review-status` | 标记待刷/掌握 |

---

## 5. 模块四接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/stats/overview` | 总体 KPI（总数/有效/挂简历率/笔试通过率/面试率/offer率） |
| GET | `/api/stats/by-job-type` | 岗位维度统计（含各环节通过率） |
| GET | `/api/stats/by-time` | 时间维度统计 `?granularity=day\|week\|month&start=&end=` |

**overview 返回示例：**

```json
{
  "total_applications": 120,
  "effective_applications": 100,
  "resume_rejected_rate": 0.35,
  "exam_pass_rate": 0.6,
  "interview_rate": 0.3,
  "offer_rate": 0.08
}
```

---

## 6. 模块五接口

### 6.1 话术库

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/scripts` | 列表 `?category=&keyword=&favorite=1` |
| POST | `/api/scripts` | 新增 |
| PUT | `/api/scripts/{id}` | 修改 |
| DELETE | `/api/scripts/{id}` | 删除 |
| PUT | `/api/scripts/{id}/favorite` | 切换收藏 `{favorite: bool}` |

### 6.2 黑名单

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/blacklist` | 列表 `?company=&issue_type=` |
| POST | `/api/blacklist` | 新增 |
| PUT | `/api/blacklist/{id}` | 修改 |
| DELETE | `/api/blacklist/{id}` | 删除 |
| GET | `/api/blacklist/check?company=` | 查询某公司命中条数（投递时提示用） |

### 6.3 每日看板 & 任务

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/dashboard/today` | 今日聚合：待投递/待复盘/待刷题 + 打卡统计 |
| GET | `/api/tasks` | 任务列表 `?due_date=YYYY-MM-DD` |
| POST | `/api/tasks` | 新增任务 |
| PUT | `/api/tasks/{id}` | 修改 |
| DELETE | `/api/tasks/{id}` | 删除 |
| PUT | `/api/tasks/{id}/done` | 打卡 `{done: bool}` |
| GET | `/api/dashboard/streak` | 连续打卡天数、本周完成 |

---

## 7. 系统接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/export` | 导出全量 JSON 备份 |
| POST | `/api/import` | 导入（可选） |
| GET | `/docs` | FastAPI 自动文档 |

---

## 8. 错误码约定

| code | HTTP | 含义 |
|------|------|------|
| 0 | 200 | 成功 |
| 40000 | 400 | 参数校验失败 |
| 40400 | 404 | 资源不存在 |
| 40900 | 409 | 冲突（如删除有关联的岗位类型、非法状态流转） |
| 50000 | 500 | 服务器错误 |
