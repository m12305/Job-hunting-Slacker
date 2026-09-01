[CmdletBinding()]
param(
    [string]$PythonExe = "D:\Anaconda\envs\agent\python.exe"
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

# GitHub Release 大文件在国内网络上容易超时。本地构建默认使用镜像，
# 调用者仍可提前设置同名环境变量来覆盖这两个地址。
if (-not $env:ELECTRON_MIRROR) {
    $env:ELECTRON_MIRROR = "https://npmmirror.com/mirrors/electron/"
}
if (-not $env:ELECTRON_BUILDER_BINARIES_MIRROR) {
    $env:ELECTRON_BUILDER_BINARIES_MIRROR = "https://npmmirror.com/mirrors/electron-builder-binaries/"
}
if (-not $env:ELECTRON_BUILDER_CACHE) {
    $env:ELECTRON_BUILDER_CACHE = Join-Path $projectRoot ".cache\electron-builder"
}

function Assert-LastExitCode([string]$StepName) {
    if ($LASTEXITCODE -ne 0) {
        throw "$StepName 失败，退出码：$LASTEXITCODE"
    }
}

if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
    throw "找不到 Python：$PythonExe"
}

Push-Location $projectRoot
try {
    Write-Host "[1/5] 安装前端依赖并构建页面"
    npm ci --prefix fronted
    Assert-LastExitCode "安装前端依赖"
    npm run build --prefix fronted
    Assert-LastExitCode "构建前端"

    Write-Host "[2/5] 安装后端与 PyInstaller 依赖"
    & $PythonExe -m pip install -r backend/requirements.txt -r desktop/requirements-build.txt
    Assert-LastExitCode "安装 Python 打包依赖"

    Write-Host "[3/5] 打包本地 FastAPI 服务"
    & $PythonExe -m PyInstaller --clean --noconfirm backend/qiuzhao_backend.spec
    Assert-LastExitCode "打包后端"

    Write-Host "[4/5] 安装 Electron 依赖并生成 NSIS 安装程序"
    npm ci --prefix desktop
    Assert-LastExitCode "安装桌面端依赖"
    npm run dist --prefix desktop
    Assert-LastExitCode "生成 Windows 安装程序"

    Write-Host "[5/5] 生成 SHA-256 校验文件"
    $installer = Get-ChildItem -LiteralPath (Join-Path $projectRoot "release") -Filter "QiuzhaoRoom-Setup-*-x64.exe" |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $installer) {
        throw "release 目录中没有找到安装程序"
    }
    $checksumPath = "$($installer.FullName).sha256"
    $hash = (Get-FileHash -LiteralPath $installer.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    Set-Content -LiteralPath $checksumPath -Value "$hash  $($installer.Name)" -Encoding ascii

    Write-Host ""
    Write-Host "安装包已生成：$($installer.FullName)"
    Write-Host "校验文件：$checksumPath"
}
finally {
    Pop-Location
}
