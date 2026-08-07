"""Sangala Studio on a Chromebook: Ver 1.4 -> Ver 1.5.

Edits the real file. Every paragraph keeps its own XML - styles.xml, numbering.xml, the footer and
the sectPr are never touched - so only the body order and the specific texts named here change.

Every operation asserts what it expected to find. A single mismatch aborts the whole run before
anything is written, so a partial revision cannot reach the disk.
"""

import os
import re
import shutil
import sys
import zipfile

SRC_DIR = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making"
           r"\Sangala Tools\Other Platforms\Chromebook")
SRC = os.path.join(SRC_DIR, "Sangala Studio on a Chromebook (Ver 1.4).docx")
OUT = os.path.join(SRC_DIR, "Sangala Studio on a Chromebook (Ver 1.5).docx")

RPR = ('<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>%s'
       '<w:color w:val="000000"/><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr>')
CODE_RPR = ('<w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:color w:val="000000"/>'
            '<w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>')


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def heading(text, page_break=False):
    brk = "<w:pageBreakBefore/>" if page_break else ""
    return ('<w:p><w:pPr><w:keepNext/><w:keepLines/>%s<w:spacing w:before="240" w:after="60"/>'
            '</w:pPr><w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:p>'
            % (brk, RPR % "<w:b/>", esc(text)))


def body(text):
    return ('<w:p><w:pPr><w:spacing w:before="0" w:after="60"/></w:pPr><w:r>%s'
            '<w:t xml:space="preserve">%s</w:t></w:r></w:p>' % (RPR % "", esc(text)))


def item(label, text):
    """An italic label leading a paragraph - the shape the existing bullet-style items use."""
    return ('<w:p><w:pPr><w:spacing w:before="0" w:after="60"/></w:pPr>'
            '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>'
            '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:p>'
            % (RPR % "<w:i/>", esc(label), RPR % "", esc(text)))


def code(text):
    return ('<w:p><w:pPr><w:keepNext/><w:keepLines/><w:ind w:left="720"/>'
            '<w:spacing w:before="60" w:after="120"/></w:pPr><w:r>%s'
            '<w:t xml:space="preserve">%s</w:t></w:r></w:p>' % (CODE_RPR, esc(text)))


# ---------------------------------------------------------------- read
with zipfile.ZipFile(SRC) as z:
    names = z.namelist()
    blobs = {n: z.read(n) for n in names}
doc = blobs["word/document.xml"].decode("utf8")
head, rest = doc.split("<w:body>", 1)
inner, tail = rest.rsplit("</w:body>", 1)
paras = re.findall(r"<w:p(?:\s[^>]*)?>.*?</w:p>|<w:p\s*/>", inner, re.S)
sect = inner[inner.rindex("</w:p>") + 6:]
assert len(paras) == 56, "expected 56 paragraphs, found %d" % len(paras)

problems = []


def text_of(i):
    return "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", paras[i], re.S))


def retext(i, expect_start, new_runs):
    """Replace a paragraph wholesale, having checked it is the one meant."""
    got = text_of(i)
    if not got.startswith(expect_start):
        problems.append("para %d starts %r, expected %r" % (i, got[:60], expect_start[:60]))
        return
    paras[i] = new_runs


def edit(i, old, new):
    """Replace a phrase inside one paragraph, at run level."""
    if old not in paras[i]:
        problems.append("para %d does not contain %r" % (i, old[:70]))
        return
    paras[i] = paras[i].replace(old, new, 1)


# ---------------------------------------------------------------- 1. the opening claim
# The script path has NOT been run end to end; the hand-typed sequence has. Say which is which,
# rather than letting the document's authority ("every step below is the one that worked") carry
# over onto steps nobody has yet performed.
retext(1, "This procedure was carried out end to end", body(
    "Sangala Studio runs on a Chromebook through the Linux environment that ChromeOS provides. "
    "Three things must be done in ChromeOS first, because no script can do them, and a setup "
    "script then does everything else. The sequence that script automates was carried out by "
    "hand, end to end, on 5 August 2026, on a Chromebook running ChromeOS version 143 with a "
    "Silhouette Portrait 2, and Sangala Studio connected to the die cutter. That hand-typed "
    "sequence is preserved in the appendix, both as a record of what was proven and as a way to "
    "proceed if the script cannot."))

# ---------------------------------------------------------------- 2. only one command to type now
retext(5, "Type the Commands Rather than Pasting Them.", item(
    "Type the One Command Rather than Pasting It. ",
    "The ChromeOS Terminal inserts hidden characters into pasted text, producing errors such as "
    "command not found on a command that looks correct. Only one command has to be typed, and the "
    "setup script corrects the Terminal's handling of pasted text once it has run, so anything "
    "sent later can be pasted. Where a filename is long, type the first few characters and press "
    "the Tab key, which completes it without error. Pasting into the Terminal is Ctrl-Shift-V "
    "rather than Ctrl-V."))

