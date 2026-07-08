@echo off
REM ==========================================================================
REM  Build SangalaStudio.exe -- the local helper that serves the polished
REM  Sangala Studio page and drives the Die Cutter. Compiled in-box with the
REM  .NET compiler already in Windows. No admin, no install, no internet.
REM
REM  Needs three files together in this folder:
REM     DieCutter.cs        (the proven USB + SVG + fabrication engine)
REM     SangalaServer.cs    (the local web helper / server)
REM     SangalaStudio.html  (the polished page it serves)
REM
REM  After building, keep SangalaStudio.exe and SangalaStudio.html together.
REM  Double-click SangalaStudio.exe: your browser opens the design page and it
REM  drives the machine.
REM ==========================================================================
setlocal
cd /d "%~dp0"

set "OUT=SangalaStudio.exe"
set "CSC=%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if not exist "%CSC%" set "CSC=%WINDIR%\Microsoft.NET\Framework\v4.0.30319\csc.exe"
if not exist "%CSC%" ( echo Could not find the built-in .NET compiler ^(csc.exe^). & pause & exit /b 1 )

echo Building %OUT% ...
"%CSC%" /nologo /target:winexe /main:DieCutterApp.Server /out:"%OUT%" ^
  /reference:System.dll ^
  /reference:System.Core.dll ^
  /reference:System.Drawing.dll ^
  /reference:System.Windows.Forms.dll ^
  /reference:System.Xml.dll ^
  "DieCutter.cs" "SangalaServer.cs"

if errorlevel 1 (
  echo.
  echo BUILD FAILED. Copy the red error messages above and send them back.
  echo.
  pause
  exit /b 1
)

echo.
echo Build succeeded:  "%~dp0%OUT%"
echo Keep SangalaStudio.exe and SangalaStudio.html together, then double-click the exe.
echo.
pause
