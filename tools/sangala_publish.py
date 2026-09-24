"""Is the Dropbox Sangala Tools folder complete and current for one application?

That folder, not the repository, is what Jo, Moses and the students install from. A push that never
reaches it is a change nobody outside the repository can run.

Since 2026-09-24 this runs on GitHub, not on anyone's own computer (Jo: "Nothing should be done
directly from Glen's machine anymore. It should all be done from Github"). Every merge into main of
any of the three repositories starts .github/workflows/sangala-release.yml, which rebuilds the exe
when its source changed and then runs this against Dropbox through Dropbox's own interface - so
nobody has to remember to publish, and nothing depends on a Dropbox folder synced to one machine.

    python sangala_publish.py --app Studio --repo PATH             report; exit code 1 if stale
    python sangala_publish.py --app Studio --repo PATH --publish   copy what is stale
    python sangala_publish.py ... --local FOLDER    a local stand-in for Sangala Tools, for testing

PATH is a checkout of that application's repository. Against Dropbox it reads DROPBOX_APP_KEY,
DROPBOX_APP_SECRET, DROPBOX_REFRESH_TOKEN and DROPBOX_BASE (the path of the Sangala Tools folder,
counted from the top of the team's Dropbox) from the environment - the workflow supplies them from
the organization's secrets.

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
import argparse, hashlib, io, os, re, shutil, subprocess, sys, tempfile, zipfile

APPS = {
    "Studio": {
        "dest": "Sangala Studio Files/Sangala Studio (Program)",
        "page": "SangalaStudio.html",
        "exe": "SangalaStudio.exe",
        "marker": "SANGALA_VERSION",
        "cmds": ["Update SangalaStudio.cmd", "Create Desktop Shortcut.cmd"],
        # the zip beside the program folder: same page and exe, wrapped for a one-file download
        "zip_dir": "Sangala Studio Files",
        "zip_glob": "Sangala Studio (Ver ",
        "zip_inner": "Sangala Studio/",
    },
    "Mosaic": {
        "dest": "Sangala Mosaic Files",
        "page": "SangalaMosaic.html",
        "exe": "SangalaMosaic.exe",
        "marker": "SANGALA_MOSAIC_VERSION",
        "cmds": ["Update SangalaMosaic.cmd", "Create Desktop Shortcut.cmd"],
    },
    "Blocks": {
        "dest": "Sangala Blocks Files",
        "page": "SangalaBlockDesigner.html",
        "exe": "SangalaBlockDesigner.exe",
        "marker": "SANGALA_VERSION",
        "cmds": ["Update SangalaBlocks.cmd", "Create Desktop Shortcut.cmd"],
        "ldraw": True,
        # The parts list the LDraw check reads. It lives in Dropbox, not in the repository.
        "sheet": "Sangala Blocks Files/Documents/Full Parts List.xlsx",
        # THE DOWNLOAD, built from git ls-files over exactly these paths. Source, tools, Documents
        # and CLAUDE.md are not here on purpose: a student never needs them.
        "zip_dir": "Sangala Blocks Files",
        "zip_glob": "Sangala Blocks (Ver ",
        "zip_inner": "Sangala Blocks/",
        "zip_build": ["SangalaBlockDesigner.exe", "SangalaBlockDesigner.html", "Crane.ico",
                      "Create Desktop Shortcut.cmd", "Update SangalaBlocks.cmd", "LICENSE",
                      "LDraw", "LDView", "Projects"],
    },
}


# ---- where the published files live ---------------------------------------------------------------
# Paths are relative to the Sangala Tools folder and always written with "/".
def content_hash(data):
    """Dropbox's content_hash: SHA-256 over the SHA-256 of each 4 MiB block (dropbox/
    dropbox-api-content-hasher). Comparing it with the one Dropbox reports saves downloading a file
    just to learn it has not changed."""
    whole = hashlib.sha256()
    for i in range(0, len(data), 4 * 1024 * 1024):
        whole.update(hashlib.sha256(data[i:i + 4 * 1024 * 1024]).digest())
    return whole.hexdigest()


class LocalStore:
    """A folder standing in for Sangala Tools. Used to test this script without touching Dropbox."""

    def __init__(self, root):
        self.root = root

    def _p(self, rel):
        return os.path.join(self.root, *rel.split("/"))

    def read(self, rel):
        p = self._p(rel)
        return open(p, "rb").read() if os.path.isfile(p) else None

    def hash(self, rel):
        data = self.read(rel)
        return None if data is None else content_hash(data)

    def write(self, rel, data):
        p = self._p(rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(data)

    def move(self, src, dst):
        d = self._p(dst)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.move(self._p(src), d)

    def listdir(self, rel):
        p = self._p(rel)
        return sorted(f for f in os.listdir(p) if os.path.isfile(os.path.join(p, f))) \
            if os.path.isdir(p) else []

    def walk(self, rel):
        """Every file under rel, as paths relative to rel."""
        p, out = self._p(rel), []
        for dirpath, dirnames, filenames in os.walk(p):
            for fn in filenames:
                out.append(os.path.relpath(os.path.join(dirpath, fn), p).replace(os.sep, "/"))
        return out


class DropboxStore:
    """The Sangala Tools folder itself, reached through the Dropbox API."""

    def __init__(self, base):
        import dropbox
        from dropbox import common, files
        self.files = files
        self.exc = dropbox.exceptions.ApiError
        key, secret, token = (os.environ.get(k) for k in
                              ("DROPBOX_APP_KEY", "DROPBOX_APP_SECRET", "DROPBOX_REFRESH_TOKEN"))
        if not (key and secret and token and base):
            sys.exit("Dropbox is not set up: DROPBOX_APP_KEY, DROPBOX_APP_SECRET, "
                     "DROPBOX_REFRESH_TOKEN and DROPBOX_BASE must all be set.")
        dbx = dropbox.Dropbox(oauth2_refresh_token=token, app_key=key, app_secret=secret)
        # Sangala Tools sits in the team's shared space, not in one member's own folder, so paths
        # are counted from the team's root rather than from the account's home folder.
        root = dbx.users_get_current_account().root_info.root_namespace_id
        self.dbx = dbx.with_path_root(common.PathRoot.root(root))
        self.base = "/" + base.strip("/")

    def _p(self, rel):
        return self.base + "/" + rel

    def _meta(self, rel):
        try:
            return self.dbx.files_get_metadata(self._p(rel))
        except self.exc:
            return None

    def read(self, rel):
        if not isinstance(self._meta(rel), self.files.FileMetadata):
            return None
        return self.dbx.files_download(self._p(rel))[1].content

    def hash(self, rel):
        m = self._meta(rel)
        return m.content_hash if isinstance(m, self.files.FileMetadata) else None

    def write(self, rel, data):
        mode = self.files.WriteMode.overwrite
        chunk = 100 * 1024 * 1024        # a single upload may carry at most 150 MiB
        if len(data) <= chunk:
            self.dbx.files_upload(data, self._p(rel), mode=mode)
            return
        start = self.dbx.files_upload_session_start(data[:chunk])
        cur = self.files.UploadSessionCursor(session_id=start.session_id, offset=chunk)
        while len(data) - cur.offset > chunk:
            self.dbx.files_upload_session_append_v2(data[cur.offset:cur.offset + chunk], cur)
            cur.offset += chunk
        self.dbx.files_upload_session_finish(data[cur.offset:], cur,
                                             self.files.CommitInfo(path=self._p(rel), mode=mode))

    def move(self, src, dst):
        # autorename: an Archive that already holds this name keeps both rather than losing one.
        self.dbx.files_move_v2(self._p(src), self._p(dst), autorename=True)

    def _list(self, rel, recursive):
        try:
            r = self.dbx.files_list_folder(self._p(rel), recursive=recursive)
        except self.exc:
            return []
        entries = list(r.entries)
        while r.has_more:
            r = self.dbx.files_list_folder_continue(r.cursor)
            entries += r.entries
        return [e for e in entries if isinstance(e, self.files.FileMetadata)]

    def listdir(self, rel):
        return sorted(e.name for e in self._list(rel, False))

    def walk(self, rel):
        top = self._p(rel).lower() + "/"
        return [e.path_display[len(top):] for e in self._list(rel, True)
                if e.path_lower.startswith(top)]


# ---- small helpers --------------------------------------------------------------------------------
def sha(data):
    return None if data is None else hashlib.sha256(data).hexdigest()[:12]


def text_sha(data):
    """Hash with line endings normalized, so CRLF against LF is not reported as a difference."""
    return None if data is None else sha(data.replace(b"\r\n", b"\n"))


def crlf(data):
    """A .cmd reaches Windows with CRLF line endings whatever the checkout gave it. GitHub's Linux
    machine checks out LF, and cmd.exe misreads labels in an LF-only batch file."""
    return data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")


def for_windows(name, data):
    return crlf(data) if name.lower().endswith(".cmd") else data


def marker_of(data, key):
    if data is None:
        return "(absent)"
    m = re.search(key + r":\s*(\S+)", data[:4000].decode("utf-8", "replace"))
    return m.group(1) if m else "(no marker)"


def repo_file(repo, rel):
    p = os.path.join(repo, *rel.split("/"))
    return open(p, "rb").read() if os.path.isfile(p) else None


def place(store, data, dst, publish, out, marker=None):
    """Write data over dst, moving the superseded file into Archive beside it.

    NOT a .bak alongside, which is what this did first. Glen, 2026-08-30: the folder already holds
    more than a new user can sort out, and a program folder wearing two spare copies of itself is
    the clutter, not the safety net. Archive is where every other Sangala folder keeps what it has
    superseded, and the version it carried goes in its name so the copy can be identified."""
    if not publish:
        return
    old = store.read(dst)
    if old is not None:
        folder, name = dst.rsplit("/", 1)
        stem, ext = os.path.splitext(name)
        was = marker_of(old, marker) if marker else None
        tag = " (%s)" % was if was and was[0].isdigit() else ""
        store.move(dst, folder + "/Archive/" + stem + tag + ext)
    store.write(dst, data)
    out.append("      copied " + dst.rsplit("/", 1)[1])


def stamp_readme(app, repo, store, publish, out):
    """Keep the version inside Read Me First.txt true.

    Studio's has said 2026-08-10.191 since the day it was written, while that folder now holds .206
    - a number typed into a file goes stale the moment the file beside it changes. The publish is
    the one moment both are known, so it is written here rather than maintained by hand."""
    path = app["dest"] + "/Read Me First.txt"
    raw = store.read(path)
    if raw is None:
        return True
    ver = marker_of(repo_file(repo, app["page"]), app["marker"])
    text = raw.decode("utf-8")
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
        store.write(path, fixed.encode("utf-8"))
        out.append("      stamped Read Me First.txt with " + ver)
        return True
    return False


# ---- the LDraw files the Blocks parts list actually needs ---------------------------------------
def ldraw_closure(app, repo, store):
    """Every .dat the parts list reaches, following subfile references and ~Moved to redirects.
    Returns (root, paths relative to the repo's LDraw folder), or None if the checker or the parts
    list cannot be loaded."""
    check = os.path.join(repo, "tools", "check_parts.py")
    sheet = store.read(app["sheet"])
    if not os.path.isfile(check) or sheet is None:
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_parts", check)
    cp = importlib.util.module_from_spec(spec)
    argv, sys.argv = sys.argv, [check, "--none--"]      # keep its main() off the spreadsheet
    spec.loader.exec_module(cp)
    sys.argv = argv
    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    tmp.write(sheet)
    tmp.close()
    cp.SHEET = tmp.name
    root = os.path.join(repo, "LDraw", "ldraw")
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
        need.add(os.path.relpath(p, root).replace(os.sep, "/"))
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
    for pid in sorted(design_parts(app, repo, store)):
        want(pid)
    os.unlink(tmp.name)
    return root, sorted(need)


def design_parts(app, repo, store):
    """Every part number named by a design, library or kit that ships in either Projects folder."""
    import json
    ext = (".block", ".library", ".kit", ".parts")
    docs = []
    folder = app["dest"] + "/Projects"
    for rel in store.walk(folder):
        if rel.lower().endswith(ext):
            docs.append(store.read(folder + "/" + rel))
    top = os.path.join(repo, "Projects")
    for dirpath, dirnames, filenames in os.walk(top):
        for fn in filenames:
            if fn.lower().endswith(ext):
                docs.append(open(os.path.join(dirpath, fn), "rb").read())
    ids = set()
    for raw in docs:
        try:
            d = json.loads(raw.decode("utf-8"))
        except Exception:
            continue
        for key in ("bricks", "parts", "libParts"):
            for item in (d.get(key) or []):
                if isinstance(item, dict) and item.get("id"):
                    ids.add(str(item["id"]))
    return ids


def check_ldraw(app, repo, store, publish, out):
    got = ldraw_closure(app, repo, store)
    if got is None:
        out.append("   LDraw       cannot check - tools/check_parts.py or %s is missing" % app["sheet"])
        return False
    root, need = got
    folder = app["dest"] + "/LDraw/ldraw"
    have = {r.lower() for r in store.walk(folder)}
    missing = [r for r in need if r.lower() not in have]
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
        for r in missing:
            store.write(folder + "/" + r, open(os.path.join(root, *r.split("/")), "rb").read())
        out.append("      copied %d part files" % len(missing))
        return True
    return False


def build_zip(app, repo, store, publish, out):
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
    ver = marker_of(repo_file(repo, app["page"]), app["marker"])
    want = "%s%s).zip" % (app["zip_glob"], ver.split(".")[-1])
    zdir = app["zip_dir"]
    have = [f for f in store.listdir(zdir) if f.startswith(app["zip_glob"]) and f.endswith(".zip")]
    # The Read Me travels INSIDE the zip, so a change to it makes the zip stale even when the
    # version has not moved. Compare the copy in the folder against the copy in the download.
    readme = store.read(app["dest"] + "/Read Me First.txt")
    fresh = have == [want]
    if fresh and readme is not None:
        try:
            inzip = zipfile.ZipFile(io.BytesIO(store.read(zdir + "/" + want))).read(
                app["zip_inner"] + "Read Me First.txt")
            fresh = inzip == readme
        except KeyError:
            fresh = False
    if fresh:
        out.append("   %-11s %-44s %s" % ("zip", want, "current"))
        return True
    out.append("   %-11s %-44s %s" % ("zip", want, "MISSING" if not have else "STALE"))
    if not publish:
        return False

    tracked = subprocess.run(["git", "-C", repo, "ls-files"] + app["zip_build"],
                             capture_output=True, text=True).stdout.split("\n")
    inner = app["zip_inner"]
    buf = io.BytesIO()
    zo = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
    n = 0
    for rel in tracked:
        rel = rel.strip()
        if not rel or "/Archive/" in rel or rel.startswith("Archive/"):
            continue
        data = repo_file(repo, rel)
        if data is None:
            continue
        zo.writestr(inner + rel, for_windows(rel, data))
        n += 1
    # The Read Me lives beside the program in Dropbox, not in the repository - it is written for
    # whoever downloads this, and the zip is the thing they download.
    if readme is not None:
        zo.writestr(inner + "Read Me First.txt", readme)
        n += 1
    zo.close()
    for f in have:
        if f != want:
            store.move(zdir + "/" + f, zdir + "/Archive/" + f)
    store.write(zdir + "/" + want, buf.getvalue())
    out.append("      built %s - %d files, %.1f MB" % (want, n, len(buf.getvalue()) / 1e6))
    return True


def check_zip(app, repo, store, publish, out):
    zdir = app["zip_dir"]
    zips = sorted(f for f in store.listdir(zdir)
                  if f.startswith(app["zip_glob"]) and f.endswith(".zip"))
    if not zips:
        out.append("   zip         none found in %s" % zdir)
        return False
    zpath = zdir + "/" + zips[-1]
    page, exe = repo_file(repo, app["page"]), repo_file(repo, app["exe"])
    zf = zipfile.ZipFile(io.BytesIO(store.read(zpath)))
    inner_page = app["zip_inner"] + app["page"]
    inner_exe = app["zip_inner"] + app["exe"]

    def zh(n):
        return sha(zf.read(n)) if n in zf.namelist() else None

    # The helper .cmd files travel in the zip too, compared with line endings normalized as they
    # are for the program folder. Before 2026-09-24 only the page and the exe were replaced, so the
    # zip kept whatever updater it was first built with - and an updater older than the one that
    # replaces itself never gets any newer on its own.
    cmds = {app["zip_inner"] + c: repo_file(repo, c) for c in app.get("cmds", [])
            if repo_file(repo, c) is not None}

    def zt(n):
        return text_sha(zf.read(n)) if n in zf.namelist() else None

    ok = zh(inner_page) == sha(page) and zh(inner_exe) == sha(exe) \
        and all(zt(n) == text_sha(data) for n, data in cmds.items())
    ver = marker_of(page, app["marker"])
    want = "%s%s).zip" % (app["zip_glob"], ver.split(".")[-1])
    named = zips[-1] == want
    out.append("   zip         %-34s %s%s" %
               (zips[-1], "current" if ok else "STALE",
                "" if named else "   (name does not match %s)" % want))
    if ok and named:
        return True
    if publish:
        buf = io.BytesIO()
        zo = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
        for i in zf.infolist():
            data = page if i.filename == inner_page else exe if i.filename == inner_exe \
                else crlf(cmds[i.filename]) if i.filename in cmds \
                else zf.read(i.filename)
            zo.writestr(i, data)
        for n, data in cmds.items():
            if n not in zf.namelist():
                zo.writestr(n, crlf(data))
        for n, data in ((inner_page, page), (inner_exe, exe)):
            if n not in zf.namelist():
                zo.writestr(n, data)
        zo.close()
        # The zip it replaces goes to Archive, whether or not the new one takes the same name.
        store.move(zpath, zdir + "/Archive/" + zips[-1])
        store.write(zdir + "/" + want, buf.getvalue())
        out.append("      rebuilt %s, previous one archived" % want)
        return True
    return False


def run(name, repo, store, publish):
    app = APPS[name]
    out = []
    clean = True
    for label, key in (("page", "page"), ("exe", "exe")):
        a = repo_file(repo, app[key])
        if a is None:
            sys.exit("%s is not in %s - is --repo the %s repository?" % (app[key], repo, name))
        dst = app["dest"] + "/" + app[key]
        same = store.hash(dst) == content_hash(a)
        note = ""
        if label == "page":
            note = "repo %s   dropbox %s" % (marker_of(a, app["marker"]),
                                             marker_of(store.read(dst), app["marker"]))
        out.append("   %-11s %-44s %s" % (label, note, "current" if same else "STALE"))
        if not same:
            clean = False
            # the page carries a version, so the copy it displaces can be named by it
            place(store, a, dst, publish, out, app["marker"] if label == "page" else None)
    for c in app.get("cmds", []):
        a = repo_file(repo, c)
        if a is None:
            continue
        dst = app["dest"] + "/" + c
        if text_sha(a) != text_sha(store.read(dst)):
            out.append("   %-11s %-44s %s" % ("cmd", c, "STALE"))
            clean = False
            place(store, crlf(a), dst, publish, out)
    if not stamp_readme(app, repo, store, publish, out):
        clean = False
    if app.get("ldraw") and not check_ldraw(app, repo, store, publish, out):
        clean = False
    if app.get("zip_build"):
        if not build_zip(app, repo, store, publish, out):
            clean = False
    elif app.get("zip_dir") and not check_zip(app, repo, store, publish, out):
        clean = False
    print(name)
    for line in out:
        print(line)
    print()
    if clean:
        print("%s is complete and current in Sangala Tools." % name)
    elif publish:
        print("published; re-run without --publish to confirm")
    else:
        print("%s is STALE in Dropbox. Re-run with --publish to fix." % name)
    return 0 if clean or publish else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--app", required=True, choices=sorted(APPS))
    ap.add_argument("--repo", required=True, help="a checkout of that application's repository")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--local", help="a folder standing in for Sangala Tools (testing)")
    a = ap.parse_args()
    store = LocalStore(a.local) if a.local else DropboxStore(os.environ.get("DROPBOX_BASE", ""))
    return run(a.app, os.path.abspath(a.repo), store, a.publish)


if __name__ == "__main__":
    sys.exit(main())
