const { app, BrowserWindow, Menu, dialog, shell } = require('electron')
const { spawn } = require('node:child_process')
const fs = require('node:fs')
const net = require('node:net')
const path = require('node:path')

let mainWindow = null
let backendProcess = null
let backendOrigin = null
let quitting = false

const gotSingleInstanceLock = app.requestSingleInstanceLock()
if (!gotSingleInstanceLock) {
  app.quit()
}

function appendDesktopLog(message) {
  try {
    const logDir = path.join(app.getPath('userData'), 'logs')
    fs.mkdirSync(logDir, { recursive: true })
    fs.appendFileSync(
      path.join(logDir, 'desktop.log'),
      `${new Date().toISOString()} ${message}\n`,
      'utf8',
    )
  } catch {
    // 日志写入失败不能阻止应用启动。
  }
}

function reserveLocalPort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer()
    server.unref()
    server.once('error', reject)
    server.listen(0, '127.0.0.1', () => {
      const address = server.address()
      const port = typeof address === 'object' && address ? address.port : null
      server.close((error) => {
        if (error) reject(error)
        else if (port) resolve(port)
        else reject(new Error('无法分配本地端口'))
      })
    })
  })
}

function backendCommand(port) {
  if (app.isPackaged) {
    return {
      executable: path.join(process.resourcesPath, 'backend', 'qiuzhao-backend.exe'),
      args: ['--host', '127.0.0.1', '--port', String(port)],
      cwd: path.join(process.resourcesPath, 'backend'),
    }
  }

  const projectRoot = path.resolve(__dirname, '..')
  return {
    executable: process.env.QIUZHAO_PYTHON || 'python',
    args: [
      path.join(projectRoot, 'backend', 'desktop_entry.py'),
      '--host',
      '127.0.0.1',
      '--port',
      String(port),
    ],
    cwd: path.join(projectRoot, 'backend'),
  }
}

function startBackend(port) {
  const command = backendCommand(port)
  const userDataDir = app.getPath('userData')
  const dataDir = path.join(userDataDir, 'data')
  const logDir = path.join(userDataDir, 'logs')
  fs.mkdirSync(dataDir, { recursive: true })
  fs.mkdirSync(logDir, { recursive: true })

  if (!fs.existsSync(command.executable) && app.isPackaged) {
    throw new Error(`后端程序不存在：${command.executable}`)
  }

  appendDesktopLog(`启动本地服务：${command.executable} ${command.args.join(' ')}`)
  backendProcess = spawn(command.executable, command.args, {
    cwd: command.cwd,
    windowsHide: true,
    env: {
      ...process.env,
      QIUZHAO_DATA_DIR: dataDir,
      QIUZHAO_LOG_FILE: path.join(logDir, 'backend.log'),
      QIUZHAO_DESKTOP_ORIGIN: `http://127.0.0.1:${port}`,
      PYTHONUTF8: '1',
    },
    stdio: ['ignore', 'pipe', 'pipe'],
  })

  backendProcess.stdout?.on('data', (chunk) => appendDesktopLog(`[backend] ${chunk.toString().trim()}`))
  backendProcess.stderr?.on('data', (chunk) => appendDesktopLog(`[backend] ${chunk.toString().trim()}`))
  backendProcess.once('error', (error) => appendDesktopLog(`本地服务启动失败：${error.stack || error.message}`))
  backendProcess.once('exit', (code, signal) => {
    appendDesktopLog(`本地服务退出：code=${code} signal=${signal}`)
    backendProcess = null
    if (!quitting && mainWindow && !mainWindow.isDestroyed()) {
      dialog.showMessageBox(mainWindow, {
        type: 'error',
        title: '本地服务已停止',
        message: '求职摆烂管理局的本地服务意外退出。',
        detail: `请重新启动应用。日志位置：${path.join(app.getPath('userData'), 'logs')}`,
      })
    }
  })
}

