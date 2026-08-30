"""Is the Dropbox Sangala Tools folder complete and current for all three applications?

That folder, not the repository, is what Jo, Moses and the students install from. A push that never
reaches it is a change nobody outside this machine can run. Run this after ANY commit or update to
any of the three applications.

    python sangala_publish.py            report only; exit code 1 if anything is stale
    python sangala_publish.py --publish  copy what is stale, keeping the superseded file as .bak

WHAT IT CHECKS, and why each one is here rather than assumed:
  * the page, by hash and by its own version marker - Mosaic's marker is spelled
    SANGALA_MOSAIC_VERSION, not SANGALA_VERSION, so asking every application the same question
    reports Mosaic as unmarked;
  * the exe, by HASH - Studio's exe was byte-identical across three locations while the pages
    differed by thirteen releases, so a version number does not answer this;
  * the helper .cmd scripts, comparing CONTENT with line endings normalized - the Blocks scripts
    differ only in CRLF and are not stale;
  * the Studio zip, which is a second delivery point beside the program folder and can hold a
    different version from it;
  * for Blocks, EVERY LDRAW FILE THE PARTS LIST ACTUALLY NEEDS. The updater deliberately never
    touches LDraw\\, so the parts library does not travel with the page and the exe. On 29 August
    the published folder held 26 of the 74 parts and nothing said so.
"""
import os, re, sys, shutil, hashlib, zipfile

DROPBOX = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making"
           r"\Sangala Tools")
CODE = r"D:\Code Projects"

APPS = [
    {
        "name": "Studio",
        "repo": os.path.join(CODE, "Silhouette Tools"),
        "dest": os.path.join(DROPBOX, "Sangala Studio Files", "Sangala Studio (Program)"),
        "page": "SangalaStudio.html",
        "exe": "SangalaStudio.exe",
        "marker": "SANGALA_VERSION",
        "cmds": ["Update SangalaStudio.cmd", "Create Desktop Shortcut.cmd"],
        # the zip beside the program folder: same page and exe, wrapped for a one-file download
        "zip_dir": os.path.join(DROPBOX, "Sangala Studio Files"),
        "zip_glob": "Sangala Studio (Ver ",
        "zip_inner": "Sangala Studio/",
    },
    {
        "name": "Mosaic",
        "repo": os.path.join(CODE, "Mosaic"),
        "dest": os.path.join(DROPBOX, "Sangala Mosaic Files"),
        "page": "SangalaMosaic.html",
        "exe": "SangalaMosaic.exe",
        "marker": "SANGALA_MOSAIC_VERSION",
        "cmds": ["Update SangalaMosaic.cmd", "Create Desktop Shortcut.cmd"],
    },
    {
        "name": "Blocks",
        "repo": os.path.join(CODE, "Block Tools"),
        "dest": os.path.join(DROPBOX, "Sangala Blocks Files"),
        "page": "SangalaBlockDesigner.html",
        "exe": "SangalaBlockDesigner.exe",
        "marker": "SANGALA_VERSION",
        "cmds": ["Update SangalaBlocks.cmd", "Create Desktop Shortcut.cmd"],
        "ldraw": True,
        # THE DOWNLOAD, built from git ls-files over exactly these paths. Source, tools, Documents
        # and CLAUDE.md are not here on purpose: a student never needs them.
        "zip_dir": os.path.join(DROPBOX, "Sangala Blocks Files"),
        "zip_glob": "Sangala Blocks (Ver ",
        "zip_inner": "Sangala Blocks/",
        "zip_build": ["SangalaBlockDesigner.exe", "SangalaBlockDesigner.html", "Crane.ico",
                      "Create Desktop Shortcut.cmd", "Update SangalaBlocks.cmd", "LICENSE",
                      "LDraw", "LDView", "Projects"],
    },
]

PARTS_CHECK = os.path.join(CODE, "Block Tools", "tools", "check_parts.py")


def sha(path):
    if not os.path.isfile(path):
        return None
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:12]


def text_sha(path):
    """Hash with line endings normalized, so CRLF against LF is not reported as a difference."""
    if not os.path.isfile(path):
        return None
    return hashlib.sha256(open(path, "rb").read().replace(b"\r\n", b"\n")).hexdigest()[:12]


def marker_of(path, key):
    if not os.path.isfile(path):
        return "(absent)"
    head = open(path, encoding="utf-8", errors="replace").read(4000)
    m = re.search(key + r":\s*(\S+)", head)
    return m.group(1) if m else "(no marker)"


