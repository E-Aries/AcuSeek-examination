# AXUS 企业考核系统

基于 Vue 3 + FastAPI 的全栈在线考试系统，支持题库管理、智能组卷、在线考试、自动阅卷与成绩统计。

---

## 功能概览

| 模块 | 功能 |
|---|---|
| 登录认证 | 账号密码登录，JWT 令牌鉴权，支持管理员/考生两种角色 |
| 仪表盘 | 考试概况、通过率统计、成绩分布图表（ECharts） |
| 题库管理 | 题目增删改查，支持单选/多选/判断题，按分类筛选 |
| 考试管理 | 创建考试、随机组卷 / 按分类比例组卷、设置时长和及格分 |
| 在线考试 | 计时答题、自动提交、答题卡导航 |
| 成绩管理 | 自动阅卷评分、成绩明细查看、试卷回看 |

## 技术栈

**前端**
- Vue 3（Composition API）
- Vite 8
- Element Plus 2
- ECharts 6 + vue-echarts
- Pinia（状态管理）
- Vue Router 4

**后端**
- Python 3.10+
- FastAPI
- SQLAlchemy 2.0 + SQLite
- Pydantic 2
- python-jose（JWT 认证）
- passlib + bcrypt（密码加密）

## 快速启动

### 1. 启动后端

\\\\\ash
cd backend
pip install -r requirements.txt
python main.py
\\\\
后端默认运行在 http://localhost:8000

API 文档访问 http://localhost:8000/docs（Swagger UI）

首次启动会自动创建 SQLite 数据库 \exam.db\ 并生成默认管理员账号。

### 2. 初始化数据（可选）

\\\\\ash
python seed.py
\\\\
该脚本会向数据库注入示例题目和考试数据，方便快速体验。

### 3. 启动前端

\\\\\ash
npm install
npm run dev
\\\\
前端默认运行在 http://localhost:5173

---

## 默认账号

启动后端并执行 \seed.py\ 后：

| 角色 | 用户名 | 密码 |
|---|---|---|
| 管理员 | \dmin\ | \dmin123\ |
| 考生 | \candidate\ | \candidate123\ |

（建议首次登录后修改密码）

## 项目结构

\\\\examination/
\u251c\u2500\u2500 backend/                  # FastAPI 后端
\u2502   \u251c\u2500\u2500 main.py               # 应用入口，路由注册
\u2502   \u251c\u2500\u2500 config.py             # 数据库、JWT 配置
\u2502   \u251c\u2500\u2500 database.py           # 数据库连接与会话
\u2502   \u251c\u2500\u2500 models.py             # SQLAlchemy 数据模型
\u2502   \u251c\u2500\u2500 schemas.py            # Pydantic 数据校验
\u2502   \u251c\u2500\u2500 seed.py               # 初始化示例数据
\u2502   \u251c\u2500\u2500 requirements.txt      # Python 依赖
\u2502   \u2514\u2500\u2500 routers/              # API 路由模块
\u2502       \u251c\u2500\u2500 auth.py           # 登录注册
\u2502       \u251c\u2500\u2500 questions.py      # 题库管理
\u2502       \u251c\u2500\u2500 exams.py          # 考试管理
\u2502       \u251c\u2500\u2500 answers.py        # 答题提交
\u2502       \u2514\u2500\u2500 results.py        # 成绩查询
\u251c\u2500\u2500 src/                      # Vue 3 前端
\u2502   \u251c\u2500\u2500 main.js               # 应用入口
\u2502   \u251c\u2500\u2500 App.vue               # 根组件
\u2502   \u251c\u2500\u2500 api.js                # Axios HTTP 封装
\u2502   \u251c\u2500\u2500 router/index.js       # 路由配置
\u2502   \u251c\u2500\u2500 stores/               # Pinia 状态管理
\u2502   \u251c\u2500\u2500 views/                # 页面视图
\u2502   \u2502   \u251c\u2500\u2500 Login.vue         # 登录页
\u2502   \u2502   \u251c\u2500\u2500 Dashboard.vue     # 仪表盘
\u2502   \u2502   \u251c\u2500\u2500 Questions.vue     # 题库管理
\u2502   \u2502   \u251c\u2500\u2500 Exams.vue         # 考试列表
\u2502   \u2502   \u251c\u2500\u2500 ExamDetail.vue    # 考试详情/配置
\u2502   \u2502   \u251c\u2500\u2500 TakeExam.vue      # 在线答题
\u2502   \u2502   \u251c\u2500\u2500 Results.vue       # 成绩列表
\u2502   \u2502   \u2514\u2500\u2500 ResultDetail.vue  # 成绩明细
\u2502   \u251c\u2500\u2500 components/           # 通用组件
\u2502   \u2514\u2500\u2500 styles/               # 全局样式
\u251c\u2500\u2500 index.html                # 入口 HTML
\u251c\u2500\u2500 vite.config.js            # Vite 配置
\u2514\u2500\u2500 package.json              # 前端依赖
\\\\
## 环境变量

在 \ackend/config.py\ 中可配置：

| 变量 | 说明 | 默认值 |
|---|---|---|
| \DATABASE_URL\ | 数据库连接地址 | \sqlite:///./exam.db\ |
| \SECRET_KEY\ | JWT 签名密钥 | 默认密钥（生产环境请修改） |
| \ALGORITHM\ | JWT 加密算法 | \HS256\ |
| \ACCESS_TOKEN_EXPIRE_MINUTES\ | 令牌有效期（分钟） | 80\ |

## 许可证

仅供内部使用。
