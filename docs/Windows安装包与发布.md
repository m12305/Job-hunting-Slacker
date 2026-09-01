# Windows 安装包与 GitHub Release 发布

## 发行形态

Windows x64 安装包由三部分组成：

1. Electron 原生窗口与应用生命周期；
2. PyInstaller 打包的 FastAPI 本地服务；
3. Vite 构建后的前端静态资源。

最终用户不需要安装 Python、Node.js 或数据库。安装程序提供安装目录选择；完成页提供“创建桌面快捷方式”复选框，默认勾选。

## 本地构建

在项目根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1
```

如需使用其他 Python：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1 -PythonExe "C:\path\to\python.exe"
```

构建产物：

```text
release/
├── QiuzhaoRoom-Setup-<版本号>-x64.exe
└── QiuzhaoRoom-Setup-<版本号>-x64.exe.sha256
```

## 用户数据位置

安装目录只保存程序文件。数据库、上传文件、备份与日志保存在当前 Windows 用户的应用数据目录：

```text
%APPDATA%\qiuzhao-room-desktop\
├── data\
└── logs\
```

卸载程序默认保留该目录，避免误删求职数据。用户若确定不再需要，可在卸载后手动删除。

## GitHub 自动发布

工作流文件：`.github/workflows/windows-release.yml`。

发布新版本时：

1. 修改 `desktop/package.json` 中的 `version`；
2. 提交并推送代码；
3. 创建与版本一致的标签，例如本次修复版 `v1.0.1`；
4. 推送标签，GitHub Actions 会构建 Windows x64 安装包并创建 Release。

```bash
git tag v1.0.1
git push origin v1.0.1
```

也可以在 GitHub 的 Actions 页面手动运行 `Build Windows installer`。手动运行只生成工作流附件，不创建 Release。

## 代码签名

未签名安装包可以正常发布，但 Windows SmartScreen 可能显示“未知发布者”。正式公开分发建议购买 Windows 代码签名证书，并在仓库 Actions Secrets 中配置：

- `WINDOWS_CSC_LINK`：Base64 编码证书或证书下载地址；
- `WINDOWS_CSC_KEY_PASSWORD`：证书密码。

未配置这两个 Secret 时，工作流会生成未签名安装包。
