"""The three Sangala repositories moved from GlenBull to the maketolearn organization (2026-09-23).

Makes the next version of each document that names the old address, changing only the account
name inside word/document.xml. Every other part of the package is copied byte for byte, in its
original order, so the edit is in place in every sense but the filename. Opens the new file with
mode "x", so it refuses to overwrite a version that already exists.

    set PYTHONUTF8=1
    python tools\\docs\\edit_maketolearn_address.py
"""
import os
import zipfile

DB = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\Sangala Tools"
CP = r"D:\Code Projects"

# (folder, old name, new name, how many occurrences the old version holds)
JOBS = [
    (CP + r"\Silhouette Tools\Documents", "Tech Manual (Ver 4.1).docx", "Tech Manual (Ver 4.2).docx", 2),
    (CP + r"\Mosaic\Documents", "Tech Manual (Ver 1.0).docx", "Tech Manual (Ver 1.1).docx", 1),
    (CP + r"\Block Tools\Documents", "Tech Manual (Ver 1.6).docx", "Tech Manual (Ver 1.7).docx", 1),
    (DB, "Shared Repository (Ver 1.0).docx", "Shared Repository (Ver 1.1).docx", 5),
]

OLD, NEW = b"GlenBull/Sangala", b"maketolearn/Sangala"


def edit(folder, old, new, expected):
    src, dst = os.path.join(folder, old), os.path.join(folder, new)
    with zipfile.ZipFile(src) as zin, open(dst, "xb") as f, zipfile.ZipFile(f, "w") as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "word/document.xml":
                n = data.count(OLD)
                if n != expected:
                    raise SystemExit(f"{src}: found {n} occurrences, expected {expected}")
                data = data.replace(OLD, NEW)
            elif OLD in data:
                raise SystemExit(f"{src}: old address also in {info.filename}")
            zout.writestr(info, data, compress_type=info.compress_type)
    print("wrote", dst)


if __name__ == "__main__":
    for job in JOBS:
        edit(*job)
