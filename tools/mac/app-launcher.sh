#!/bin/bash
# The script inside "Sangala Studio.app" on macOS — the file Platypus installs as
# Contents/Resources/script. It is tracked here so the app's behavior can be reviewed and
# revised as a diff; the .app itself is built on a Mac and is not in this repository.
#
# Platypus keeps THIS script's process alive as the app (Dock icon + Quit), and terminates it
# when the app quits, so the trap below stops the Python bridge instead of orphaning it.
#
# THE SPLIT THAT MAKES UPDATING POSSIBLE. The app bundle is signed and notarized, so nothing may
# write inside it, ever — a changed file invalidates the signature and macOS then refuses to run
# the app. So the bundle carries a read-only TEMPLATE of the program, and the copy that actually
# runs lives in the user's own Documents folder, where "Update Sangala Studio.command" may rewrite
# it without an administrator password.

PY="/usr/bin/python3"
WORKDIR="$HOME/Documents/Sangala Studio"
BRIDGE="$WORKDIR/sangala_bridge.py"

# The frozen template inside the app bundle. Platypus puts bundled files in the app's Resources
# folder, which it exposes as this script's working directory.
TEMPLATE="$(dirname "$0")/working"

# Copy across anything the working folder does not already have. -n never overwrites, so a page
# the updater has already replaced with a newer one is left alone, while a file the working folder
# has never held — the updater itself, on a Mac that installed an earlier version — arrives at the
# next launch. A first-run-only copy could not deliver that.
mkdir -p "$WORKDIR"
cp -Rn "$TEMPLATE/." "$WORKDIR/" 2>/dev/null

# A .command is double-clicked, so it has to be executable. The bit survives the bundle, but not
# every route a file can take into the folder, and it costs nothing to be sure.
for cmd in "$WORKDIR"/*.command; do
  [ -f "$cmd" ] && chmod +x "$cmd"
done

# FIRST RUN ONLY: Desktop alias with the buffalo icon.
DESKTOP_ALIAS="$HOME/Desktop/Sangala Studio"
if [ ! -e "$DESKTOP_ALIAS" ]; then
  APP_PATH="$(cd "$(dirname "$0")/../.." && pwd)"
  osascript >/dev/null 2>&1 <<OSA
tell application "Finder"
    make alias file to POSIX file "$APP_PATH" at desktop
    set name of result to "Sangala Studio"
end tell
OSA
fi

cd "$WORKDIR" || exit 1

# First run: install the USB library if missing.
if ! "$PY" -c "import usb.core" >/dev/null 2>&1; then
  "$PY" -m pip install --user pyusb libusb-package >/dev/null 2>&1 \
    || "$PY" -m pip install --user --break-system-packages pyusb libusb-package >/dev/null 2>&1
fi

# Start the bridge as a CHILD (not exec), record its PID.
"$PY" "$BRIDGE" &
BRIDGE_PID=$!

# When Platypus quits the app, this script gets a termination signal. Trap it and kill the bridge
# so nothing is left running on the port.
trap 'kill $BRIDGE_PID 2>/dev/null; exit 0' TERM INT EXIT

# Stay alive as long as the bridge runs (this keeps the Dock icon present).
wait $BRIDGE_PID