# ---------------------------------------------------------------- 3. the file listing gained two
retext(27, "The listing should include", body(
    "The listing should include setup.sh, sangala_bridge.py, SangalaStudio.html, "
    "99-silhouette.rules, sangala-studio.png, Calibration Card.svg, Sangala for Snap.xml, "
    "Read Me First.txt and a folder named assets."))

# ---------------------------------------------------------------- 4. the new Step 4
STEP4 = [
    heading("Step 4. Run the Setup Script"),
    body("Everything that remains is done by one command. In the Terminal, type:"),
    code("bash setup.sh"),
    body("The script installs the USB library and the permission rule, confirms that the die "
         "cutter can be opened and reports which model it found, adds Sangala Studio to the "
         "ChromeOS launcher, and starts the program. The password it asks for is the one used to "
         "sign in to the Chromebook."),
    body("It is safe to run as many times as necessary. Every step checks before it acts, and the "
         "script stops at the first thing that is wrong with a sentence saying what to do about "
         "it. If a step is corrected, running the script again continues from there."),
]

# ---------------------------------------------------------------- 5. Step 7 becomes Step 5
edit(44, ">Step 7. Open the Page and Connect<", ">Step 5. Open the Page and Connect<")
retext(45, "In the Chrome browser, go to:", body(
    "The program opens its own page in the Chrome browser. If that does not happen, the address "
    "is printed in the window the program is running in, and can be opened there or typed into "
    "Chrome:"))

# ---------------------------------------------------------------- 6. what happens from then on
AFTER = [
    heading("After the First Time: Starting from the Launcher"),
    body("The Terminal is not needed again. The setup script adds Sangala Studio to the ChromeOS "
         "launcher, where it behaves like any other application on the Chromebook."),
    body("Open the launcher with the circle at the bottom-left of the screen, search for Sangala, "
         "and click Sangala Studio. The first time, the entry can take a few seconds to appear."),
    body("The program opens a small window showing the address it is serving, and opens the "
         "design page in Chrome. Pressing Ctrl-C in that window stops the program, and so does "
         "closing it. Starting it a second time while it is already running does no harm: it "
         "reopens the page of the copy already running rather than starting another."),
]

# ---------------------------------------------------------------- 7. the stale Windows advice
# The bridge used to answer a permission failure with "close Silhouette Studio", which is Windows
# advice, and Ver 1.4 warned the reader to disregard it. The program was corrected on 7 August, so
# the warning now describes something that no longer happens.
retext(53, "Access Denied, or Insufficient Permissions.", item(
    "Access Denied, or Insufficient Permissions. ",
    "The permission rule was not installed, or has not taken effect. On Linux an ordinary user "
    "cannot open a USB device unless a rule names it. Run bash setup.sh again, then unplug the "
    "die cutter and plug it back in."))

LAUNCHER_TROUBLE = [
    item("Sangala Studio Is Absent from the Launcher. ",
         "The entry can take a few seconds to appear the first time. If it is still missing, "
         "bash setup.sh installs it again and starts the program directly in the meantime."),
]

# ---------------------------------------------------------------- 7b. small corrections of fact
# "Leave that Terminal window open" followed the python3 command in Ver 1.4. It now follows the
# script, so name what the script does rather than leaving "that window" to be inferred.
edit(42, ">Leave that Terminal window open while working. Pressing Ctrl-C in it stops the program.<",
     ">The script ends by starting Sangala Studio in that same Terminal window. Leave it open while "
     "working; pressing Ctrl-C in it stops the program.<")

# The model list was never quite right and the document is open anyway: the Portrait 3 is the
# FALLBACK rather than a recognised identifier, and the bridge knows every Cameo, not only the Cameo 2.
retext(50, "The Machine Is Named Wrongly.", item(
    "The Machine Is Named Wrongly. ",
    "Sangala Studio knows the Portrait 4 and the Cameo models by their identifiers, and anything it "
    "does not know falls back to Portrait 3 settings. A Portrait 2 therefore reports as a "
    "Portrait 3. The cutting width is the same, so this does not affect the result."))

