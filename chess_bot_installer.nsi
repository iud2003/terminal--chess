; NSIS Installer Script for Chess Bot GUI
; Usage: makensis chess_bot_installer.nsi

!include "MUI2.nsh"

; Basic settings
Name "Chess Bot GUI"
OutFile "ChessBotSetup.exe"
InstallDir "$PROGRAMFILES\ChessBot"
RequestExecutionLevel admin

; MUI Settings
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Install Chess Bot"
    SetOutPath "$INSTDIR"
    
    ; Copy executable
    File "dist\ChessBot.exe"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\Chess Bot"
    CreateShortCut "$SMPROGRAMS\Chess Bot\Chess Bot.lnk" "$INSTDIR\ChessBot.exe"
    CreateShortCut "$SMPROGRAMS\Chess Bot\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\ChessBot.exe"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"
    
    Delete "$SMPROGRAMS\Chess Bot\Chess Bot.lnk"
    Delete "$SMPROGRAMS\Chess Bot\Uninstall.lnk"
    RMDir "$SMPROGRAMS\Chess Bot"
SectionEnd
