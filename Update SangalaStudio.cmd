@echo off
REM ==========================================================================
REM  Update Sangala Studio to the latest version from GitHub.
REM  Double-click this file. No admin, no install, no git, no compiler needed.
REM
REM  SangalaStudio.exe also runs this by itself every time it starts, before
REM  the program opens, so nobody has to remember to. It runs it with --launch:
REM  no window, nothing to answer, and the program opens whether or not there
REM  was anything new. Double-clicking this file still works as it always did.
REM
REM  This updates BOTH parts of the program in one step:
REM     SangalaStudio.html    (the page: buttons, tools, fixes)
REM     SangalaStudio.exe     (the engine that drives the die cutter)
REM     Sangala for Snap.xml  (the blocks Sangala loads into Snap! / TurtleStitch)
REM  so an ordinary update and a machine-engine update both arrive the same
REM  way -- you never have to rebuild anything by hand.
REM
REM  It also replaces ITSELF when GitHub has a newer copy, and then carries on
REM  as the new copy, so a change to these rules reaches every computer.
REM
REM  It only downloads when there is actually a newer version, and it never
REM  leaves you half-updated: if any file fails to download, nothing on your
REM  computer is changed.
REM
REM  It also puts a "Sangala Studio" icon on your Desktop -- and refreshes it if
REM  you have moved this folder -- so you can start the program without hunting
REM  for it. That happens whether or not there was anything new to download.
REM
REM  The line below tells SangalaStudio.exe that this copy can run unattended.
REM  An older copy without it would stop at "Press any key" in a window nobody
REM  can see, so the program never runs one.
REM  SANGALA_UPDATER: 1
REM ==========================================================================
setlocal
cd /d "%~dp0"

set "LAUNCH="
set "REPLACED="
for %%A in (%*) do (
  if /i "%%~A"=="--launch" set "LAUNCH=1"
  if /i "%%~A"=="--replaced" set "REPLACED=1"
)

set "BASE=https://raw.githubusercontent.com/maketolearn/SangalaStudio/main"
REM  To test a branch, set SANGALA_UPDATE_BASE to that branch's raw address first.
if defined SANGALA_UPDATE_BASE set "BASE=%SANGALA_UPDATE_BASE%"
set "HTML=SangalaStudio.html"
set "EXE=SangalaStudio.exe"
set "TMPHTML=SangalaStudio.html.new"
set "TMPEXE=SangalaStudio.exe.new"
set "XML=Sangala for Snap.xml"
set "TMPXML=Sangala for Snap.xml.new"
set "TMPSELF=%~nx0.new"
REM  The spaces in the names have to be encoded for the URL; %%20 is a literal %20 in a batch file.
set "XMLURL=%BASE%/Sangala%%20for%%20Snap.xml"
set "SELFURL=%BASE%/Update%%20SangalaStudio.cmd"
REM  The last line of this file is a marker that proves a download of it arrived whole. It is
REM  built in two pieces here so that this line does not contain the marker it looks for.
set "ENDMARK=SANGALA_UPDATER_"
set "RC=0"

echo Checking for a newer Sangala Studio...
echo.

if exist "%TMPHTML%" del "%TMPHTML%" >nul 2>&1
if exist "%TMPEXE%"  del "%TMPEXE%"  >nul 2>&1
if exist "%TMPXML%"  del "%TMPXML%"  >nul 2>&1
if exist "%TMPSELF%" del "%TMPSELF%" >nul 2>&1

REM ---- 1. Is this updater itself out of date? Only a copy that arrived whole and can run
REM     unattended is taken. cmd reads a batch file a line at a time as it goes, so the swap
REM     and the hand-over to the new copy sit in one bracketed block: cmd reads the whole
REM     block before running any of it, and running the new file without CALL means this one
REM     is never read again. --replaced stops a loop if the two copies somehow never match.
if defined REPLACED goto :checkpage
call :download "%SELFURL%" "%TMPSELF%"
if not exist "%TMPSELF%" goto :checkpage
findstr /c:"SANGALA_UPDATER:" "%TMPSELF%" >nul 2>&1 || goto :noself
findstr /c:"%ENDMARK%END" "%TMPSELF%" >nul 2>&1 || goto :noself
fc /b "%TMPSELF%" "%~f0" >nul 2>&1 && goto :noself
(
  copy /y "%~f0" "%~f0.bak" >nul 2>&1
  move /y "%TMPSELF%" "%~f0" >nul 2>&1
  "%~f0" %* --replaced
)
:noself
if exist "%TMPSELF%" del "%TMPSELF%" >nul 2>&1

:checkpage
REM ---- 2. Download the page. curl is built into Windows 10/11; PowerShell is the fallback.
call :download "%BASE%/%HTML%" "%TMPHTML%"
if not exist "%TMPHTML%" goto :failed

REM A good page ends with the closing </html> tag; a truncated download will not.
find "</html>" "%TMPHTML%" >nul 2>&1
if errorlevel 1 goto :badfile

REM ---- 3. Compare release versions. Same version -> nothing to do, download nothing else.
set "REMOTEVER="
set "LOCALVER="
for /f "delims=" %%V in ('findstr /c:"SANGALA_VERSION" "%TMPHTML%"') do if not defined REMOTEVER set "REMOTEVER=%%V"
if exist "%HTML%" for /f "delims=" %%V in ('findstr /c:"SANGALA_VERSION" "%HTML%"') do if not defined LOCALVER set "LOCALVER=%%V"

