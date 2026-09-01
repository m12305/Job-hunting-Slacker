!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "nsDialogs.nsh"

; electron-builder 的内置桌面快捷方式关闭，由完成页复选框交给用户决定。
!macro customFinishPage
  Function StartQiuzhaoRoom
    ${StdUtils.ExecShellAsUser} $0 "$launchLink" "open" ""
  FunctionEnd

  !define MUI_FINISHPAGE_RUN
  !define MUI_FINISHPAGE_RUN_TEXT "安装完成后运行求职摆烂管理局"
  !define MUI_FINISHPAGE_RUN_FUNCTION "StartQiuzhaoRoom"

  Function CreateQiuzhaoDesktopShortcut
    CreateShortCut "$newDesktopLink" "$appExe" "" "$appExe" 0 "" "" "${APP_DESCRIPTION}"
    ClearErrors
    WinShell::SetLnkAUMI "$newDesktopLink" "${APP_ID}"
    System::Call 'Shell32::SHChangeNotify(i 0x1002, i 0, i 0, i 0)'
  FunctionEnd

  Var QiuzhaoDesktopShortcutCheckbox
  Var QiuzhaoDesktopShortcutState

  Function ShowQiuzhaoDesktopShortcutCheckbox
    ${NSD_CreateCheckbox} 120u 110u 195u 10u "创建桌面快捷方式"
    Pop $QiuzhaoDesktopShortcutCheckbox
    ${NSD_SetState} $QiuzhaoDesktopShortcutCheckbox ${BST_CHECKED}
  FunctionEnd

  Function FinishQiuzhaoDesktopShortcut
    ${NSD_GetState} $QiuzhaoDesktopShortcutCheckbox $QiuzhaoDesktopShortcutState
    ${If} $QiuzhaoDesktopShortcutState == ${BST_CHECKED}
      Call CreateQiuzhaoDesktopShortcut
    ${Else}
      Delete "$newDesktopLink"
    ${EndIf}
  FunctionEnd

  !define MUI_PAGE_CUSTOMFUNCTION_SHOW ShowQiuzhaoDesktopShortcutCheckbox
  !define MUI_PAGE_CUSTOMFUNCTION_LEAVE FinishQiuzhaoDesktopShortcut
  !insertmacro MUI_PAGE_FINISH
!macroend
