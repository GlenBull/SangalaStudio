@echo off
REM ==========================================================================
REM  Update Sangala Studio to the latest version from GitHub.
REM  Double-click this file. No admin, no install, no git, no compiler needed.
REM
REM  This updates BOTH parts of the program in one step:
REM     SangalaStudio.html  (the page: buttons, tools, fixes)
REM     SangalaStudio.exe   (the engine that drives the die cutter)
REM  so an ordinary update and a machine-engine update both arrive the same
REM  way -- you never have to rebuild anything by hand.
REM
REM  It only downloads when there is actually a newer version, and it never
REM  leaves you half-updated: if either file fails to download, nothing on your
REM  computer is changed.
REM
REM  It also puts a "Sangala Studio" icon on your Desktop -- and refreshes it if
REM  you have moved this folder -- so you can start the program without hunting
REM  for it. That happens whether or not there was anything new to download.
REM ==========================================================================
setlocal
cd /d "%~dp0"

set "BASE=https://raw.githubusercontent.com/GlenBull/SangalaStudio/main"
set "HTML=SangalaStudio.html"
set "EXE=SangalaStudio.exe"
set "TMPHTML=SangalaStudio.html.new"
set "TMPEXE=SangalaStudio.exe.new"

echo Checking for a newer Sangala Studio...
echo.

if exist "%TMPHTML%" del "%TMPHTML%" >nul 2>&1
if exist "%TMPEXE%"  del "%TMPEXE%"  >nul 2>&1

REM ---- 1. Download the page. curl is built into Windows 10/11; PowerShell is the fallback.
call :download "%BASE%/%HTML%" "%TMPHTML%"
if not exist "%TMPHTML%" goto :failed

REM A good page ends with the closing </html> tag; a truncated download will not.
find "</html>" "%TMPHTML%" >nul 2>&1
if errorlevel 1 goto :badfile

REM ---- 2. Compare release versions. Same version -> nothing to do, download nothing else.
set "REMOTEVER="
set "LOCALVER="
for /f "delims=" %%V in ('findstr /c:"SANGALA_VERSION" "%TMPHTML%"') do if not defined REMOTEVER set "REMOTEVER=%%V"
if exist "%HTML%" for /f "delims=" %%V in ('findstr /c:"SANGALA_VERSION" "%HTML%"') do if not defined LOCALVER set "LOCALVER=%%V"

if defined LOCALVER if "%LOCALVER%"=="%REMOTEVER%" (
  del "%TMPHTML%" >nul 2>&1
  echo Already up to date - nothing downloaded.
  call :shortcut
  echo.
  pause
  exit /b 0
)

REM ---- 3. There is a newer version. Download the engine too, BEFORE we touch anything.
echo A newer version is available. Downloading...
call :download "%BASE%/%EXE%" "%TMPEXE%"

REM Sanity-check the engine download: it must exist and be a real program (tens of KB, not an error page).
set "EXEOK="
for %%F in ("%TMPEXE%") do if %%~zF GTR 20000 set "EXEOK=1"
if not defined EXEOK goto :badfile

REM ---- 4. Both files are downloaded and look complete. Now swap them in.
REM     The engine may be running (its icon sits in the tray), which locks the file,
REM     so close it first. Nothing is lost -- you just reopen it when we are done.
taskkill /im "%EXE%" /f >nul 2>&1
REM Give Windows a moment to release the file after closing the program.
timeout /t 1 /nobreak >nul 2>&1

REM Keep the current copies as backups, then move the new ones into place.
if exist "%HTML%" copy /y "%HTML%" "%HTML%.bak" >nul
if exist "%EXE%"  copy /y "%EXE%"  "%EXE%.bak"  >nul

move /y "%TMPHTML%" "%HTML%" >nul
move /y "%TMPEXE%"  "%EXE%"  >nul 2>&1
if exist "%TMPEXE%" (
  REM The engine was still locked; wait a bit longer and try once more.
  timeout /t 2 /nobreak >nul 2>&1
  move /y "%TMPEXE%" "%EXE%" >nul 2>&1
)
if exist "%TMPEXE%" goto :exelocked

echo.
echo Done - Sangala Studio is up to date.
echo.
echo   Now reopen SangalaStudio.exe (double-click it). Your browser will open
echo   the design page. If a page was already open, press F5 to refresh it.
call :shortcut
echo.
echo   (Your previous version was saved as %HTML%.bak and %EXE%.bak, just in case.)
echo.
pause
exit /b 0

REM ==========================================================================
:download
REM  %1 = URL, %2 = output file. curl if present, else PowerShell.
where curl >nul 2>&1
if %errorlevel%==0 (
  curl -L -f -s -o "%~2" "%~1"
) else (
  powershell -NoProfile -Command "try { Invoke-WebRequest -Uri '%~1' -OutFile '%~2' -UseBasicParsing } catch { exit 1 }"
)
goto :eof

REM ==========================================================================
:shortcut
REM  Put (or refresh) a "Sangala Studio" icon on the Desktop, pointing at the
REM  engine in THIS folder -- so the icon keeps working even after an update,
REM  and gets corrected if the folder has been moved.
REM  Pure convenience: it writes only to the user's own Desktop (no admin), and
REM  if anything goes wrong the update itself is still good, so this never
REM  changes the exit code. The paths travel as environment variables so folder
REM  names with spaces or apostrophes cannot break the quoting, and
REM  SpecialFolders finds the real Desktop even when OneDrive has redirected it.
if not exist "%~dp0%EXE%" goto :eof
set "SANGALA_HOME=%~dp0"
set "SANGALA_TARGET=%~dp0%EXE%"
powershell -NoProfile -Command "try { $ws = New-Object -ComObject WScript.Shell; $p = Join-Path $ws.SpecialFolders('Desktop') 'Sangala Studio.lnk'; $l = $ws.CreateShortcut($p); $l.TargetPath = $env:SANGALA_TARGET; $l.WorkingDirectory = $env:SANGALA_HOME.TrimEnd('\'); $l.Description = 'Sangala Studio - Digital Fabrication Tool'; $l.Save(); exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 goto :eof
echo.
echo   A "Sangala Studio" icon is on your Desktop, ready to use.
goto :eof

REM ==========================================================================
:exelocked
echo.
echo Update ALMOST done - the page was updated, but the engine file was still
echo in use and could not be replaced.
echo   1. Close SangalaStudio.exe completely (right-click its tray icon, Exit).
echo   2. Run this update again.
echo Your program still works in the meantime.
echo.
pause
exit /b 1

:badfile
del "%TMPHTML%" >nul 2>&1
del "%TMPEXE%"  >nul 2>&1
:failed
echo.
echo Update FAILED - could not download a complete copy.
echo Your current Sangala Studio was NOT changed, so it still works.
echo Check the internet connection and run this again.
echo.
pause
exit /b 1
