#!/bin/bash
# Sangala Studio - Chromebook setup.
#
# Run this inside the Linux Terminal, from the folder holding sangala_bridge.py:
#
#     bash setup.sh
#
# Three things this CANNOT do, because they are ChromeOS decisions rather than Linux ones: turn on the
# Linux environment, share the die cutter with Linux, and copy the files into "Linux files". Everything
# else is here.
#
# The point of this script is not to save typing, though it does. It is that a teacher or a student who
# hits a problem gets a sentence naming what to do, rather than [Errno 13]. Every check below exists
# because it cost somebody an evening on 5 August 2026.
#
# It also installs a LAUNCHER, which is the part that matters most: after this runs once, Sangala Studio
# starts from the ChromeOS launcher with a click, and the Terminal is never needed again. Typing a
# command correctly is the step non-Linux users get wrong, so the aim is that they type exactly one
# command, once, in their lives.
#
# Safe to run again. Every step checks before it acts.
#
# NOTE: sangala_bridge.py currently lives on the mac-bridge branch. Until that branch is merged, this
# script ships alongside it in the Chromebook zip rather than resolving it from this repository.

set -u

VID="0b4d"
RULE="99-silhouette.rules"
BRIDGE="sangala_bridge.py"
ICON="sangala-studio.png"
APPID="sangala-studio"
RUN_AFTER=1
[ "${1:-}" = "--check-only" ] && RUN_AFTER=0

say()  { printf '\n%s\n' "$*"; }
ok()   { printf '  [ok]   %s\n' "$*"; }
warn() { printf '  [--]   %s\n' "$*"; }
bad()  { printf '\n!! %s\n' "$*"; }

say "Sangala Studio - Chromebook setup"

# ---------------------------------------------------------------- 1. the right folder
if [ ! -f "$BRIDGE" ]; then
  bad "This is not the Sangala Studio folder."
  cat <<'EOF'
  There is no sangala_bridge.py here, so the files were probably not copied into Linux.

  In the Files application, open My files > Downloads, double-click
  "Sangala Studio for Chromebook.zip", press Ctrl-A then Ctrl-C, then click
  "Linux files" in the list on the left and press Ctrl-V.

  Then close this window, open the Terminal again, and run: bash setup.sh
EOF
  exit 1
fi
HERE=$(pwd -P)
ok "Sangala Studio files are here."

# ---------------------------------------------------------------- 2. python
if ! command -v python3 >/dev/null 2>&1; then
  bad "Python 3 is missing, which is unexpected in this environment."
  echo "  Try:  sudo apt update && sudo apt install -y python3"
  exit 1
fi
ok "Python 3 is installed."

# ---------------------------------------------------------------- 3. the USB library
# Debian packages pyusb as python3-usb. pip is NOT used: it is absent from this container, and recent
# Debian refuses pip installations into the system Python even when it is present.
if python3 -c "import usb.core" >/dev/null 2>&1; then
  ok "The USB library is installed."
else
  say "Installing the USB library. This needs your password."
  if ! sudo apt-get update -qq || ! sudo apt-get install -y -qq python3-usb; then
    bad "Could not install the USB library (python3-usb)."
    echo "  Check that the Chromebook is online, then run this script again."
    exit 1
  fi
  if python3 -c "import usb.core" >/dev/null 2>&1; then
    ok "The USB library is installed."
  else
    bad "python3-usb installed but Python still cannot import it."
    exit 1
  fi
fi

# ---------------------------------------------------------------- 4. the permission rule
NEED_RELOAD=0
if [ -f "/etc/udev/rules.d/$RULE" ] && cmp -s "$RULE" "/etc/udev/rules.d/$RULE"; then
  ok "Permission rule is already installed."
