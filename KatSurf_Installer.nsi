!include "MUI2.nsh"

Name "KatSurf"
OutFile "KatSurf_Installer.exe"
InstallDir $PROGRAMFILES\KatSurf
RequestExecutionLevel admin

Section
  SetOutPath $INSTDIR
  File /r "C:\Users\User\Downloads\KatSurf\KatSurf V1.1\*.*"
SectionEnd