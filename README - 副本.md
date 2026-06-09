# AXUS 企业考核管理系统

> 基于 Vue 3 + FastAPI + SQLite 的企业在线考核管理系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Vue 3](https://img.shields.io/badge/Vue-3.5-4FC08D)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB)](https://python.org)
[![Node](https://img.shields.io/badge/Node-22+-339933)](https://nodejs.org)

---

## 目录

- [项目简介](#项目简介)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [功能特性](#功能特性)
- [系统架构](#系统架构)
- [数据库与系统兼容性](#数据库与系统兼容性)
- [如何贡献](#如何贡献)
- [许可证](#许可证)

---

## 项目简介

AXUS 是一套功能完整的企业在线考核管理系统，支持题库管理、智能组卷、在线考试、自动评分、手工批改、成绩分析等全流程功能。

适合企业内部培训考核、技能认证、模拟考试等场景。

**角色**
- **管理员** — 题库管理、考核创建、成绩查询、系统设置
- **考生** — 参加考试、查看成绩

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | Vue 3 + Vue Router |
| UI 组件库 | Element Plus |
| 构建工具 | Vite 6 |
| 图表 | ECharts (vue-echarts) |
| 后端框架 | FastAPI (Python 3.10+) |
| 数据库 | SQLite (SQLAlchemy ORM) |
| 开发环境 | Node.js 22+ / npm / pip |

---

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/your-username/axus-examination.git
cd axus-examination

# 2. 安装后端依赖
cd backend
pip install -r requirements.txt
cd ..

# 3. 安装前端依赖
npm install

# 4. 初始化数据库
python backend/seed.py

# 5. 启动服务
# 终端1 — 后端
cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 终端2 — 前端
npx vite --host
```

访问：
- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

**默认账户**：admin / admin123

---

## 功能特性

### 题库管理
- 五种题型：单选 / 多选 / 判断 / 填空 / 简答
- 每题设置分类、难度、分值与解析
- 批量导入导出、批量分类、批量删除
- 分类管理

### 考核管理
- 三种考核类型：正式 / 练习 / 模拟
- 智能组卷：按题型分布精确控制题目数量
- 自动生成试卷，支持重新组卷
- 题型分布与题目数量联动
- 指定考生名单（正式考核）
- 百分比及格线
- 补考与续考

### 考试答题
- 限时答题 + 自动计时
- 答题卡导航 + 跳至未答
- 切屏检测（超过限制自动交卷）
- 练习模式即时反馈
- 退出可续考或放弃

### 成绩分析
- 等级制评分：优秀 ≥95% / 良好 ≥80% / 通过 ≥60% / 未通过 <60%
- 成绩详情页：分数环、分类得分、每题对比、难度分析、分布图表
- 管理员成绩统览
- 逐题批改（简答题）
- 成绩导出 CSV

### 系统设置
- 品牌文字自定义
- Logo 上传（登录页 / 导航栏 / Favicon）
- 实时预览

---

## 系统架构

```
Frontend (Vue 3 + Element Plus)
    ↓ HTTP API
Backend (FastAPI)
    ↓ ORM
SQLite / PostgreSQL / MySQL
```

支持 3 层解耦架构，前端通过统一 API 与后端通信，后端通过 SQLAlchemy ORM 操作数据库。

---

## 数据库与系统兼容性

### 支持的操作系统

| 系统 | 状态 |
|------|------|
| Windows | ✅ 完全支持 |
| macOS   | ✅ 支持 |
| Linux   | ✅ 支持 |

所有平台通用：Python / Node.js / npm 三平台兼容，SQLite 数据库可直接跨平台拷贝。

### 支持的数据库

| 数据库 | 状态 | 切换方式 |
|--------|------|----------|
| SQLite      | ✅ 默认配置 | 零配置，开箱即用 |
| PostgreSQL  | ⚠️ 需配置 | 修改 config.py 中 DATABASE_URL |
| MySQL       | ⚠️ 需配置 | 修改 config.py 中 DATABASE_URL |
| SQL Server  | ⚠️ 需配置 | 修改 config.py 中 DATABASE_URL |

底层使用 SQLAlchemy ORM，切换数据库只需修改 `backend/config.py` 中的数据库连接串并安装对应驱动。

---

## 如何贡献

欢迎贡献代码！详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

提交 Issue 时请包含：问题描述、复现步骤、环境信息。

---

## 许可证

[MIT License](LICENSE)

Copyright (c) 2026 达咩