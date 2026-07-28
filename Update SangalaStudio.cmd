@echo off
REM ==========================================================================
REM  Update Sangala Studio to the latest version from GitHub.
REM  Double-click this file. No admin, no install, no git needed.
REM
REM  This updates the whole program in one step. It downloads the latest
REM  source:
REM     SangalaStudio.html    (the page: buttons, tools, fixes)
REM     DieCutter.cs          (the USB + GPGL engine source)
REM     SangalaServer.cs      (the local bridge source)
REM     Build SangalaStudio.cmd (the compile script)
REM     Sangala for Snap.xml  (the blocks Sangala loads into Snap! / TurtleStitch)
REM     Sangala.ico           (the program icon)
REM  and then rebuilds the engine (SangalaStudio.exe) on your own computer
REM  with the .NET compiler that ships inside Windows -- so an ordinary
REM  update and a machine-engine update both arrive the same way, and you
REM  never have to rebuild anything by hand.
REM
REM  We build the engine here rather than downloading a ready-made one: a
REM  program you compile yourself carries no "downloaded from the internet"
REM  mark, so Windows will not warn about it.
REM
REM  It only downloads when there is actually a newer version, and it never
REM  leaves you half-updated: if any file fails to download or fails its
REM  check, nothing on your computer is changed.
REM
REM  It also puts a "Sangala Studio" icon on your Desktop -- and refreshes it
REM  if you have moved this folder -- so you can start the program without
REM  hunting for it. That happens whether or not there was anything new.
REM ==========================================================================
setlocal
cd /d "%~dp0"

set "BASE=https://raw.githubusercontent.com/GlenBull/SangalaStudio/installer-only"

set "HTML=SangalaStudio.html"
set "CS1=DieCutter.cs"
set "CS2=SangalaServer.cs"
set "BUILD=Build SangalaStudio.cmd"
set "XML=Sangala for Snap.xml"
set "ICO=Sangala.ico"
set "EXE=SangalaStudio.exe"

set "TMPHTML=SangalaStudio.html.new"
set "TMPCS1=DieCutter.cs.new"
set "TMPCS2=SangalaServer.cs.new"
set "TMPBUILD=Build SangalaStudio.cmd.new"
set "TMPXML=Sangala for Snap.xml.new"
set "TMPICO=Sangala.ico.new"

REM  Spaces in a name have to be encoded for the URL; %%20 is a literal %20 in a batch file.
set "BUILDURL=%BASE%/Build%%20SangalaStudio.cmd"
set "XMLURL=%BASE%/Sangala%%20for%%20Snap.xml"

echo Checking for a newer Sangala Studio...
echo.

for %%T in ("%TMPHTML%" "%TMPCS1%" "%TMPCS2%" "%TMPBUILD%" "%TMPXML%" "%TMPICO%") do if exist "%%~T" del "%%~T" >nul 2>&1

REM ---- 1. Download the page. curl is built into Windows 10/11; PowerShell is the fallback.
call :download "%BASE%/%HTML%" "%TMPHTML%"
if not exist "%TMPHTML%" goto :failed

REM A good page ends with the closing </html> tag; a truncated download will not.
find "</html>" "%TMPHTML%" >nul 2>&1
if errorlevel 1 goto :badfile

REM ---- 2. Compare release versions. Same version, and already built -> nothing to do.
set "REMOTEVER="
set "LOCALVER="
for /f "delims=" %%V in ('findstr /c:"SANGALA_VERSION" "%TMPHTML%"') do if not defined REMOTEVER set "REMOTEVER=%%V"
if exist "%HTML%" for /f "delims=" %%V in ('findstr /c:"SANGALA_VERSION" "%HTML%"') do if not defined LOCALVER set "LOCALVER=%%V"

REM  Same version AND the engine is already built AND the blocks file is present -> nothing to do.
if defined LOCALVER if "%LOCALVER%"=="%REMOTEVER%" if exist "%EXE%" if exist "%XML%" (
  del "%TMPHTML%" >nul 2>&1
  echo Already up to date - nothing downloaded.
  call :shortcut
  echo.
  pause
  exit /b 0
)

