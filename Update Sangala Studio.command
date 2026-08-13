#!/bin/bash
# ==========================================================================
#  Update Sangala Studio to the latest version, on a Mac.
#  Double-click this file. No admin password, no install, no git needed.
#
#  This updates all three parts of the program in one step:
#     SangalaStudio.html      (the page: buttons, tools, fixes)
#     tools/sangala_bridge.py (the engine that drives the die cutter)
#     Sangala for Snap.xml    (the blocks Sangala loads into Snap! )
#  and refreshes the launcher itself, so an ordinary update and a machine-
#  engine update both arrive the same way.
#
#  It never leaves you half-updated: everything is downloaded and checked
#  first, and if any part fails, nothing on your Mac is changed.
#
#  It also puts a "Sangala Studio" icon on your Desktop, so you can start the
#  program without hunting for it.
# ==========================================================================

cd "$(dirname "$0")" || exit 1

# The page and the blocks come from the main line of the project. The Mac
# engine and these two launchers still live on the mac-bridge branch; when
# that branch is merged, BRIDGE_BASE becomes the same address as BASE.
BASE="https://raw.githubusercontent.com/GlenBull/SangalaStudio/main"
BRIDGE_BASE="https://raw.githubusercontent.com/GlenBull/SangalaStudio/mac-bridge"

HTML="SangalaStudio.html"
XML="Sangala for Snap.xml"
BRIDGE="tools/sangala_bridge.py"
LAUNCHER="Sangala Studio.command"

if [ ! -f "$HTML" ]; then
  echo "This updater has to sit in the same folder as SangalaStudio.html."
  echo "Move it there and double-click it again."
  echo
  echo "Press any key to close this window."
  read -r -n 1 -s
  exit 1
fi

# Everything is downloaded into a scratch folder first and only moved into
# place once every piece has arrived and been checked.
TMP="$(mktemp -d /tmp/sangala.XXXXXX)" || exit 1
trap 'rm -rf "$TMP"' EXIT

fail() {
  echo
  echo "Update FAILED - $1"
  echo "Your current Sangala Studio was NOT changed, so it still works."
  echo "Check the internet connection and run this again."
  echo
  echo "Press any key to close this window."
  read -r -n 1 -s
  exit 1
}

echo "Checking for a newer Sangala Studio..."
echo

# ---- 1. Download. curl is built into macOS. -f fails on an error page rather
#         than saving it, which is what stops a web outage from overwriting a
#         good file with a page of HTML apologising.
curl -fsSL "$BASE/$HTML"                        -o "$TMP/html" || fail "could not download the page."
curl -fsSL "$BASE/Sangala%20for%20Snap.xml"     -o "$TMP/xml"  || fail "could not download the blocks file."
curl -fsSL "$BRIDGE_BASE/tools/sangala_bridge.py" -o "$TMP/bridge" || fail "could not download the engine."
# The launcher is a convenience, not a requirement: an older copy still starts
# the program, so a missing one must not stop the rest of the update.
curl -fsSL "$BRIDGE_BASE/Sangala%20Studio.command" -o "$TMP/launcher" 2>/dev/null

# ---- 2. Check each download is complete and is the file it claims to be.
grep -q "</html>" "$TMP/html"   || fail "the page downloaded incomplete."
grep -q "<blocks" "$TMP/xml"    || fail "the blocks file downloaded incomplete."
grep -q "Sangala Studio bridge" "$TMP/bridge" || fail "the engine downloaded incomplete."
if [ "$(wc -c < "$TMP/bridge")" -lt 20000 ]; then fail "the engine downloaded incomplete."; fi

# ---- 3. Is any of it actually new? If not, change nothing at all.
NEW=0
cmp -s "$TMP/html"   "$HTML"   || NEW=1
cmp -s "$TMP/xml"    "$XML"    || NEW=1
cmp -s "$TMP/bridge" "$BRIDGE" || NEW=1

if [ "$NEW" -eq 0 ]; then
  echo "Already up to date - nothing downloaded."
else
  echo "A newer version is available. Installing..."

  # Keep the current copies as backups, then move the new ones into place.
  # Replacing a file the running program opened is safe on a Mac: the copy it
  # is already using stays valid until it stops.
  mkdir -p tools
  [ -f "$HTML" ]   && cp -p "$HTML"   "$HTML.bak"
  [ -f "$XML" ]    && cp -p "$XML"    "$XML.bak"
  [ -f "$BRIDGE" ] && cp -p "$BRIDGE" "$BRIDGE.bak"

  mv "$TMP/html"   "$HTML"   || fail "the page could not be replaced."
  mv "$TMP/xml"    "$XML"    || fail "the blocks file could not be replaced."
  mv "$TMP/bridge" "$BRIDGE" || fail "the engine could not be replaced."

  echo
  echo "Done - Sangala Studio is up to date."
  echo
  echo "  If the program is running, stop it (press Control-C in its Terminal"
  echo "  window, or just close that window) and start it again. Then press"
  echo "  Command-R in the browser to reload the page."
  echo
  echo "  (Your previous version was saved alongside, ending in .bak.)"
fi

# ---- 4. Refresh the launcher, whether or not anything else was new, and make
#         sure it is allowed to run. A copy that arrived by email, Dropbox or a
#         zip file loses that permission; this puts it back.
if [ -s "$TMP/launcher" ] && grep -q "Sangala Studio" "$TMP/launcher"; then
  cmp -s "$TMP/launcher" "$LAUNCHER" || mv "$TMP/launcher" "$LAUNCHER"
fi
[ -f "$LAUNCHER" ] && chmod +x "$LAUNCHER"
chmod +x "$0" 2>/dev/null

# ---- 5. Put a "Sangala Studio" icon on the Desktop pointing at the launcher in
#         THIS folder, so the icon keeps working even if the folder is moved.
#         Pure convenience: if anything goes wrong the update itself is still
#         good, so none of this changes the result.
if [ -f "$LAUNCHER" ]; then
  TARGET="$(pwd)/$LAUNCHER"
  DESKTOP="$HOME/Desktop"
  MADE=0
  if [ -d "$DESKTOP" ]; then
    # A Finder alias is the tidy Mac way and shows the launcher's own icon.
    # macOS may ask once for permission for Terminal to control Finder.
    if osascript >/dev/null 2>&1 <<OSA
tell application "Finder"
  try
    delete (every alias file of desktop whose name is "Sangala Studio")
  end try
  make new alias file at desktop to (POSIX file "$TARGET" as alias) with properties {name:"Sangala Studio"}
end tell
OSA
    then
      MADE=1
    else
      # Permission refused, or Finder is not scriptable here. A plain link does
      # the same job when double-clicked.
      rm -f "$DESKTOP/Sangala Studio" 2>/dev/null
      ln -s "$TARGET" "$DESKTOP/Sangala Studio" 2>/dev/null && MADE=1
    fi
  fi
  if [ "$MADE" -eq 1 ]; then
    echo
    echo "  A \"Sangala Studio\" icon is on your Desktop, ready to use."
  fi
fi

echo
echo "Press any key to close this window."
read -r -n 1 -s
exit 0
