# AXUS 考核系统 — 项目总结

## 项目概览
Vue 3 + FastAPI + SQLite 在线考试系统。路径: D:\codex\examination。后端 8000 端口，前端 Vite 5173 端口。

## 当前最新备份
D:\examination_backup_20260608_121537（还原点）

## 功能清单（已实现）
- 用户管理（超级管理员/管理员/考生三级权限）
- 题库管理（单选/多选/判断/填空/简答，CRUD + 导入导出 + 批量操作）
- 分类管理
- 考核管理（正式考试/模拟考试/练习模式）
- 组卷方式（手动/随机）
- 考试/练习界面（答题卡、切屏检测、计时）
- 交卷评分（简答人工评分）
- 成绩查询 / 成绩详情（每题对错对比）
- 仪表盘统计（ECharts）
- 操作日志 / 系统日志
- 系统设置/OEM品牌定制（Logo上传、名称、版权、版本号）
- 个人资料/修改密码
- 通知中心
- 补考机制
- 批量导出CSV

## 数据库字段要点
- Exam.type: "正式考试" / "模拟考试" / "练习"（注意是"模拟"不是"模拟考试"）
- Exam.status: "未开始" / "进行中" / "已结束"
- ExamPaper.status: "进行中" / "待批改" / "已完成"
- User.role: "admin" / "candidate"

## 操作须知
- 文件写入用 Set-Content + Python 脚本，不用 PowerShell 直接处理中文
- 重启后端后代码才生效（修改完后端要重启）
- 改完运行 npx vite build 验证编译
- 备份路径 D:\examination_backup_yyyyMMdd_HHmmss

## 已知问题/待办
- 8000端口可能有僵尸进程，Start-Process 会报 Access Denied，建议用 cmd /c 方式启动
- Python 3.14 + uvicorn 启动有兼容问题，前台启动正常但后台启动可能立即退出

## 最近丢失的改动（需重新加）
1. Categories.vue / Users.vue 操作列改为紧凑图标按钮
2. Questions.vue 预览按钮移到题目列
3. answers.py 模拟考试简答自动评分
4. exams.py + TakeExam.vue 模拟考试交卷修复（UPDATE而非DELETE）
5. answers.py 多选题评分 fix（split而非eval）+ "模拟考试"→"模拟"
