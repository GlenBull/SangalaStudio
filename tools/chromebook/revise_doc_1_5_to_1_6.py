"""Sangala Studio on a Chromebook: Ver 1.5 -> Ver 1.6.

The launcher changed (commit c3b95ac): the icon no longer opens a Terminal window. It starts the
part that talks to the die cutter out of sight and opens the page in Chrome. Five passages in 1.5
describe the old behavior, and one of the four opening warnings existed only because of it.

Edited in place - every zip entry is copied and only word/document.xml is rewritten - so the
document's own formatting is untouched. Each replacement must match exactly once or the run aborts
without writing anything.
"""
import os, re, shutil, sys, zipfile

sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
import trackedit          # only for its run-aware paragraph helpers

DIR = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making"
       r"\Sangala Tools\Other Platforms\Chromebook")
SRC = os.path.join(DIR, "Sangala Studio on a Chromebook (Ver 1.5).docx")
DST = os.path.join(DIR, "Sangala Studio on a Chromebook (Ver 1.6).docx")

# (locator - a unique phrase in the paragraph, old text, new text)
EDITS = [
    # 1. the tab warning existed because the program held the window it started in
    ("The Terminal Window Has Tabs",
     "This matters more than it sounds. Once Sangala Studio is running, the window it started in "
     "belongs to the program, and anything typed there goes to the program rather than to Linux. "
     "Without a second tab there is no way to run a command except by stopping the program, which "
     "then has to be started again.",
     "This is worth knowing if a second command is ever needed while something else is running, "
     "though in ordinary use the Terminal is finished with once the setup script has run."),
    # 2. Step 4: the script no longer holds the window
    ("The script ends by starting Sangala Studio",
     "The script ends by starting Sangala Studio in that same Terminal window. Leave it open while "
     "working; pressing Ctrl-C in it stops the program.",
     "The script ends by starting Sangala Studio, which opens in Chrome. The Terminal is not held "
     "by it and can be closed."),
    ("That window now belongs to the program",
     "That window now belongs to the program. To run any further command, open a second tab with "
     "the plus sign at the top of the Terminal window, as described at the start. The program keeps "
     "running in the first tab.",
     "The part of Sangala Studio that talks to the die cutter keeps running out of sight, so nothing "
     "has to be left open and nothing has to be stopped by hand. It ends when the Chromebook's Linux "
     "environment is shut down."),
    # 3. Step 5: there is no window printing an address any more
    ("The program opens its own page in the Chrome browser",
     "The program opens its own page in the Chrome browser. If that does not happen, the address is "
     "printed in the window the program is running in, and can be opened there or typed into Chrome:",
     "The program opens its own page in the Chrome browser. If that does not happen, type the "
     "address into Chrome:"),
    # 4. the launcher section, which described the small window
    ("The program opens a small window showing the address",
     "The program opens a small window showing the address it is serving, and opens the design page "
     "in Chrome. Pressing Ctrl-C in that window stops the program, and so does closing it. Starting "
     "it a second time while it is already running does no harm: it reopens the page of the copy "
     "already running rather than starting another.",
     "The design page opens in Chrome, and nothing else appears: the part that talks to the die "
     "cutter runs out of sight. Starting it a second time while it is already running does no harm "
     "- it reopens the page of the copy already running rather than starting another. If it cannot "
     "start, a window opens showing the reason, which is also kept in a file named "
     ".sangala-studio.log in Linux files."),
    # 5. troubleshooting: the address is no longer printed in a Terminal
    ("Could Not Reach the Program",
     "Could Not Reach the Program. The page is pointing at the wrong port. Look at the Terminal for "
     "the address the program printed when it started, and use that port number.",
     "Could Not Reach the Program. The page is pointing at the wrong port. The port is recorded in "
     ".sangala-studio.log in Linux files; use the number given there."),
]

z = zipfile.ZipFile(SRC)
doc = z.read("word/document.xml").decode("utf-8")

ed = trackedit.Editor(doc)
for locator, old, new in EDITS:
    ed.replace(locator, old, new)          # raises unless the locator and target each match once
    print("revised: %s" % locator[:52])
doc = ed.doc

# The revisions are ACCEPTED here rather than left as marks: this is a rewrite of instructions that
# no longer describe the program, not a suggestion for the author to weigh.
doc = re.sub(r'<w:del [^>]*>.*?</w:del>', '', doc, flags=re.S)
doc = re.sub(r'<w:ins [^>]*>(.*?)</w:ins>', r'\1', doc, flags=re.S)

with zipfile.ZipFile(DST, "x", zipfile.ZIP_DEFLATED) as w:
    for item in z.infolist():
        w.writestr(item, doc.encode("utf-8") if item.filename == "word/document.xml"
                   else z.read(item.filename))
print("wrote", DST)