else
  if [ ! -f "$RULE" ]; then
    bad "$RULE is missing from this folder."
    echo "  Re-copy the zip contents into Linux files and run this script again."
    exit 1
  fi
  say "Installing the permission rule. This needs your password."
  sudo cp "$RULE" /etc/udev/rules.d/ || { bad "Could not copy the rule."; exit 1; }
  NEED_RELOAD=1
  ok "Permission rule installed."
fi
if [ "$NEED_RELOAD" = "1" ]; then
  sudo udevadm control --reload-rules >/dev/null 2>&1
  sudo udevadm trigger >/dev/null 2>&1
  ok "Permission rule applied to the connected device."
fi

# ---------------------------------------------------------------- 5. is the die cutter shared?
# This is the step ChromeOS controls, and the one people get stuck on. The machine reports no name, so
# it appears in the ChromeOS list as "USB device" and looking for the word Silhouette fails.
if ! command -v lsusb >/dev/null 2>&1; then
  sudo apt-get install -y -qq usbutils >/dev/null 2>&1
fi

if lsusb 2>/dev/null | grep -qi "$VID:"; then
  FOUND=$(lsusb | grep -i "$VID:" | head -1)
  ok "The die cutter is visible to Linux."
  printf '         %s\n' "$FOUND"
else
  bad "The die cutter is not shared with Linux."
  cat <<'EOF'
  Linux cannot see the machine, so nothing after this can work. It is switched on and
  plugged in, but ChromeOS has not handed it over.

  1. Make sure the die cutter is plugged in AND switched on.
  2. Open Settings, then About ChromeOS, then Developers, then
     "Linux development environment", then "Manage USB devices".
  3. Turn ON the entry named "USB device".

     It is called "USB device" and not Silhouette, because the machine does not
     report a name. To be sure which entry it is, unplug the die cutter and watch
     which entry disappears.

  Note: opening Settings > Printers can make ChromeOS take the device back. If the
  die cutter shows up there as an available printer, do NOT save it as a printer -
  Sangala Studio never prints to it.

  Then run this script again:  bash setup.sh
EOF
  exit 1
fi

# ---------------------------------------------------------------- 6. can we actually open it?
# This asks sangala_bridge.py's OWN Cutter.open() rather than reimplementing a probe, for two reasons.
# The check cannot drift from the thing it is checking - an earlier version here called only
# set_configuration(), which does not detach the kernel's usblp driver or claim the interface, so it
# could report success on a machine the bridge would then fail to open. And the failure text is the
# bridge's own, which now names the udev rule on Linux instead of telling a Chromebook user to close
# Silhouette Studio. Success also reports the MODEL NAME, which is how you confirm the machine was
# recognised rather than silently falling back to the Portrait 3 defaults.
PROBE=$(python3 - <<'PY' 2>/dev/null
import sys
sys.path.insert(0, ".")
try:
    import sangala_bridge as B
except Exception as e:
    print("IMPORT|%s" % e); raise SystemExit
c = B.Cutter()
try:
    c.open()
    print("OK|%s" % c.model_name)
except Exception as e:
    print("ERR|%s" % e)
finally:
    try:
        c.dispose()
    except Exception:
        pass
PY
)
PSTATE=${PROBE%%|*}
PTEXT=${PROBE#*|}
case "$PSTATE" in
  OK)
    ok "The die cutter can be opened. Permissions are correct."
    printf '         It reports itself as: %s\n' "$PTEXT"
    ;;
  ERR)
    bad "Linux can see the die cutter but Sangala Studio could not open it."
    printf '  %s\n' "$PTEXT"
    echo
    echo "  Fix that, then run this script again:  bash setup.sh"
    exit 1
    ;;
  IMPORT)
    bad "sangala_bridge.py is here but Python cannot load it."
    printf '  %s\n' "$PTEXT"
    echo "  The copy in this folder is probably damaged. Copy the zip contents into"
    echo "  Linux files again, and run this script once more."
    exit 1
    ;;
  *)
    warn "Could not test opening the die cutter. Continuing anyway."
    ;;
esac