def place(src, dst, publish, out, marker=None):
    """Copy src over dst, moving the superseded file into Archive beside it.

    NOT a .bak alongside, which is what this did first. Glen, 2026-08-30: the folder already holds
    more than a new user can sort out, and a program folder wearing two spare copies of itself is
    the clutter, not the safety net. Archive is where every other Sangala folder keeps what it has
    superseded, and the version it carried goes in its name so the copy can be identified."""
    if not publish:
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.isfile(dst):
        arch = os.path.join(os.path.dirname(dst), "Archive")
        os.makedirs(arch, exist_ok=True)
        stem, ext = os.path.splitext(os.path.basename(dst))
        was = marker_of(dst, marker) if marker else None
        tag = " (%s)" % was if was and was[0].isdigit() else ""
        shutil.move(dst, os.path.join(arch, stem + tag + ext))
    shutil.copy2(src, dst)
    out.append("      copied " + os.path.basename(dst))


def stamp_readme(app, publish, out):
    """Keep the version inside Read Me First.txt true.

    Studio's has said 2026-08-10.191 since the day it was written, while that folder now holds .206
    - a number typed into a file goes stale the moment the file beside it changes. The publish is
    the one moment both are known, so it is written here rather than maintained by hand."""
    path = os.path.join(app["dest"], "Read Me First.txt")
    if not os.path.isfile(path):
        return True
    ver = marker_of(os.path.join(app["repo"], app["page"]), app["marker"])
    text = open(path, encoding="utf-8").read()
    fixed = re.sub(r"\b20\d\d-\d\d-\d\d\.\d+\b", ver, text)
    # AND THE NAME OF THE DOWNLOAD, which carries the release number rather than the date. Stamping
    # only the date left the Blocks Read Me telling a user to fetch "Sangala Blocks (Ver 202).zip"
    # on the day 203 replaced it - a file that was no longer in the folder.
    if app.get("zip_glob"):
        fixed = re.sub(re.escape(app["zip_glob"]) + r"\d+\)\.zip",
                       "%s%s).zip" % (app["zip_glob"], ver.split(".")[-1]), fixed)
    if fixed == text:
        return True
    out.append("   %-11s %-44s %s" % ("read me", "version inside it", "STALE"))
    if publish:
        open(path, "w", encoding="utf-8", newline="").write(fixed)
        out.append("      stamped Read Me First.txt with " + ver)
        return True
    return False


# ---- the LDraw files the Blocks parts list actually needs ---------------------------------------
def ldraw_closure():
    """Every .dat the parts list reaches, following subfile references and ~Moved to redirects.
    Returns paths relative to the repo's LDraw folder, or None if the checker cannot be loaded."""
    if not os.path.isfile(PARTS_CHECK):
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_parts", PARTS_CHECK)
    cp = importlib.util.module_from_spec(spec)
    sys.argv = [PARTS_CHECK, "--none--"]      # keep its main() off the spreadsheet
    spec.loader.exec_module(cp)
    root = os.path.join(CODE, "Block Tools", "LDraw", "ldraw")
    cp.LDRAW = root
    cp._found.clear()
    need, seen = set(), set()

    def close(name, depth=0):
        key = name.strip().replace("\\", "/").lower()
        if key in seen or depth > 24:
            return
        seen.add(key)
        p = cp.find(name)
        if not p:
            return
        need.add(os.path.relpath(p, root))
        for line in open(p, encoding="utf-8", errors="replace"):
            f = line.split()
            if len(f) >= 15 and f[0] == "1":
                close(" ".join(f[14:]), depth + 1)

    def want(pid):
        name, real, err = cp.declared(pid)
        # THE REDIRECT STUB COUNTS TOO. 4032.dat holds nothing but "~Moved to 4032a", and the
        # application asks for the number the student typed BEFORE it can learn where it went - so
        # shipping only the target leaves the lookup failing at its first step. Six parts were
        # reported present on that mistake.
        close(pid + ".dat")
        if not err and real != pid:
            close(real + ".dat")

    for listed, pid in cp.sheet_parts():
        want(pid)
    # AND EVERY PART THE SHIPPED DESIGNS USE. The parts list is what a student can CHOOSE; a design
    # travelling beside it may be built from parts that were never on that list. The crane uses
    # 43712, 14716, 2453b and 4073 - four parts the spreadsheet does not name - and on 30 August it
    # opened on a freshly installed laptop with its wings drawn as flat slabs, because this check
    # had been built from the spreadsheet alone and reported the folder complete.
    for pid in sorted(design_parts()):
        want(pid)
    return root, sorted(need)