REM ---- 3. There is a newer version. Download the rest of the source, BEFORE we touch anything.
echo A newer version is available. Downloading the source...
call :download "%BASE%/%CS1%"  "%TMPCS1%"
call :download "%BASE%/%CS2%"  "%TMPCS2%"
call :download "%BUILDURL%"    "%TMPBUILD%"
call :download "%XMLURL%"      "%TMPXML%"
call :download "%BASE%/%ICO%"  "%TMPICO%"

REM ---- 4. Sanity-check every download before we swap anything in.
REM  The engine sources must be the real thing (they name the program's namespace).
find "DieCutterApp" "%TMPCS1%" >nul 2>&1
if errorlevel 1 goto :badfile
find "DieCutterApp" "%TMPCS2%" >nul 2>&1
if errorlevel 1 goto :badfile

REM  The build script must be the real compile script (it calls csc.exe).
find "csc.exe" "%TMPBUILD%" >nul 2>&1
if errorlevel 1 goto :badfile

REM  The blocks file must be an XML block library, not an error page.
find "<blocks" "%TMPXML%" >nul 2>&1
if errorlevel 1 goto :badfile

REM  The icon must be a real icon file (well over 100 bytes), not an error page.
set "ICOOK="
for %%F in ("%TMPICO%") do if %%~zF GTR 100 set "ICOOK=1"
if not defined ICOOK goto :badfile

REM ---- 5. Everything downloaded and looks complete. Swap the source in.
REM     The engine may be running (its icon sits in the tray), which locks the
REM     exe, so close it first. Nothing is lost -- you reopen it when we are done.
taskkill /im "%EXE%" /f >nul 2>&1
REM Give Windows a moment to release the file after closing the program.
timeout /t 1 /nobreak >nul 2>&1

REM Keep the current copies as backups, then move the new ones into place.
for %%P in ("%HTML%" "%CS1%" "%CS2%" "%BUILD%" "%XML%" "%ICO%") do if exist "%%~P" copy /y "%%~P" "%%~P.bak" >nul

move /y "%TMPHTML%"  "%HTML%"  >nul
move /y "%TMPCS1%"   "%CS1%"   >nul
move /y "%TMPCS2%"   "%CS2%"   >nul
move /y "%TMPBUILD%" "%BUILD%" >nul
move /y "%TMPXML%"   "%XML%"   >nul
move /y "%TMPICO%"   "%ICO%"   >nul

REM ---- 6. Rebuild the engine locally with the in-box .NET compiler.
REM     Redirect the build script's input from nul so its own "pause" does not
REM     stop and wait here -- this window drives it start to finish.
echo.
echo Building the die cutter engine on your computer...
call "%BUILD%" <nul

REM  A good build produces an exe well over 20 KB; anything smaller means it failed.
set "EXEOK="
if exist "%EXE%" for %%F in ("%EXE%") do if %%~zF GTR 20000 set "EXEOK=1"
if not defined EXEOK goto :buildfailed

echo.
echo Done - Sangala Studio is up to date.
echo.
echo   Now reopen SangalaStudio.exe (double-click it). Your browser will open
echo   the design page. If a page was already open, press F5 to refresh it.
call :shortcut
echo.
echo   (Your previous files were saved alongside as *.bak, just in case.)
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
powershell -NoProfile -Command "try { $ws = New-Object -ComObject WScript.Shell; $p = Join-Path $ws.SpecialFolders('Desktop') 'Sangala Studio.lnk'; $l = $ws.CreateShortcut($p); $l.TargetPath = $env:SANGALA_TARGET; $l.WorkingDirectory = $env:SANGALA_HOME.TrimEnd('\'); $l.Description = 'Sangala Studio - Digital Fabrication tool'; $l.Save(); exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 goto :eof
echo.
echo   A "Sangala Studio" icon is on your Desktop, ready to use.
goto :eof

REM ==========================================================================
:buildfailed
echo.
echo Update ALMOST done - the source was updated, but the engine did not
echo build. Try running "Build SangalaStudio.cmd" by hand to see the error.
echo Your previous files were saved alongside as *.bak.
echo.
pause
exit /b 1

:badfile
for %%T in ("%TMPHTML%" "%TMPCS1%" "%TMPCS2%" "%TMPBUILD%" "%TMPXML%" "%TMPICO%") do if exist "%%~T" del "%%~T" >nul 2>&1
:failed
echo.
echo Update FAILED - could not download a complete copy.
echo Your current Sangala Studio was NOT changed, so it still works.
echo Check the internet connection and run this again.
echo.
pause
exit /b 1