# ---------------------------------------------------------------- 7. the launcher
# Crostini publishes any .desktop file under ~/.local/share/applications into the ChromeOS launcher,
# beside the Chrome applications. Clicking it must open SANGALA STUDIO - not a Terminal (Glen,
# 2026-08-10, after Jo's install): the icon opened a Terminal window that printed nothing and then
# appeared to freeze, and a classroom cannot be asked to tell a working server from a hung one.
#
# So the launcher now behaves the way the Windows one does. It starts the bridge in the BACKGROUND,
# waits until the port actually answers, and hands the address to Chrome. Nothing is shown unless
# something is wrong, in which case the log is opened so the reason is on screen rather than lost in
# a window that has already closed.
#
# The old version's silent first step is the prime suspect for the freeze: it probed twenty ports
# with urllib, which resolves and can consult a proxy before any timeout applies. That is replaced
# by a plain socket connect to the loopback address, which cannot do either.
BINDIR="$HOME/.local/bin"
APPDIR="$HOME/.local/share/applications"
ICONDIR="$HOME/.local/share/icons/hicolor/128x128/apps"
mkdir -p "$BINDIR" "$APPDIR" "$ICONDIR"

# The start script. HERE is written in as a literal, so the launcher keeps working from any folder.
{
  printf '#!/bin/bash\n'
  printf '# Sangala Studio launcher. Written by setup.sh - edit setup.sh, not this file.\n'
  printf 'HERE=%q\n' "$HERE"
  cat <<'BODY'
cd "$HERE" 2>/dev/null || {
  echo "The Sangala Studio folder has moved or been deleted:"
  echo "    $HERE"
  echo "Copy the files back into Linux files and run: bash setup.sh"
  read -r -p "Press Enter to close this window. " _
  exit 1
}

LOG="$HOME/.sangala-studio.log"

# Which port is a bridge already answering on? It takes the first free port from 8787 up, so a second
# copy would start on a different one and the page already open would keep talking to the first.
# Roger Wagner lost a call to exactly this on a Mac.
#
# A plain socket connect to 127.0.0.1, not a URL fetch: a fetch resolves a host name and may consult a
# proxy, and neither of those is bounded by the timeout, which is how a launcher that prints nothing
# can sit forever. This cannot block - the whole sweep is capped at a fifth of a second per port and
# talks only to the loopback address.
find_port() {
  python3 - <<'PY' 2>/dev/null
import socket
for p in range(8787, 8808):
    s = socket.socket(); s.settimeout(0.3)
    try:
        s.connect(("127.0.0.1", p))
        s.sendall(b"GET / HTTP/1.0\r\n\r\n")
        # KEEP READING until the marker turns up: one recv returns whatever has arrived, which is
        # usually just the HTTP headers, and the marker is on the second line of the page itself.
        buf = b""
        while len(buf) < 16384:
            chunk = s.recv(4096)
            if not chunk:
                break
            buf += chunk
            if b"SANGALA_VERSION" in buf:
                break
        if b"SANGALA_VERSION" in buf:
            print(p); break
    except Exception:
        pass
    finally:
        s.close()
PY
}

open_page() {                       # hand the address to the ChromeOS browser
  if command -v xdg-open >/dev/null 2>&1; then xdg-open "$1" >/dev/null 2>&1 & return 0; fi
  return 1
}

PORT=$(find_port)
if [ -z "$PORT" ]; then
  # Not running: start it detached, so the icon opens the application rather than a window to mind.
  : > "$LOG"
  nohup python3 sangala_bridge.py >>"$LOG" 2>&1 &
  for _ in $(seq 1 40); do          # up to about 20 seconds, checked five times a second
    PORT=$(find_port)
    [ -n "$PORT" ] && break
    sleep 0.5
  done
fi

if [ -n "$PORT" ]; then
  open_page "http://localhost:$PORT/" || {
    # No xdg-open: say where it is, in a window, since there is nothing else to show.
    echo "Sangala Studio is running at http://localhost:$PORT/"
    echo "Type that address into Chrome."
    read -r -p "Press Enter to close this window. " _
  }
  exit 0
fi

# It never came up. Show the reason rather than leaving an empty window: the log opens in the ChromeOS
# text editor, and failing that it is printed here.
echo "Sangala Studio did not start. The details are in:"
echo "    $LOG"
open_page "$LOG" || { echo; cat "$LOG" 2>/dev/null; }
read -r -p "Press Enter to close this window. " _
exit 1
BODY
} > "$BINDIR/$APPID"
chmod +x "$BINDIR/$APPID"

