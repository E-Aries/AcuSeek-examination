# 数据库配置与初始化

AcuSeek 企业考核管理系统默认使用 **SQLite**（零配置），也支持 **MySQL / MariaDB / PostgreSQL**。

---

## 快速切换

```bash
# SQLite（默认，不设环境变量）
python backend/seed.py

# MySQL
DATABASE_URL="mysql+pymysql://root:密码@localhost/acuseek" python backend/seed.py

# PostgreSQL
DATABASE_URL="postgresql://postgres:密码@localhost/acuseek" python backend/seed.py
```

> 也可以直接修改 `backend/config.py` 中的 `DATABASE_URL`，效果相同。

---

## SQLite（默认）

**无需安装任何软件。** 跑完 seed.py 后 `backend/exam.db` 即数据库文件。

```bash
python backend/seed.py
```

---

## MySQL / MariaDB

### 前置条件

- MySQL 8.0+ 或 MariaDB 10.5+
- Python 驱动

```bash
pip install pymysql
```

### 建库

```sql
CREATE DATABASE acuseek CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 初始化

```bash
DATABASE_URL="mysql+pymysql://root:密码@localhost:3306/acuseek?charset=utf8mb4" python backend/seed.py
```

### 连接串格式

```
mysql+pymysql://用户名:密码@主机:端口/库名?charset=utf8mb4
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `用户名` | 数据库用户 | `root` |
| `密码` | 对应用户密码 | — |
| `主机` | 数据库地址 | `localhost` |
| `端口` | 默认 3306 | `3306` |
| `库名` | 数据库名 | `acuseek` |

---

## PostgreSQL

### 前置条件

- PostgreSQL 14+
- Python 驱动

```bash
pip install psycopg2-binary
```

### 建库

```bash
psql -U postgres -c "CREATE DATABASE acuseek;"
```

### 初始化

```bash
DATABASE_URL="postgresql://postgres:密码@localhost:5432/acuseek" python backend/seed.py
```

### 连接串格式

```
postgresql://用户名:密码@主机:端口/库名
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `用户名` | 数据库用户 | `postgres` |
| `密码` | 对应用户密码 | — |
| `主机` | 数据库地址 | `localhost` |
| `端口` | 默认 5432 | `5432` |
| `库名` | 数据库名 | `acuseek` |

---

## seed.py 做了什么

```bash
python backend/seed.py
```

1. **建表** — 自动创建 `users`、`questions`、`categories`、`exams`、`exam_papers`、`operation_logs`、`system_settings`、`notifications` 共 8 张表
2. **插数据** — 写入初始用户、示例题目和分类

| 账号 | 密码 | 角色 |
|------|------|------|
| `admin` | `admin123` | 管理员 |
| `zhangsan` | `123456` | 考生 |
| `lisi` | `123456` | 考生 |

---

## 常见问题

### 建库失败 `Access denied`

```bash
# 确认 MySQL 允许密码登录
mysql -u root -p

# 如不允许多次重试，用 root 直接创建
mysql -u root -p -e "CREATE DATABASE acuseek CHARACTER SET utf8mb4;"
```

### 连接报错 `authentication plugin`

MySQL 8+ 默认用 `caching_sha2_password`，pymysql 兼容。

如果遇到 `mysql_native_password` 报错，安装 `mysql-connector-python`：

```bash
pip install mysql-connector-python
DATABASE_URL="mysql+mysqlconnector://root:密码@localhost/acuseek" python backend/seed.py
```

### PostgreSQL 连不上

```bash
# 检查 postgres 是否运行
systemctl status postgresql

# 检查 pg_hba.conf 是否允许密码登录
# 修改后重启: systemctl restart postgresql
```

---

> `config.py` 通过环境变量 `DATABASE_URL` 控制数据库类型，优先读环境变量，没有则使用 SQLite。