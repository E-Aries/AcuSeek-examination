# AXUS 企业考核系统

基于 Vue 3 + FastAPI 的全栈在线考试系统，支持题库管理、智能组卷、在线考试、自动阅卷与成绩统计。

---

## 快速启动

### 后端

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

首次启动自动创建 SQLite 数据库。

### 前端

```bash
npm install
npm run dev     # 开发模式（5173 端口）
npm run build   # 生产构建
```

---

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 考生 | 1234 | 1234 |

## 功能清单

### 已实现

| 模块 | 功能 | 说明 |
|------|------|------|
| 仪表盘 | 数据概览 | 考核概况、通过率、成绩分布图 |
| 题库管理 | 增删改查 | 单选/多选/判断题，按分类筛选 |
| 题库管理 | 批量操作 | 批量删除/导出CSV/改分类 |
| 题库管理 | 分类管理 | 创建/编辑/删除分类 |
| 题库管理 | 题目解析 | 每道题支持答案解析 |
| 考核管理 | 创建配置 | 时长、及格线、组卷策略 |
| 考核管理 | 组卷方式 | 随机抽题/按分类比例 |
| 考核管理 | 重新组卷 | 按配置重新生成 |
| 在线考试 | 正式考试 | 计时、切屏检测、自动提交 |
| 在线考试 | 模拟考试 | 同正式考试，不计入成绩 |
| 在线考试 | 练习模式 | 选完即反馈对错+解析，不限时 |
| 在线考试 | 答题卡导航 | 已答/未答/当前题跳转 |
| 成绩管理 | 自动阅卷 | 客观题自动评分 |
| 成绩管理 | 成绩列表 | 按考核分组 |
| 成绩管理 | 成绩详情 | 每题得分明细 |
| 试卷批改 | 逐题批改 | 手动批改 |
| 用户管理 | 增删改查 | 管理者管理 |
| 用户管理 | 个人资料 | 姓名/部门/密码修改 |
| 系统设置 | 通用配置 | 名称/及格线/切屏/时长 |
| 通知中心 | 系统通知 | 铃铛+未读数+列表 |
| 操作日志 | 审计记录 | 分页+筛选 |

### 待实现

| 优先级 | 功能 | 说明 |
|--------|------|------|
| ★★★ | 补考机制 | 未通过的考生允许重新考试 |
| ★★ | 每题对比 | 成绩详情页每题显示你的答案 vs 正确答案 |
| ★ | 导入结果反馈 | 批量导入题库时显示失败的行号和原因 |

## 技术栈

前端: Vue 3 + Vite 8 + Element Plus 2 + ECharts 6
后端: Python 3.10+ + FastAPI + SQLAlchemy 2.0 + SQLite
认证: JWT

## 项目结构

`
examination/
├── backend/                  # FastAPI 后端
│   ├── main.py               # 应用入口
│   ├── config.py             # 配置
│   ├── database.py           # 数据库连接
│   ├── models.py             # 数据模型
│   ├── schemas.py            # 数据校验
│   ├── exam.db               # SQLite 数据库
│   └── routers/              # API 路由
│       ├── auth.py / questions.py / exams.py
│       ├── answers.py / results.py / users.py
│       ├── dashboard.py / categories.py
│       ├── settings.py / logs.py / notifications.py
├── src/                      # Vue 3 前端
│   ├── main.js / App.vue / api.js
│   ├── router/index.js
│   ├── views/                # 13 个页面视图
│   └── components/AppLayout.vue
├── index.html
├── vite.config.js
├── package.json
└── README.md
`

## 数据库（8 个业务表）

| 表名 | 用途 | 关键字段 |
|------|------|----------|
| users | 用户 | username, name, role, department |
| questions | 题目 | type, category, content, options, answer, explanation, score |
| categories | 分类 | name, sort |
| exams | 考核 | name, type, duration, question_count, pass_score, strategy |
| exam_papers | 答卷 | exam_id, user_id, questions, answers, score, status |
| system_settings | 设置 | key, value |
| operation_logs | 日志 | username, action, target, detail, ip |
| notifications | 通知 | title, content, type, is_read |

## 注意事项

- 数据库文件 backend/exam.db（非根目录 exam.db）
- 练习模式选完即反馈，不限时无切屏
- 管理员用户名不可修改
- 批量导出 CSV 使用 fetch 直接请求
