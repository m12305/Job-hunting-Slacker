# 求职摆烂管理局 · 前端（fronted）

依据 `docs/` 下 PRD / 数据库设计 / API 接口契约 / 技术架构与设计 实现的秋招辅助管理软件前端。

> 技术栈：**Vue 3（组合式 API）+ Vite + TypeScript + Element Plus + Pinia + Vue Router + ECharts + Axios**
> 与后端 `backend/`（FastAPI，端口 8000）前后端分离联调。
> 曾用名「秋招室」，现已改版为趣味卡通风格「求职摆烂管理局」（原创线条小狗吉祥物，非版权角色）。

---

## 1. 快速开始

```bash
cd fronted
npm install          # 安装依赖
npm run dev          # 启动开发服务器：http://127.0.0.1:5173
```

- 开发服务器已配置 `/api` 代理到 `http://127.0.0.1:8000`（见 `vite.config.ts`）。
- 生产构建：`npm run build`（产物在 `dist/`，含 vue-tsc 类型检查）。

> 前置条件：后端已启动（`uvicorn app.main:app --reload --port 8000`）。

---

## 2. 页面与模块（对应 PRD 五大模块）

| 路由 | 页面 | 模块 | 覆盖功能 |
|------|------|------|----------|
| `/dashboard` | 今日看板 | 五 | 待投递 / 待复盘 / 待刷题聚合、任务打卡、连续打卡、快捷入口、小狗局长批示台词 |
| `/stats` | 数据看板 | 四 | 六大 KPI（总投递/有效/挂简历率/笔试通过率/面试率/Offer率）、岗位维度柱+线图、投递节奏（日/周/月） |
| `/resumes` | 简历版本 | 一 | 岗位类型分组、多版本 CRUD、PDF/Word 预览抽屉、修改日志时间线、上传/设默认/下载 |
| `/materials` | 素材库 | 一 | STAR 结构素材、分类/关键词/标签筛选、技术栈标签 |
| `/assets` | 资产归档 | 一 | 链接类一键跳转、文件类上传归档、分类筛选 |
| `/applications` | 投递管理 | 二 | 搜索筛选分页、状态机流转（合法去向下拉 + 备注）、状态时间线、详情抽屉联动笔面试/Offer、投递时黑名单命中提示 |
| `/offers` | Offer 管理 | 二 | Offer 全字段 CRUD、年薪折算展示、关联投递 |
| `/offers/compare` | Offer 对比 | 二 | 多 Offer 勾选、权重滑杆临时调整、打分排序 + 最优推荐、雷达图、权重保存为全局配置 |
| `/exams` | 笔试管理 | 三 | 笔试信息（时间/平台/链接/账号密码遮蔽）、写复盘（通过/题目/错题/考点/总结） |
| `/interviews` | 面试管理 | 三 | 按投递聚合的多轮面试时间线、准备清单、问答复盘抽屉、面试结果 + 录音上传 |
| `/questions` | 题库 | 三 | 分类/难度/掌握状态筛选、题目展开查看答案、待刷/已掌握标记 |
| `/scripts` | 话术库 | 五 | 分类/收藏/搜索、一键复制（计入使用次数） |
| `/blacklist` | 避雷库 | 五 | 公司搜索 + 类型筛选，投递录入时联动提示 |
| `/appearance` | 外观设置 | — | 7 套主题配色一键切换、上传背景壁纸（自动压缩后本地持久化）、壁纸透明度调节、恢复默认 |
| `/settings` | 设置 | 二/五 | 理想年薪区间、首选城市、打分权重配置、JSON 导出/导入备份 |

跨页联动：投递详情「笔试/面试」按钮 → 带 `application_id` 跳转新建；看板「去复盘」→ 深链打开复盘/结果弹窗。

---

## 3. 目录结构

```
fronted/
├── index.html                 # 入口 HTML（字体、favicon）
├── vite.config.ts             # 别名 / 代理 / 分包
├── tsconfig.json
└── src/
    ├── main.ts                # 挂载 Element Plus(zh-cn) + 全量图标注册
    ├── App.vue
    ├── styles/
    │   ├── tokens.css         # 设计令牌（色板 / 圆角 / 阴影 / Element Plus 主题变量）
    │   └── index.css          # 全局样式与组件微调
    ├── api/                   # Axios 封装 + 按模块组织的接口
    │   ├── http.ts            # 统一响应解包 / 错误提示 / 上传 / 下载
    │   ├── module1.ts ~ module5.ts
    │   └── index.ts           # 统一出口
    ├── types/index.ts         # 与后端 schema 一一对应的领域类型
    ├── constants/index.ts     # 枚举 → 中文/色板映射、投递状态机
    ├── utils/                 # 日期/数字/文件格式化、下载
    ├── stores/dict.ts         # 岗位类型 / 素材分类共享字典
    ├── composables/useEcharts.ts  # 图表封装（自适应 + 卸载释放）
    ├── router/index.ts
    ├── layouts/MainLayout.vue # 侧边栏 + 顶栏外壳
    ├── components/            # PageHeader / StatusTag / EmptyState / KpiCard / CountUp / TagInput
    └── views/                 # 按模块组织的页面
```

---

## 4. 设计说明

- **设计方向「趣味卡通」**：暖纸底 + 墨色文字，强调色由单一 `--accent` 变量派生（`color-mix`），可一键换肤。
- **主题风格**（`/appearance`，持久化 localStorage）：
  - **原始主题**：清爽克制的经典界面，无吉祥物与涂鸦；
  - **线条小狗**：网上流行的形象风格（大头 + 长垂耳 + ω 嘴），深色粗描边白色填充，贯穿侧边栏 / 空状态 / 看板；
  - **蜡笔小新**：原创 Q 版参考形象（蘑菇头 + 标志性粗眉毛 + 红 T 恤 + 黄短裤），侧边栏有眉毛小涂鸦；
  - 顶栏「调色盘」按钮可随时切换主题风格与配色。
- **界面配色**：8 个预设色板（秋柿橙 / 抹茶绿 / 桃子汽水 / 黄油曲奇 / 雪山青 / 葡萄果冻 / 番茄锅底 / 小新红）+ **自定义色板**（`el-color-picker` 选色后应用即生效），柔和色自动派生。
- **背景壁纸**：上传图片自动压缩（最长边 ≤1920px、JPEG 82% 质量）后存入本机；壁纸透明度滑杆可调，启用后主要面板自动切换为毛玻璃半透明。
- **响应式**：768px 以下侧边栏折叠为图标栏，页面内容单列。
- **完整交互状态**：骨架屏加载、主题吉祥物空态引导、错误内联提示、`:active` 触感、卡片 hover 微抬升、数字滚动动画。
- **状态机前端同步**：`constants/STATUS_TRANSITIONS` 与后端 `core/constants.py` 保持一致，非法流转在 UI 层即被禁用。
- **深链约定**：`/applications?focus=id`、`/exams?focus=id&new=1&application_id=x` 等，支撑跨页联动。

---

## 5. 已知边界

- 资产文件类条目：后端未提供公网下载端点，前端仅展示本地归档文件名。
- Word 简历预览依赖后端 LibreOffice 转换，环境缺失时前端优雅降级为「下载查看」。
- 账号密码为本地明文存储（个人使用），预览界面默认遮蔽、可手动揭示。