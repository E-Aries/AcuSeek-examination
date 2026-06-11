# =============================================
# AcuSeek 企业考核管理系统 - Windows 一键安装脚本
# 用法: 右键 "以 PowerShell 运行"
# =============================================

$PROJECT_DIR = "$env:USERPROFILE\AcuSeek"
$BACKEND_LOG = "$env:TEMP\acuseek-backend.log"
$FRONTEND_LOG = "$env:TEMP\acuseek-frontend.log"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " AcuSeek 企业考核管理系统 - 安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. 检查环境
Write-Host "`n[1/6] 检查运行环境..." -ForegroundColor Yellow
$envOK = $true

try { python --version | Out-Null } catch {
    Write-Host "  ❌ Python 未安装，请安装 Python 3.10+" -ForegroundColor Red
    $envOK = $false
}
try { node --version | Out-Null } catch {
    Write-Host "  ❌ Node.js 未安装，请安装 Node.js 22+" -ForegroundColor Red
    $envOK = $false
}
try { git --version | Out-Null } catch {
    Write-Host "  ❌ Git 未安装" -ForegroundColor Red
    $envOK = $false
}

if (-not $envOK) {
    Write-Host "`n请先安装缺失的依赖后重新运行此脚本" -ForegroundColor Red
    Read-Host "按回车退出"
    exit 1
}
Write-Host "  ✅ Python: $(python --version)"
Write-Host "  ✅ Node.js: $(node --version)"
Write-Host "  ✅ Git: OK"

# 2. 克隆项目
Write-Host "`n[2/6] 克隆项目..." -ForegroundColor Yellow
if (Test-Path "$PROJECT_DIR") {
    Write-Host "  项目目录已存在，更新代码..."
    Set-Location $PROJECT_DIR
    git pull
} else {
    git clone https://gitee.com/aries-minnasang/AcuSeek.git $PROJECT_DIR
    Set-Location $PROJECT_DIR
}

# 3. 安装后端依赖
Write-Host "`n[3/6] 安装后端依赖..." -ForegroundColor Yellow
Set-Location "$PROJECT_DIR\backend"
pip install -r requirements.txt -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ 后端依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "  ❌ 安装失败，请检查 pip" -ForegroundColor Red
    Read-Host "按回车退出"
    exit 1
}

# 4. 初始化数据库
Write-Host "`n[4/6] 初始化数据库..." -ForegroundColor Yellow
Set-Location $PROJECT_DIR
python backend\seed.py
Write-Host "  ✅ 数据库初始化完成" -ForegroundColor Green

# 5. 安装前端依赖
Write-Host "`n[5/6] 安装前端依赖..." -ForegroundColor Yellow
npm install --no-audit --no-fund
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ 前端依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "  ❌ 安装失败，请检查 npm" -ForegroundColor Red
    Read-Host "按回车退出"
    exit 1
}

# 6. 启动服务
Write-Host "`n[6/6] 启动服务..." -ForegroundColor Yellow

Set-Location "$PROJECT_DIR\backend"
$backend = Start-Process -WindowStyle Hidden -FilePath "python" -ArgumentList "-m uvicorn main:app --host 0.0.0.0 --port 8000" -PassThru
Write-Host "  ✅ 后端已启动 (PID: $($backend.Id))" -ForegroundColor Green

Set-Location $PROJECT_DIR
$frontend = Start-Process -WindowStyle Hidden -FilePath "node" -ArgumentList "node_modules\.bin\vite --host" -PassThru
Write-Host "  ✅ 前端已启动 (PID: $($frontend.Id))" -ForegroundColor Green

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 安装完成!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " 前端地址:  http://localhost:5173" -ForegroundColor White
Write-Host " 后端地址:  http://localhost:8000" -ForegroundColor White
Write-Host " API 文档:  http://localhost:8000/docs" -ForegroundColor White
Write-Host " 登录账号:  admin / admin123" -ForegroundColor White
Write-Host ""
Write-Host " MySQL 用户如需切换数据库:" -ForegroundColor Gray
Write-Host "   先改 backend\config.py 中的 DATABASE_URL"
Write-Host "   再重新运行 python backend\seed.py"
Write-Host ""

Read-Host "按回车退出"