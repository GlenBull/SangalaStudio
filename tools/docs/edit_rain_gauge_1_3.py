"""Rain Gauge (Ver 1.2) -> (Ver 1.3): the MakerPort-MicroBlocks collaboration.

Glen, 2026-09-19: the MakerPort was expressly designed to run MicroBlocks, in a long
collaboration with John Maloney, the developer of MicroBlocks. Ver 1.2 treated MicroBlocks as
one open-source project among others and its developers as a prospect to contact. Four
passages change, in place, and nothing else: the opening of "What the MakerPort Can Read",
the lead-in of the collaborators section, the MicroBlocks entry in that section, and the
MicroBlocks row of Table 2.
"""

import os, re, shutil, zipfile
import xml.dom.minidom

W = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\Weather Station"
SRC = os.path.join(W, "Rain Gauge (Ver 1.2).docx")
OUT = os.path.join(W, "Rain Gauge (Ver 1.3).docx")
ARCHIVE = os.path.join(W, "Archive")

z = zipfile.ZipFile(SRC)
names = z.namelist()
parts = {n: z.read(n) for n in names}
z.close()
dx = parts["word/document.xml"].decode("utf8")


def rep(old, new, count=1):
    global dx
    assert dx.count(old) == count, (old[:60], dx.count(old))
    dx = dx.replace(old, new)


# 1. What the MakerPort Can Read - the run before the italic "!" of Snap!
rep("The MakerPort is a classroom microcontroller from 1010 Technologies, programmed in "
    "MicroBlocks, Scratch or Snap",
    "The MakerPort is a classroom microcontroller from 1010 Technologies. It was designed "
    "expressly to run MicroBlocks, in a long collaboration with John Maloney, the developer of "
    "the language, that predates this project; it can also be programmed in Scratch or Snap")

# 2. The collaborators section's lead-in
rep("MakerPort station, and how contact is made.",
    "MakerPort station, and how contact is made. One of these relationships already exists: "
    "the MakerPort itself is the product of a long collaboration with John Maloney, the "
    "developer of MicroBlocks, so the author of the language is a partner in the project "
    "rather than a prospect.")

# 3. The MicroBlocks entry
rep(">MicroBlocks. </w:t>", ">MicroBlocks and John Maloney. </w:t>")
rep("The MakerPort is programmed in MicroBlocks, whose developers maintain the pin and sensor "
    "libraries the gauge will use (MicroBlocks, n.d.). Fit: a rain gauge library, or a weather "
    "station example, contributed back to MicroBlocks would reach every school using the "
    "language. Contact: the MicroBlocks community forum.",
    "John Maloney, the developer of MicroBlocks, is already a collaborator: the MakerPort was "
    "designed expressly to run MicroBlocks, and the board and the language were brought "
    "together through a long working relationship with him. The pin and sensor libraries the "
    "gauge will use are his (MicroBlocks, n.d.). Fit: a rain gauge library, or a weather station "
    "example, contributed back to MicroBlocks would reach every school using the language, and "
    "the channel for doing so is already open. Contact: through the existing collaboration.")

# 4. The MicroBlocks row of Table 2
rep(">Open-source project</w:t>", ">John Maloney; existing collaborator</w:t>")
rep(">Community forum</w:t>", ">The existing collaboration</w:t>")

parts["word/document.xml"] = dx.encode("utf8")
xml.dom.minidom.parseString(parts["word/document.xml"])
assert not os.path.exists(OUT), OUT
with zipfile.ZipFile(OUT, "x", zipfile.ZIP_DEFLATED) as zo:
    zo.writestr("[Content_Types].xml", parts["[Content_Types].xml"])
    for n in names:
        if n != "[Content_Types].xml":
            zo.writestr(n, parts[n])
os.makedirs(ARCHIVE, exist_ok=True)
shutil.move(SRC, os.path.join(ARCHIVE, os.path.basename(SRC)))
print(OUT)