if [ -f "$ICON" ]; then
  cp -f "$ICON" "$ICONDIR/$APPID.png"
  ICONLINE="$ICONDIR/$APPID.png"
else
  ICONLINE="application-x-executable"      # a generic icon is better than a broken one
fi

cat > "$APPDIR/$APPID.desktop" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=Sangala Studio
GenericName=Digital Fabrication Tool
Comment=Design and cut with a Silhouette die cutter
Exec=$BINDIR/$APPID
Icon=$ICONLINE
Terminal=false
Categories=Education;Graphics;2DGraphics;
Keywords=Sangala;Silhouette;die cutter;cut;fabrication;
StartupNotify=false
EOF
chmod +x "$APPDIR/$APPID.desktop" 2>/dev/null
ok "Launcher installed. Sangala Studio is now in the ChromeOS launcher."

# xdg-open is how Linux hands a web address to the ChromeOS browser, and the icon now depends on it
# entirely: with no Terminal window there is nowhere else for the address to appear. So install it
# rather than only warning, which is what left the page unopened on Jo's Chromebook.
if ! command -v xdg-open >/dev/null 2>&1; then
  say "Installing xdg-utils, which is how Linux hands the page to Chrome..."
  sudo apt-get install -y -qq xdg-utils >/dev/null 2>&1
  if command -v xdg-open >/dev/null 2>&1; then
    ok "xdg-utils installed."
  else
    warn "xdg-utils could not be installed, so the icon cannot open the page by itself."
    echo "         Sangala Studio still runs; type localhost:8787 into Chrome to reach it."
  fi
fi

# ---------------------------------------------------------------- 8. make pasting work
# The ChromeOS Terminal sends bracketed-paste markers. If readline is not consuming them the marker
# arrives as text, and a pasted command fails as $'\E[200~sudo': command not found - which is how
# 5 August went. This makes pasting work in every Terminal opened from now on, so a command sent by
# email later can be pasted rather than retyped.
INPUTRC="$HOME/.inputrc"
if [ -f "$INPUTRC" ] && grep -q "enable-bracketed-paste" "$INPUTRC"; then
  ok "Terminal pasting is already set up."
else
  printf '\n# Added by Sangala Studio setup: let the Terminal paste commands properly.\nset enable-bracketed-paste on\n' >> "$INPUTRC"
  ok "Terminal pasting fixed (applies to Terminal windows opened from now on)."
fi

# ---------------------------------------------------------------- 9. done
say "Setup is complete."
cat <<EOF
  From now on you do not need the Terminal.

  Open the ChromeOS launcher (the circle at the bottom-left), search for
  "Sangala", and click Sangala Studio. It may take a few seconds to appear
  there the first time.

  If it is not there, this one line still starts it from the Terminal:

      bash setup.sh

  Clicking it opens Sangala Studio in Chrome. Nothing else appears: the part
  that talks to the die cutter runs out of sight. If the page does not open,
  type this address into Chrome yourself:

      http://localhost:8787/

  Pasting into the Terminal is Ctrl-Shift-V, never Ctrl-V.
EOF

if [ "$RUN_AFTER" = "1" ]; then
  say "Starting Sangala Studio now. It will open in Chrome."
  echo
  exec "$BINDIR/$APPID"
fi