# ---------------------------------------------------------------- 8. the appendix
APPENDIX_HEAD = [
    heading("Appendix. Installing by Hand", page_break=True),
    body("This is the sequence the setup script performs, and it is the sequence that was carried "
         "out by hand on 5 August 2026. It is recorded here for two reasons: it is the path that "
         "has been proven on a real Chromebook, and it is what to fall back on if the script "
         "cannot run. It replaces Step 4 above; Steps 1 to 3 are the same either way."),
]
# The three headings lose their "Step N" numbers, which now belong to the steps above.
edit(28, ">Step 4. Install the USB Library<", ">Install the USB Library<")
edit(32, ">Step 5. Install the Permission Rule<", ">Install the Permission Rule<")
edit(40, ">Step 6. Start Sangala Studio<", ">Start Sangala Studio<")

# Installing by hand does NOT add the launcher entry, which is the one thing the script does that
# has no hand equivalent here. Say so, rather than letting the reader look for an icon that the
# path they followed never created.
APPENDIX_TAIL = [
    body("Installed this way, Sangala Studio does not appear in the ChromeOS launcher: the entry is "
         "something the setup script adds. The command above starts the program, and has to be "
         "typed each time. Running bash setup.sh afterward installs the launcher entry without "
         "repeating any of the work above, since every step checks before it acts."),
]

# ---------------------------------------------------------------- 9. restart each Step's list at 1
# Seen only by rendering the pages: the items ran 1-2 under Step 1, 3-5 under Step 2 and 6-9 under
# Step 3, because all three lists share one numId and therefore one counter. Under headings that are
# themselves numbered "Step N", a sub-list beginning at 6 reads as a fault.
#
# A NEW numId ALONE DOES NOT RESTART A LIST - it inherits the abstract definition's counter. Each
# needs an explicit lvlOverride/startOverride. The XML looks right either way, so this is verified
# afterwards through Word's own ListFormat.ListString rather than by reading the file.
numbering = blobs["word/numbering.xml"].decode("utf8")
OVERRIDE = ('<w:num w:numId="%d"><w:abstractNumId w:val="0"/>'
            '<w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride></w:num>')
assert '<w:num w:numId="1">' in numbering, "numbering.xml is not the shape expected"
numbering = numbering.replace("</w:numbering>", (OVERRIDE % 2) + (OVERRIDE % 3) + "</w:numbering>")

for idx, num in ((14, 2), (15, 2), (16, 2),                  # Step 2's three actions
                 (21, 3), (22, 3), (23, 3), (24, 3)):        # Step 3's four actions
    old = '<w:numId w:val="1"/>'
    if old not in paras[idx]:
        problems.append("para %d has no numId to retarget" % idx)
        continue
    paras[idx] = paras[idx].replace(old, '<w:numId w:val="%d"/>' % num, 1)

# ---------------------------------------------------------------- assemble
if problems:
    print("ABORTED - nothing written:")
    for p in problems:
        print("   " + p)
    sys.exit(1)

new = []
new += paras[0:28]              # title, opening, Before Starting, Steps 1-3
new += STEP4                    # the new Step 4
new += paras[42:44]             # "Leave that Terminal window open", "That window now belongs..."
new += paras[44:49]             # Step 5 (was 7): open the page and connect
new += AFTER                    # After the First Time
new += paras[49:53]             # Two Things That Look Like Faults; If Something Goes Wrong + first item
new += paras[53:56]             # the three trouble items (53 already rewritten)
new += LAUNCHER_TROUBLE
new += APPENDIX_HEAD
new += paras[28:42]             # the hand-typed sequence, headings renumbered
new += APPENDIX_TAIL            # what installing by hand does NOT give you

# Nothing may be dropped or duplicated by the reordering: every original paragraph must appear in
# the result exactly once. Counting totals would not catch a slice that repeated one and lost another.
added = len(STEP4) + len(AFTER) + len(LAUNCHER_TROUBLE) + len(APPENDIX_HEAD) + len(APPENDIX_TAIL)
missing = [i for i, p in enumerate(paras) if new.count(p) != 1]
if missing:
    sys.exit("ABORTED - these original paragraphs are lost or duplicated: %s" % missing)
assert len(new) == len(paras) + added, \
    "expected %d paragraphs, assembled %d" % (len(paras) + added, len(new))

out_doc = head + "<w:body>" + "".join(new) + sect + "</w:body>" + tail

# Rebuild by copying every entry and replacing only word/document.xml, so images, styles and the
# footer stay byte-identical. (No unzip/rezip: there is no zip command on this machine anyway.)
if os.path.exists(OUT):
    sys.exit("refusing to overwrite an existing %s" % os.path.basename(OUT))
with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
    for info in zin.infolist():
        if info.filename == "word/document.xml":
            data = out_doc.encode("utf8")
        elif info.filename == "word/numbering.xml":
            data = numbering.encode("utf8")
        else:
            data = zin.read(info.filename)
        zout.writestr(info, data)

print("wrote %s" % OUT)
print("  paragraphs %d -> %d" % (len(paras), len(new)))
