#!/bin/bash
# ==========================================================================
#  Sangala Studio - start the program on a Mac.
#
#  Double-click this file. A Terminal window opens and stays open while the
#  program runs, and your browser opens the design page by itself. That
#  Terminal window IS the program: leave it alone, and close it (or press
#  Control-C in it) when you are finished.
#
#  This is the Mac counterpart of SangalaStudio.exe on Windows. It starts
#  tools/sangala_bridge.py, which serves the page and drives the die cutter
#  over USB.
#
#  The very first time it runs it installs one small Python library (pyusb,
#  the USB library). That needs the internet once; after that it starts
#  straight away and works offline.
# ==========================================================================

# Terminal starts a double-clicked script in your home folder, so move to the
# folder this file is sitting in.
cd "$(dirname "$0")" || exit 1

# The program's own folder is wherever SangalaStudio.html lives: normally right
# here beside this file, but tolerate this file having been put in tools/.
if [ -f "SangalaStudio.html" ]; then
  HOME_DIR="$(pwd)"
elif [ -f "../SangalaStudio.html" ]; then
  cd ..
  HOME_DIR="$(pwd)"
else
  echo "Sangala Studio was not found."
  echo
  echo "This launcher has to sit in the same folder as SangalaStudio.html."
  echo "Move it there and double-click it again."
  echo
  echo "Press any key to close this window."
  read -r -n 1 -s
  exit 1
fi

BRIDGE="$HOME_DIR/tools/sangala_bridge.py"
if [ ! -f "$BRIDGE" ]; then
  echo "The engine file is missing: tools/sangala_bridge.py"
  echo "Run \"Update Sangala Studio.command\" to fetch it, then try again."
  echo
  echo "Press any key to close this window."
  read -r -n 1 -s
  exit 1
fi

# ---- 1. Python. Every Mac can run it, but on a machine that has never done any
#         development macOS asks to install the developer tools the first time.
PY="$(command -v python3)"
if [ -z "$PY" ]; then
  echo "Python is not installed yet."
  echo
  echo "macOS will offer to install it: a window titled \"The python3 command"
  echo "requires the command line developer tools\" appears when you run"
  echo "python3. Click Install, wait for it to finish, then double-click this"
  echo "launcher again."
  echo
  echo "Press any key to close this window."
  read -r -n 1 -s
  exit 1
fi

# ---- 2. The USB library. Checked every time because the check is instant; the
#         install below happens only once, on the first run.
if ! "$PY" -c "import usb.core" >/dev/null 2>&1; then
  echo "First run: installing the USB library (this needs the internet, once)..."
  echo
  # --user keeps it in Moses's own account - no admin password, nothing
  # system-wide. Newer Pythons refuse that without the second flag, so try the
  # plain form first and fall back rather than asking anyone to know which.
  "$PY" -m pip install --user pyusb libusb-package >/dev/null 2>&1 \
    || "$PY" -m pip install --user --break-system-packages pyusb libusb-package >/dev/null 2>&1
  if ! "$PY" -c "import usb.core" >/dev/null 2>&1; then
    echo "The USB library could not be installed automatically."
    echo
    echo "Copy this line, paste it into Terminal, and press Return:"
    echo
    echo "    python3 -m pip install --user pyusb libusb-package"
    echo
    echo "Then double-click this launcher again."
    echo
    echo "Press any key to close this window."
    read -r -n 1 -s
    exit 1
  fi
  echo "Installed."
  echo
fi

# ---- 3. Start the program. It opens the browser page itself.
exec "$PY" "$BRIDGE"
