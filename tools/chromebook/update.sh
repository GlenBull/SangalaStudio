#!/bin/bash
# ==========================================================================
#  Update Sangala Studio to the latest version, on a Chromebook.
#
#  The Sangala Studio icon runs this by itself every time it starts, so nobody
#  has to remember to. It can also be run by hand, in the Terminal, from the
#  Sangala Studio folder:
#
#      bash update.sh
#
#  It updates the three parts that change:
#     SangalaStudio.html   (the page: buttons, tools, fixes)
#     sangala_bridge.py    (the engine that drives the die cutter)
#     Sangala for Snap.xml (the blocks Sangala loads into Snap! )
#  and itself, and setup.sh, so the next run of either follows the newest rules.
#
#  It never leaves the Chromebook half-updated: everything is downloaded and
#  checked first, and if any part fails, nothing is changed.
#
#  The Chromebook counterpart of "Update Sangala Studio.command" on a Mac and
#  "Update SangalaStudio.cmd" on Windows, and it follows the Mac one step for
#  step. The one difference is the download: Crostini's Debian does not always
#  have curl, but setup.sh has already made sure Python 3 is here.
# ==========================================================================

cd "$(dirname "$0")" || exit 1

# --quiet is how the launcher runs this at startup: no window to read, nobody
# waiting. Everything goes to the log instead, so a failed update can still be
# diagnosed.
QUIET=""
[ "${1:-}" = "--quiet" ] && QUIET=1
[ -n "$QUIET" ] && exec >>"$HOME/.sangala-studio-update.log" 2>&1
[ -n "$QUIET" ] && echo "---- $(date)"

BASE="https://raw.githubusercontent.com/maketolearn/SangalaStudio/main"

HTML="SangalaStudio.html"
XML="Sangala for Snap.xml"
BRIDGE="sangala_bridge.py"
SELF="update.sh"
SETUP="setup.sh"

if [ ! -f "$HTML" ] || [ ! -f "$BRIDGE" ]; then
  echo "This updater has to sit in the Sangala Studio folder, beside"
  echo "SangalaStudio.html and sangala_bridge.py."
  exit 1
fi

TMP="$(mktemp -d /tmp/sangala.XXXXXX)" || exit 1
trap 'rm -rf "$TMP"' EXIT

fail() {
  echo
  echo "Update FAILED - $1"
  echo "Your current Sangala Studio was NOT changed, so it still works."
  echo "Check the internet connection and run this again."
  exit 1
}

# One download, bounded: a network that stalls must not hold the program shut.
# A server error raises rather than saving an error page over a good file.
fetch() {
  python3 - "$BASE/$1" "$2" <<'PY'
import sys, urllib.request
url, out = sys.argv[1], sys.argv[2]
try:
    with urllib.request.urlopen(url, timeout=30) as r:
        data = r.read()
except Exception as e:
    sys.stderr.write("%s: %s\n" % (url, e)); sys.exit(1)
open(out, "wb").write(data)
PY
}

echo "Checking for a newer Sangala Studio..."
echo

# ---- 1. Download.
fetch "SangalaStudio.html"            "$TMP/html"   || fail "could not download the page."
fetch "Sangala%20for%20Snap.xml"      "$TMP/xml"    || fail "could not download the blocks file."
fetch "tools/sangala_bridge.py"       "$TMP/bridge" || fail "could not download the engine."
# These two are conveniences: an older copy of either still works, so a missing
# one must not stop the rest of the update.
fetch "tools/chromebook/update.sh"    "$TMP/self"  2>/dev/null
fetch "tools/setup_chromebook.sh"     "$TMP/setup" 2>/dev/null

# ---- 2. Check each download is complete and is the file it claims to be.
grep -q "</html>" "$TMP/html"   || fail "the page downloaded incomplete."
grep -q "SANGALA_VERSION" "$TMP/html" || fail "the page downloaded incomplete."
grep -q "<blocks" "$TMP/xml"    || fail "the blocks file downloaded incomplete."
grep -q "Sangala Studio bridge" "$TMP/bridge" || fail "the engine downloaded incomplete."
if [ "$(wc -c < "$TMP/bridge")" -lt 20000 ]; then fail "the engine downloaded incomplete."; fi

# ---- 2a. Is this updater itself out of date? Replace it and hand over to the
#          new copy with exec - bash reads a script as it runs, so carrying on in
#          a file that has just changed underneath it is not safe.
#          SANGALA_UPDATER_REPLACED stops a loop if the two never match.
if [ -z "${SANGALA_UPDATER_REPLACED:-}" ] && [ -s "$TMP/self" ] \
   && grep -q "Checking for a newer Sangala Studio" "$TMP/self" \
   && ! cmp -s "$TMP/self" "$SELF"; then
  [ -f "$SELF" ] && cp -p "$SELF" "$SELF.bak"
  mv "$TMP/self" "$SELF" || fail "the updater could not replace itself."
  echo "The updater itself was out of date. Starting the new one..."
  echo
  SANGALA_UPDATER_REPLACED=1 exec bash "./$SELF" "$@"
fi

# ---- 3. Is any of it actually new? If not, change nothing at all.
NEW=0
cmp -s "$TMP/html"   "$HTML"   || NEW=1
cmp -s "$TMP/xml"    "$XML"    || NEW=1
cmp -s "$TMP/bridge" "$BRIDGE" || NEW=1

if [ "$NEW" -eq 0 ]; then
  echo "Already up to date - nothing downloaded."
else
  echo "A newer version is available. Installing..."
  [ -f "$HTML" ]   && cp -p "$HTML"   "$HTML.bak"
  [ -f "$XML" ]    && cp -p "$XML"    "$XML.bak"
  [ -f "$BRIDGE" ] && cp -p "$BRIDGE" "$BRIDGE.bak"
  mv "$TMP/html"   "$HTML"   || fail "the page could not be replaced."
  mv "$TMP/xml"    "$XML"    || fail "the blocks file could not be replaced."
  mv "$TMP/bridge" "$BRIDGE" || fail "the engine could not be replaced."
  echo
  echo "Done - Sangala Studio is up to date."
  echo "(The previous version was saved alongside, ending in .bak.)"
fi

# ---- 4. Refresh setup.sh, so running it again installs the newest launcher.
if [ -s "$TMP/setup" ] && grep -q "Sangala Studio - Chromebook setup" "$TMP/setup"; then
  cmp -s "$TMP/setup" "$SETUP" || mv "$TMP/setup" "$SETUP"
fi

echo
exit 0