REM  Same version AND the blocks file already present -> nothing to do. Someone updating from a version
REM  released before the blocks shipped has the current page but no XML, so the version alone is not enough.
if defined LOCALVER if "%LOCALVER%"=="%REMOTEVER%" if exist "%XML%" (
  del "%TMPHTML%" >nul 2>&1
  echo Already up to date - nothing downloaded.
  if not defined LAUNCH call :shortcut
  goto :end
)

REM ---- 4. There is a newer version. Download the engine too, BEFORE we touch anything.
echo A newer version is available. Downloading...
call :download "%BASE%/%EXE%" "%TMPEXE%"
call :download "%XMLURL%" "%TMPXML%"

REM Sanity-check the engine download: it must exist and be a real program (tens of KB, not an error page).
set "EXEOK="
for %%F in ("%TMPEXE%") do if %%~zF GTR 20000 set "EXEOK=1"
if not defined EXEOK goto :badfile

REM Sanity-check the blocks download: a good one is an XML block library, not an error page.
find "<blocks" "%TMPXML%" >nul 2>&1
if errorlevel 1 goto :badfile

REM ---- 5. Everything is downloaded and looks complete. Now swap it in.
REM     Run by hand, this closes the program if it is running, so it starts again on the new
REM     engine. Nothing is lost -- you just reopen it when we are done. Run by the program
REM     at startup (--launch), the program is the one waiting for this to finish, so it is
REM     left alone: the engine is renamed out of the way instead, which Windows allows even
REM     while it runs, and the program starts the new one itself.
if not defined LAUNCH (
  taskkill /im "%EXE%" /f >nul 2>&1
  REM Give Windows a moment to release the file after closing the program.
  timeout /t 1 /nobreak >nul 2>&1
)

REM Keep the current copies as backups, then move the new ones into place.
if exist "%HTML%" copy /y "%HTML%" "%HTML%.bak" >nul
if exist "%XML%"  copy /y "%XML%"  "%XML%.bak"  >nul
move /y "%TMPXML%" "%XML%" >nul

call :swapexe
if errorlevel 1 (
  REM The engine was still locked; wait a bit longer and try once more.
  timeout /t 2 /nobreak >nul 2>&1
  call :swapexe
)
if errorlevel 1 goto :exelocked

REM  The page goes in LAST. Its version line is what decides whether there is anything to
REM  update, so if anything before this failed, the next run still sees the old version
REM  and tries again, instead of reporting "up to date" over an old engine.
move /y "%TMPHTML%" "%HTML%" >nul

echo.
echo Done - Sangala Studio is up to date.
if defined LAUNCH goto :end
echo.
echo   Now reopen SangalaStudio.exe (double-click it). Your browser will open
echo   the design page. If a page was already open, press F5 to refresh it.
call :shortcut
echo.
echo   (Your previous version was saved as %HTML%.bak and %EXE%.bak, just in case.)
goto :end

REM ==========================================================================
:end
REM  Run by the program at startup, nobody is there to press a key, so never wait for one.
echo.
if not defined LAUNCH pause
exit /b %RC%

REM ==========================================================================
:download
REM  %1 = URL, %2 = output file. curl if present, else PowerShell. A download that never
REM  answers must not hold the program shut, so both give up after a set time.
if exist "%~2" del "%~2" >nul 2>&1
where curl >nul 2>&1
if %errorlevel%==0 (
  curl -L -f -s --connect-timeout 5 --max-time 120 -o "%~2" "%~1"
) else (
  powershell -NoProfile -Command "try { Invoke-WebRequest -Uri '%~1' -OutFile '%~2' -UseBasicParsing -TimeoutSec 120 } catch { exit 1 }"
)
REM  A download that stopped part-way must not be mistaken for a whole one.
if errorlevel 1 del "%~2" >nul 2>&1
goto :eof

REM ==========================================================================
:swapexe
REM  Windows will not overwrite a program that is running, but it will rename one. So the
REM  current engine is renamed to the backup name and the new one moved into its place.
REM  Returns 1, with the old engine back where it was, if either step fails.
if exist "%EXE%" move /y "%EXE%" "%EXE%.bak" >nul 2>&1
if exist "%EXE%" exit /b 1
move /y "%TMPEXE%" "%EXE%" >nul 2>&1
if exist "%EXE%" exit /b 0
move /y "%EXE%.bak" "%EXE%" >nul 2>&1
exit /b 1

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
powershell -NoProfile -Command "try { $ws = New-Object -ComObject WScript.Shell; $p = Join-Path $ws.SpecialFolders('Desktop') 'Sangala Studio.lnk'; $l = $ws.CreateShortcut($p); $l.TargetPath = $env:SANGALA_TARGET; $l.WorkingDirectory = $env:SANGALA_HOME.TrimEnd('\'); $l.Description = 'Sangala Studio - Digital Fabrication tool'; $l.Save(); exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 goto :eof
echo.
echo   A "Sangala Studio" icon is on your Desktop, ready to use.
goto :eof

REM ==========================================================================
:exelocked
del "%TMPHTML%" >nul 2>&1
del "%TMPEXE%"  >nul 2>&1
echo.
echo Update NOT finished - the engine file was in use and could not be replaced.
echo   1. Close SangalaStudio.exe completely (right-click its tray icon, Exit).
echo   2. Run this update again.
echo Your program still works in the meantime.
set "RC=1"
goto :end

:badfile
del "%TMPHTML%" >nul 2>&1
del "%TMPEXE%"  >nul 2>&1
del "%TMPXML%" >nul 2>&1
:failed
echo.
echo Update FAILED - could not download a complete copy.
echo Your current Sangala Studio was NOT changed, so it still works.
echo Check the internet connection and run this again.
set "RC=1"
goto :end

REM  SANGALA_UPDATER_END