def design_parts():
    """Every part number named by a design, library or kit that ships in either Projects folder."""
    import json
    ids = set()
    roots = [os.path.join(a["dest"], "Projects") for a in APPS if a.get("ldraw")]
    roots += [os.path.join(a["repo"], "Projects") for a in APPS if a.get("ldraw")]
    for r in roots:
        if not os.path.isdir(r):
            continue
        for dirpath, dirnames, filenames in os.walk(r):
            for fn in filenames:
                if not fn.lower().endswith((".block", ".library", ".kit", ".parts")):
                    continue
                try:
                    d = json.load(open(os.path.join(dirpath, fn), encoding="utf-8"))
                except Exception:
                    continue
                for key in ("bricks", "parts", "libParts"):
                    for item in (d.get(key) or []):
                        if isinstance(item, dict) and item.get("id"):
                            ids.add(str(item["id"]))
    return ids


def check_ldraw(app, publish, out):
    got = ldraw_closure()
    if got is None:
        out.append("   LDraw       cannot check - %s is missing" % PARTS_CHECK)
        return False
    root, need = got
    dest_root = os.path.join(app["dest"], "LDraw", "ldraw")
    missing = [r for r in need if not os.path.isfile(os.path.join(dest_root, r))]
    if not missing:
        out.append("   LDraw       all %d files the parts list needs are present" % len(need))
        return True
    out.append("   LDraw       MISSING %d of the %d files the parts list needs" %
               (len(missing), len(need)))
    for r in missing[:6]:
        out.append("                 " + r)
    if len(missing) > 6:
        out.append("                 ... and %d more" % (len(missing) - 6))
    if publish:
        n = 0
        for r in missing:
            src, dst = os.path.join(root, r), os.path.join(dest_root, r)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            n += 1
        out.append("      copied %d part files" % n)
        return True
    return False


def build_zip(app, publish, out):
    """Build the download from the REPOSITORY's own tracked files, never by hand.

    Glen, 2026-08-30: "why not put all the essential files in a Zip folder that mirrors the folder
    on Github. Why not make Github and the Blocks folder on dropbox parallel, so that they are
    always in sync." They cannot be identical - the repository also carries the C# source, the build
    script, CLAUDE.md, tools\\ and 328 files of Documents, none of which should reach a student. What
    CAN be kept in step is this: the zip holds exactly the RUNTIME subset of what git tracks, listed
    below and taken from `git ls-files`, so an untracked stray cannot travel and a file the
    repository gains under these paths arrives on the next publish without anyone remembering.

    It replaces "copy this whole folder", which was the advice in the first Read Me and was wrong:
    it would have brought Archive, the build photographs and every superseded document onto a
    student's machine. And it carries the WHOLE tracked parts library - 11,288 files, 113 MB loose
    but 9 MB compressed - not the narrow closure of the current designs, which would break the
    moment somebody picked a different part from the menu."""
    ver = marker_of(os.path.join(app["repo"], app["page"]), app["marker"])
    want = "%s%s).zip" % (app["zip_glob"], ver.split(".")[-1])
    dest = os.path.join(app["zip_dir"], want)
    have = [f for f in os.listdir(app["zip_dir"])
            if f.startswith(app["zip_glob"]) and f.endswith(".zip")]
    # The Read Me travels INSIDE the zip, so a change to it makes the zip stale even when the
    # version has not moved. Compare the copy in the folder against the copy in the download.
    fresh = have == [want] and os.path.isfile(dest)
    readme = os.path.join(app["dest"], "Read Me First.txt")
    if fresh and os.path.isfile(readme):
        try:
            inzip = zipfile.ZipFile(dest).read(app["zip_inner"] + "Read Me First.txt")
            fresh = inzip == open(readme, "rb").read()
        except KeyError:
            fresh = False
    if fresh:
        out.append("   %-11s %-44s %s" % ("zip", want, "current"))
        return True
    out.append("   %-11s %-44s %s" % ("zip", want, "MISSING" if not have else "STALE"))
    if not publish:
        return False

    import subprocess
    tracked = subprocess.run(["git", "-C", app["repo"], "ls-files"] + app["zip_build"],
                             capture_output=True, text=True).stdout.split("\n")
    inner = app["zip_inner"]
    zo = zipfile.ZipFile(dest + ".tmp", "w", zipfile.ZIP_DEFLATED)
    n = 0
    for rel in tracked:
        rel = rel.strip()
        if not rel or "/Archive/" in rel or rel.startswith("Archive/"):
            continue
        src = os.path.join(app["repo"], rel.replace("/", os.sep))
        if not os.path.isfile(src):
            continue
        zo.write(src, inner + rel)
        n += 1
    # The Read Me lives beside the program in Dropbox, not in the repository - it is written for
    # whoever downloads this, and the zip is the thing they download.
    readme = os.path.join(app["dest"], "Read Me First.txt")
    if os.path.isfile(readme):
        zo.write(readme, inner + "Read Me First.txt")
        n += 1
    zo.close()
    arch = os.path.join(app["zip_dir"], "Archive")
    os.makedirs(arch, exist_ok=True)
    for f in have:
        if f != want:
            shutil.move(os.path.join(app["zip_dir"], f), os.path.join(arch, f))
    os.replace(dest + ".tmp", dest)
    out.append("      built %s — %d files, %.1f MB" % (want, n, os.path.getsize(dest) / 1e6))
    return True