async function waitForBackend(origin, timeoutMs = 30000) {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    if (!backendProcess) throw new Error('本地服务进程已退出')
    try {
      const response = await fetch(`${origin}/api/health`, { signal: AbortSignal.timeout(1500) })
      if (response.ok) return
    } catch {
      // 服务初始化和数据库迁移期间继续等待。
    }
    await new Promise((resolve) => setTimeout(resolve, 250))
  }
  throw new Error('本地服务启动超时')
}

function isSameAppOrigin(url) {
  try {
    return new URL(url).origin === backendOrigin
  } catch {
    return false
  }
}

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 980,
    minHeight: 640,
    show: false,
    autoHideMenuBar: true,
    backgroundColor: '#f4f7f8',
    icon: path.join(__dirname, 'build', 'icon.png'),
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      spellcheck: false,
    },
  })

  mainWindow.once('ready-to-show', () => mainWindow?.show())

  mainWindow.webContents.on('did-fail-load', (_event, code, description, url, isMainFrame) => {
    appendDesktopLog(`页面加载失败：code=${code} mainFrame=${isMainFrame} url=${url} ${description}`)
  })
  mainWindow.webContents.on('render-process-gone', (_event, details) => {
    appendDesktopLog(`渲染进程退出：reason=${details.reason} code=${details.exitCode}`)
  })
  mainWindow.webContents.on('console-message', (_event, ...args) => {
    const details = args.length === 1 && typeof args[0] === 'object'
      ? args[0]
      : { level: args[0], message: args[1], lineNumber: args[2], sourceId: args[3] }
    if (details.level === 'error' || details.level === 3) {
      appendDesktopLog(`页面错误：${details.message} (${details.sourceId || 'unknown'}:${details.lineNumber || 0})`)
    }
  })

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (isSameAppOrigin(url)) {
      return {
        action: 'allow',
        overrideBrowserWindowOptions: {
          autoHideMenuBar: true,
          webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true },
        },
      }
    }
    if (/^https?:/i.test(url)) shell.openExternal(url)
    return { action: 'deny' }
  })

  mainWindow.webContents.on('will-navigate', (event, url) => {
    if (!isSameAppOrigin(url)) {
      event.preventDefault()
      if (/^https?:/i.test(url)) shell.openExternal(url)
    }
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

function stopBackend() {
  if (!backendProcess || backendProcess.killed) return
  appendDesktopLog('正在停止本地服务')
  backendProcess.kill()
  backendProcess = null
}

async function startApplication() {
  const port = await reserveLocalPort()
  backendOrigin = `http://127.0.0.1:${port}`
  startBackend(port)
  await waitForBackend(backendOrigin)
  appendDesktopLog(`本地服务已就绪：${backendOrigin}`)
  createMainWindow()
  const developmentUrl = !app.isPackaged ? process.env.QIUZHAO_DEV_SERVER_URL : null
  await mainWindow.loadURL(developmentUrl || backendOrigin)
}

app.setAppUserModelId('io.github.m12305.qiuzhao-room')

app.on('second-instance', () => {
  if (!mainWindow) return
  if (mainWindow.isMinimized()) mainWindow.restore()
  mainWindow.show()
  mainWindow.focus()
})

app.whenReady().then(async () => {
  Menu.setApplicationMenu(null)
  try {
    await startApplication()
  } catch (error) {
    appendDesktopLog(`应用启动失败：${error.stack || error.message}`)
    dialog.showErrorBox(
      '求职摆烂管理局启动失败',
      `${error.message}\n\n日志位置：${path.join(app.getPath('userData'), 'logs')}`,
    )
    app.quit()
  }
})

app.on('before-quit', () => {
  quitting = true
  stopBackend()
})

app.on('window-all-closed', () => app.quit())

process.on('uncaughtException', (error) => appendDesktopLog(`未捕获异常：${error.stack || error.message}`))
process.on('unhandledRejection', (error) => appendDesktopLog(`未处理 Promise：${error?.stack || error}`))
