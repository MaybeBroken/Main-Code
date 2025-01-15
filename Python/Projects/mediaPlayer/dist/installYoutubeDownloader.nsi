; NSIS script for YoutubeDownloader

!define MUI_PRODUCT "YoutubeDownloader"
!include "MUI2.nsh"
OutFile "YoutubeDownloader.exe"
Name "YoutubeDownloader"
InstallDir $PROFILE\YoutubeDownloader
RequestExecutionLevel admin

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Install"
    SetOutPath $INSTDIR
    File "C:\Users\david\git\Code\Python\Projects\mediaPlayer\dist\Main.py"
    File /r "C:\Users\david\git\Code\Python\Projects\mediaPlayer\dist\python\*"
    File "C:\Users\david\git\Code\Python\Projects\mediaPlayer\dist\_req.txt"
    File "C:\Users\david\git\Code\Python\Projects\mediaPlayer\dist\YoutubeDownloader.bat"
    CreateShortcut "$DESKTOP\YoutubeDownloader.lnk" "$INSTDIR\YoutubeDownloader.bat"
SectionEnd
Section "Run"
    Exec "$INSTDIR\YoutubeDownloader.bat"
SectionEnd