def check_zip(app, publish, out):
    zdir = app["zip_dir"]
    zips = [f for f in os.listdir(zdir) if f.startswith(app["zip_glob"]) and f.endswith(".zip")]
    if not zips:
        out.append("   zip         none found in %s" % zdir)
        return False
    zips.sort()
    zpath = os.path.join(zdir, zips[-1])
    repo_page = os.path.join(app["repo"], app["page"])
    repo_exe = os.path.join(app["repo"], app["exe"])
    zf = zipfile.ZipFile(zpath)
    inner_page = app["zip_inner"] + app["page"]
    inner_exe = app["zip_inner"] + app["exe"]
    def zh(n):
        return hashlib.sha256(zf.read(n)).hexdigest()[:12] if n in zf.namelist() else None
    ok = zh(inner_page) == sha(repo_page) and zh(inner_exe) == sha(repo_exe)
    ver = marker_of(repo_page, app["marker"])
    want = "%s%s).zip" % (app["zip_glob"], ver.split(".")[-1])
    named = zips[-1] == want
    out.append("   zip         %-34s %s%s" %
               (zips[-1], "current" if ok else "STALE",
                "" if named else "   (name does not match %s)" % want))
    if ok and named:
        return True
    if publish:
        new = os.path.join(zdir, want)
        page = open(repo_page, "rb").read()
        exe = open(repo_exe, "rb").read()
        zo = zipfile.ZipFile(new + ".tmp", "w", zipfile.ZIP_DEFLATED)
        for i in zf.infolist():
            data = page if i.filename == inner_page else exe if i.filename == inner_exe \
                else zf.read(i.filename)
            zo.writestr(i, data)
        zo.close()
        zf.close()
        arch = os.path.join(zdir, "Archive")
        os.makedirs(arch, exist_ok=True)
        if os.path.abspath(new) != os.path.abspath(zpath):
            shutil.move(zpath, os.path.join(arch, os.path.basename(zpath)))
        elif os.path.isfile(new):
            shutil.move(new, os.path.join(arch, os.path.basename(new)))
        os.replace(new + ".tmp", new)
        out.append("      rebuilt %s, previous one archived" % want)
        return True
    return False


def main():
    publish = "--publish" in sys.argv
    stale = 0
    for app in APPS:
        out = []
        clean = True
        rp, dp = os.path.join(app["repo"], app["page"]), os.path.join(app["dest"], app["page"])
        re_, de = os.path.join(app["repo"], app["exe"]), os.path.join(app["dest"], app["exe"])
        for label, a, b, hashfn in (("page", rp, dp, sha), ("exe", re_, de, sha)):
            same = hashfn(a) is not None and hashfn(a) == hashfn(b)
            note = ""
            if label == "page":
                note = "repo %s   dropbox %s" % (marker_of(a, app["marker"]),
                                                 marker_of(b, app["marker"]))
            out.append("   %-11s %-44s %s" % (label, note, "current" if same else "STALE"))
            if not same:
                clean = False
                # the page carries a version, so the copy it displaces can be named by it
                place(a, b, publish, out, app["marker"] if label == "page" else None)
        for c in app.get("cmds", []):
            a, b = os.path.join(app["repo"], c), os.path.join(app["dest"], c)
            if not os.path.isfile(a):
                continue
            same = text_sha(a) == text_sha(b)
            if not same:
                out.append("   %-11s %-44s %s" % ("cmd", c, "STALE"))
                clean = False
                place(a, b, publish, out)
        if not stamp_readme(app, publish, out):
            clean = False
        if app.get("ldraw") and not check_ldraw(app, publish, out):
            clean = False
        if app.get("zip_build"):
            if not build_zip(app, publish, out):
                clean = False
        elif app.get("zip_dir") and not check_zip(app, publish, out):
            clean = False
        print(app["name"])
        for line in out:
            print(line)
        if not clean:
            stale += 1
    print()
    if stale and not publish:
        print("%d of %d applications are STALE in Dropbox. Re-run with --publish to fix." %
              (stale, len(APPS)))
    elif stale:
        print("published; re-run without --publish to confirm")
    else:
        print("All %d applications are complete and current in Sangala Tools." % len(APPS))
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
