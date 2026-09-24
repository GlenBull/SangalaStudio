; Sangala Studio for Windows: the installer, the Windows counterpart of the Mac package.
;
; Built by GitHub on every release (.github/workflows/sangala-release.yml, the "installer" job) with
; Inno Setup, which GitHub's Windows machines carry; nobody builds it by hand. The workflow passes
; the release number read from SangalaStudio.html:
;
;     iscc /DAppVersion=2026-09-24.215 /DVersionNumeric=2026.9.24.215 tools\windows\SangalaStudio.iss
;
; No administrator is asked for, ever (PrivilegesRequired=lowest). In that mode Inno Setup's
; {autopf} is the user's own Program Files folder, %LOCALAPPDATA%\Programs, and that matters beyond
; permissions: SangalaStudio.exe runs Update SangalaStudio.cmd at every start, and the updater
; rewrites the files beside it, which it could not do inside the shared C:\Program Files.
;
; The file is not called setup.exe. Inno Setup's manual warns that Windows loads extra DLLs into
; anything with that name, "unsafely", and that they "can be hijacked".

#ifndef AppVersion
  #define AppVersion "0.0.0.0"
#endif
#ifndef VersionNumeric
  #define VersionNumeric "0.0.0.0"
#endif
; The top of the repository, from this script's folder. Inno Setup reads source files relative to
; the script's folder by default.
#define Root "..\.."

[Setup]
AppId=SangalaStudio
AppName=Sangala Studio
AppVersion={#AppVersion}
AppPublisher=Make to Learn
AppPublisherURL=https://github.com/maketolearn/SangalaStudio
VersionInfoVersion={#VersionNumeric}
OutputBaseFilename=Sangala Studio Setup
PrivilegesRequired=lowest
DefaultDirName={autopf}\Sangala Studio
DisableDirPage=yes
DisableProgramGroupPage=yes
SetupIconFile={#Root}\Sangala.ico
UninstallDisplayName=Sangala Studio
UninstallDisplayIcon={app}\SangalaStudio.exe
; The bridge holds this mutex while it runs (SangalaServer.cs), so Setup and Uninstall can ask for
; it to be closed first instead of meeting a locked engine file.
AppMutex=SangalaStudioBridge
WizardStyle=modern

[Files]
; The same program the Mac package carries, with the Windows engine and updater in place of the
; Python bridge and the .command files.
Source: "{#Root}\SangalaStudio.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Root}\SangalaStudio.html"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Root}\Sangala for Snap.xml"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Root}\Update SangalaStudio.cmd"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Root}\samples\Calibration Card.svg"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Root}\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Root}\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Sangala Studio"; Filename: "{app}\SangalaStudio.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\Sangala Studio"; Filename: "{app}\SangalaStudio.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\SangalaStudio.exe"; Description: "Start Sangala Studio"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
; What the updater leaves beside the program: the copies it keeps (.bak) and any download it had
; not finished (.new).
Type: files; Name: "{app}\*.bak"
Type: files; Name: "{app}\*.new"
