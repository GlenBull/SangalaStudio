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
# Safe to run again. Every step checks before it acts.
#
# NOTE: sangala_bridge.py currently lives on the mac-bridge branch. Until that branch is merged, this
# script ships alongside it in the Chromebook zip rather than resolving it from this repository.

set -u

VID="0b4d"
RULE="99-silhouette.rules"
BRIDGE="sangala_bridge.py"
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

if lsusb 2>/dev/null | grep -qi ":\?$VID:"; then
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
OPEN=$(python3 - <<'PY' 2>/dev/null
import sys
try:
    import usb.core
    d = usb.core.find(idVendor=0x0B4D)
    if d is None:
        print("notfound"); sys.exit()
    try:
        d.set_configuration()
        print("ok")
    except Exception as e:
        print("denied" if "denied" in str(e).lower() or "13" in str(e) else "busy")
except Exception:
    print("error")
PY
)
case "$OPEN" in
  ok)
    ok "The die cutter can be opened. Permissions are correct."
    ;;
  denied)
    bad "Linux can see the die cutter but is not allowed to open it."
    echo "  The permission rule is installed but has not taken effect yet."
    echo "  Unplug the die cutter, plug it back in, and run this script again."
    exit 1
    ;;
  busy)
    bad "Something else is holding the die cutter."
    echo "  Check that Sangala Studio is not already running in another Terminal tab,"
    echo "  and that the die cutter has not been saved as a printer in ChromeOS Settings."
    exit 1
    ;;
  *)
    warn "Could not test opening the die cutter. Continuing anyway."
    ;;
esac

# ---------------------------------------------------------------- 7. where the page will be
say "Setup is complete."
cat <<'EOF'
  When Sangala Studio starts it prints an address containing "localhost". On a
  Chromebook that address may not work, because Linux runs in a separate machine
  with its own localhost.

  Open ONE of these in the Chrome browser:

      http://localhost:8787/            (ChromeOS 143 and newer)
      http://penguin.linux.test:8787/   (older ChromeOS)

  Try the first. If the page does not load, use the second.
  If a port other than 8787 is reported, use that number instead.
EOF

if [ "$RUN_AFTER" = "1" ]; then
  say "Starting Sangala Studio. Press Ctrl-C in this window to stop it."
  say "To run other commands while it is running, open a second Terminal tab with the + at the top."
  echo
  exec python3 "$BRIDGE"
fi
