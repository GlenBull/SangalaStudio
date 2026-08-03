#!/usr/bin/env python3
"""Sangala Studio bridge for macOS - the local helper that holds the USB die cutter connection.

This is the macOS counterpart of SangalaStudio.exe (SangalaServer.cs + DieCutter.cs). It does the
same two jobs: serve SangalaStudio.html to the browser on a loopback port, and drive the die cutter
over USB. The browser page is UNCHANGED and cannot tell the two apart - it calls the same routes
with the same wire formats, so every feature that works on Windows works here.

WHY THIS EXISTS IN A SECOND LANGUAGE. Only the USB transport is platform-specific. Windows opens the
machine through the usbprint.sys device interface (SetupDi* + CreateFile), which has no macOS
equivalent; the cross-platform route is libusb, reached from Python through pyusb. Moses measured
that route on a MacBook Air on 2026-08-03: the interface claimed, and the machine answered ESC ENQ
with "2" (no media loaded). macOS's own USB printing class driver does not hold the device.

KEEPING THE TWO IN STEP. Everything below the transport - every GPGL command, the coordinate
conversion, the 1024-byte chunking - is transliterated from DieCutter.cs and must stay identical to
it. DieCutter.cs is the reference; this file follows. Method names, their order, and the comments
that explain a value are deliberately the same in both so the pair can be read side by side. Where
one changes, the other changes in the same commit.

    python3 -m pip install pyusb
    python3 tools/sangala_bridge.py

Run it from a clone of the repository: it serves SangalaStudio.html and the assets/ folder from
their places there. Ctrl-C stops it. There is no tray icon yet - that needs pyobjc and is stage 2.
"""

import json
import os
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ---------------------------------------------------------------- constants
# From DieCutter.cs: GPGL is ASCII terminated by ETX; the control bytes are the ESC pairs.
ETX, ESC, ENQ, EOT = 0x03, 0x1B, 0x05, 0x04

MAT_H = 305.0                    # SangalaServer.cs: media length handed to Setup
SILHOUETTE_VID = 0x0B4D

# Letter with the standard 15.9 mm registration inset. SangalaServer.cs repeats these three
# numbers in DoScan / DoPrintCut / DoManualRead / DoManualCut; they are gathered here once.
INSET, PAGE_W, PAGE_H = 15.9, 215.9, 279.4

# PID -> (model name, usable width mm, mat TG code, eye offset mm). Mirrors Cutter.Open() in
# DieCutter.cs exactly, including the fallback. The eye offset is the distance the optical eye sits
# to the RIGHT of the blade: the auto reg-scan starts that much further LEFT so the eye reaches the
# mark. Portrait 30, every Cameo 0 - 0 is what made registration work on Gina's Cameo 2.
MODELS = {
    0x113F: ("Silhouette Portrait 4", 216.0, "11", 30.0),
    # Cameo 2: same GPGL and type-2 registration as the Portraits. MatTG "3" is Studio-sniffed and
    # unverified for the Cameo; tune it first if a mat misfeeds.
    0x112B: ("Silhouette Cameo 2", 304.0, "3", 0.0),
    0x1121: ("Silhouette Cameo", 304.0, "3", 0.0),
    0x112F: ("Silhouette Cameo 3", 304.8, "3", 0.0),
    0x1137: ("Silhouette Cameo 4", 304.8, "3", 0.0),
    0x1138: ("Silhouette Cameo 4 Plus", 372.0, "3", 0.0),
    0x1139: ("Silhouette Cameo 4 Pro", 600.0, "3", 0.0),
    0x1140: ("Silhouette Cameo 5", 330.2, "3", 0.0),
    0x1141: ("Silhouette Cameo 5 Plus", 372.0, "3", 0.0),
}
# NOT listed, and deliberately: the Cameo Pro MK-II (0x1146) and the Cameo 5 alphas use FOUR
# registration marks. This engine prints and scans the standard three, so they would cut but fail to
# register. Better to fall back than to claim support that misleads.
FALLBACK_MODEL = ("Silhouette Portrait 3", 203.0, "3", 30.0)


def SU(mm):
    """Millimetres -> Silhouette Units. 1 mm = 20 SU.

    C# Math.Round and Python round() both break a .5 tie to even, so the two implementations agree
    on every coordinate. Do not "fix" this to int(x + 0.5).
    """
    return int(round(mm * 20.0))


class CutterError(Exception):
    """Anything the user should be told about: not found, busy, timed out, refused."""


# ---------------------------------------------------------------- the machine
class Cutter:
    """GPGL engine over a libusb bulk pipe. Transliterated from Cutter in DieCutter.cs."""

    def __init__(self):
        self.model_name, self.width_mm, self.mat_tg, self.eye_right_mm = FALLBACK_MODEL
        self._dev = None
        self._intf = None
        self._out = None
        self._in = None

    # ---- transport. These four methods are the ONLY platform-specific code in the file.
    def open(self):
        try:
            import usb.core
            import usb.util
        except ImportError:
            raise CutterError("pyusb is not installed. Run: python3 -m pip install pyusb")

        try:
            devices = list(usb.core.find(find_all=True, idVendor=SILHOUETTE_VID))
        except usb.core.NoBackendError:
            raise CutterError(
                "pyusb has no libusb backend. Install libusb (brew install libusb), or use a "
                "Python that ships one.")
        if not devices:
            raise CutterError("Die Cutter not found. Is it powered on and connected by USB, and "
                              "is Silhouette Studio closed?")

        dev = devices[0]
        self.model_name, self.width_mm, self.mat_tg, self.eye_right_mm = MODELS.get(
            dev.idProduct, FALLBACK_MODEL)

        try:
            dev.set_configuration()          # harmless if it is already configured
            cfg = dev.get_active_configuration()
        except Exception as e:
            raise CutterError("Could not configure the Die Cutter (%s). This is usually another "
                              "program holding it - close Silhouette Studio and retry." % e)

        intf = cfg[(0, 0)]
        # On Linux a class driver must be detached first. On macOS the printing class driver does
        # not hold the interface (measured), and this backend usually cannot answer the question at
        # all - so ask, but never let the asking end the run.
        try:
            if dev.is_kernel_driver_active(intf.bInterfaceNumber):
                dev.detach_kernel_driver(intf.bInterfaceNumber)
        except NotImplementedError:
            pass
        except Exception:
            pass

        try:
            usb.util.claim_interface(dev, intf.bInterfaceNumber)
        except Exception as e:
            raise CutterError("Could not claim the Die Cutter (%s). Another program has it - close "
                              "Silhouette Studio (and any earlier tool), then retry." % e)

        out = usb.util.find_descriptor(intf, custom_match=lambda e:
                                       usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
        inp = usb.util.find_descriptor(intf, custom_match=lambda e:
                                       usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
        if out is None or inp is None:
            usb.util.release_interface(dev, intf.bInterfaceNumber)
            raise CutterError("The Die Cutter did not offer both a bulk OUT and a bulk IN endpoint.")

        self._dev, self._intf, self._out, self._in = dev, intf, out, inp

    def _write_raw(self, b):
        if self._out is None:
            raise CutterError("Not connected to the Die Cutter.")
        try:
            # libusb splits this into 64-byte packets itself, so an arbitrary length is fine.
            # NOTE for a future stall: if a write whose length is an exact multiple of the endpoint's
            # packet size ever hangs, a zero-length packet is the classic cure. usbprint.sys adds one
            # on Windows. Not needed in testing so far; this is where it would go.
            self._out.write(b, timeout=8000)
        except Exception as e:
            raise CutterError("write to the Die Cutter failed: %s" % e)

    def _write_cmds(self, cmds):
        buf = bytearray()
        for c in cmds:
            buf += c.encode("ascii")
            buf.append(ETX)
        self._write_raw(bytes(buf))

    def _write_cmd(self, c):
        self._write_cmds([c])

    def _read_resp(self, ms):
        """One reply, or None on timeout. Matches ReadResp: 64 bytes, trailing ETX/NUL/space cut."""
        if self._in is None:
            raise CutterError("Not connected to the Die Cutter.")
        try:
            data = self._in.read(64, timeout=ms)
        except Exception:
            return None                       # USBTimeoutError and friends: C# returns null here
        if not len(data):
            return None
        return bytes(data).decode("ascii", "replace").rstrip("\x03\x00 ")

    # ---- protocol. Everything from here down is platform-neutral and mirrors DieCutter.cs.
    def firmware(self):
        self._write_cmd("FG")
        r = self._read_resp(3000)
        return r if r is not None else "(no response)"

    def _status(self):
        self._write_raw(bytes([ESC, ENQ]))
        r = self._read_resp(2000)
        if r == "0":
            return "ready"
        if r == "1":
            return "moving"
        if r == "2":
            return "unloaded"
        return r if r is not None else "?"

    def wait_ready(self, note, timeout_ms=120000):
        end = time.monotonic() + timeout_ms / 1000.0
        while time.monotonic() < end:
            s = self._status()
            if s == "ready":
                return
            if s == "unloaded" and note:
                note("Load the mat into the Die Cutter...")
            time.sleep(0.06)
        raise CutterError("Die Cutter never became ready")

    def setup(self, speed, pressure, pen, depth, blade_mm, media_len_mm, note):
        speed = max(1, min(30, speed))
        pressure = max(1, min(33, pressure))
        self._write_raw(bytes([ESC, EOT]))                 # initialize
        self.firmware()                                    # drain version reply
        self._write_cmd("TG" + self.mat_tg)
        self._write_cmds(["FN0", "TB50,0"])
        self._write_cmds(["\\0,0", "Z%d,%d" % (SU(media_len_mm), SU(self.width_mm))])
        self._write_cmd("FX%d,1" % pressure)
        self._write_cmd("TJ0")
        self._write_cmd("!%d,1" % speed)
        self._write_cmd("FC0,1,1")
        self._write_cmd("FE0,1")
        if pen:
            self._write_cmds(["FF0,0,1", "FF0,0,1"])
        else:
            self._write_cmds(["FF1,0,1", "FF1,1,1"])
        self._write_cmd("FX%d,1" % pressure)
        self._write_cmd("TJ3")
        self._write_cmd("FC%d,1,1" % (0 if pen else SU(blade_mm)))
        # NOTE: AutoBlade reset (FY1) removed from Setup -- it runs before the
        # registration scan and disturbed it. Blade depth is set separately.
        if not pen and depth > 0:
            self._write_cmd("TF%d,1" % max(0, min(10, depth)))
        self.wait_ready(note)

    def cut(self, paths, return_to_start, progress, note, emit_end=True):
        """paths: list of point lists in mm (x across carriage, y feed direction)."""
        cmds = []
        max_y = 0.0
        for p in paths:
            if len(p) < 2:
                continue
            last = "%d,%d" % (SU(p[0][1]), SU(p[0][0]))
            cmds.append("M" + last)
            for i in range(1, len(p)):
                pt = "%d,%d" % (SU(p[i][1]), SU(p[i][0]))
                if pt != last:
                    cmds.append("D" + pt)
                    last = pt
                if p[i][1] > max_y:
                    max_y = p[i][1]
            if p[0][1] > max_y:
                max_y = p[0][1]

        buf = bytearray()
        for c in cmds:
            buf += c.encode("ascii")
            buf.append(ETX)
        data = bytes(buf)

        off = 0
        while off < len(data):
            length = min(1024, len(data) - off)
            cut_at = length                                # trim to last ETX boundary
            for i in range(off + length - 1, off - 1, -1):
                if data[i] == ETX:
                    cut_at = i - off + 1
                    break
            self._write_raw(data[off:off + cut_at])
            self.wait_ready(note)
            off += cut_at
            if progress:
                progress(int(100 * off / max(1, len(data))))

        if emit_end:
            if return_to_start:
                self._write_cmds(["L0", "\\0,0", "M0,0", "J0", "FN0", "TB50,0"])
            else:
                # move clear of the cut; do NOT SO0 (it re-homes the origin and breaks the M0,0
                # eject in unload)
                self._write_cmd("M%d,0" % SU(max_y + 10))
            self.wait_ready(note)

    def reset(self):
        """Re-initialize. ESC EOT is the only reset the protocol exposes - there is no dedicated
        buffer flush. On the Cameo 2 this may not fully clear a stuck registration job; power-cycling
        is the sure clear."""
        self._write_raw(bytes([ESC, EOT]))
        try:
            self.firmware()                                # drain the version reply
        except CutterError:
            pass

    def scan_reg_marks(self, len_mm, wid_mm, ox_mm, oy_mm, approach_mm=10.0):
        """Print-and-cut registration scan. Returns the machine's reply -- "0" means marks found.

        TB123,height,width,top,left. top/left = the first-mark search start = mark origin minus a
        10 mm search range, mirroring fablabnbg/inkscape-silhouette (Graphtec.py:
        automatic_regmark_test_mm_cmd, origin - 10). Keep the 10.
        Caller must setup() first so the machine has a coordinate frame.
        """
        self._write_cmd("TB50,0")
        self._write_cmd("TB99")
        self._write_cmd("TB52,2")                          # type 2 = Cameo/Portrait
        self._write_cmd("TB51,400")                        # 20 mm mark length
        self._write_cmd("TB53,10")                         # 0.5 mm thickness
        self._write_cmd("TB55,1")
        # The optical eye sits eye_right_mm to the RIGHT of the blade and the firmware aims the
        # blade, so start the search that much further LEFT (may go negative, into the left margin)
        # so the eye actually reaches the top-left square.
        start_y = max(oy_mm - approach_mm, 0)
        start_x = ox_mm - approach_mm - self.eye_right_mm
        self._write_cmd("TB123,%d,%d,%d,%d" % (SU(len_mm), SU(wid_mm), SU(start_y), SU(start_x)))
        r = self._read_resp(60000)                         # "    0" = found
        return "(no response)" if r is None else r.strip()

    def set_force(self, f):
        """Change tool force between passes (a lighter pass to score/crease)."""
        self._write_cmd("FX%d,1" % max(1, min(33, f)))

    def unload(self, media_len_mm):
        """Eject the mat: roll it all the way out to the front. A bare M0,0 = "go to the load
        origin" (setup's \\0,0), which rolls the media fully out. Works because the cut end no longer
        sends SO0, which re-homed the origin and cancelled this move."""
        self.wait_ready(None)
        self._write_cmd("M0,0")
        self.wait_ready(None)

    def send_raw(self, cmd):
        """Debug: one raw GPGL command (ETX is appended by _write_cmd)."""
        self.wait_ready(None)
        self._write_cmd(cmd)
        self.wait_ready(None)

    def send_raw_bytes(self, b):
        """An exact byte sequence, no ETX and no framing, for control packets like ESC FF. No
        wait_ready after - an eject may roll the mat out without reporting ready."""
        self.wait_ready(None)
        self._write_raw(b)

    def set_blade_depth(self, d):
        """AutoBlade depth mid-job (reset then tap to depth)."""
        self._write_cmd("FY1")
        self._write_cmd("TF%d,1" % max(1, min(10, d)))

    def move_to_mm(self, x_mm, y_mm):
        """Jog the tool head (pen UP) to an absolute position in mm. Caller must setup() first.

        x may go LEFT of the logical origin: the optical eye sits ~30 mm right of the blade, so
        reaching a left-edge mark needs the carriage in the left margin. Studio drives it there too.
        """
        x = max(-60.0, min(self.width_mm, x_mm))
        y = max(0.0, y_mm)
        self._write_cmd("M%d,%d" % (SU(y), SU(x)))
        self.wait_ready(None)

    def manual_reg_marks(self, len_mm, wid_mm):
        """Manual registration: the head already sits over the top-left SQUARE mark, the machine
        reads it there and finds the other two from the spacing. TB23 = manual regmark test
        (Graphtec.py: manual_regmark_mm_cmd). Same setup block as the scan; only TB123 -> TB23."""
        self._write_cmd("TB50,0")
        self._write_cmd("TB99")
        self._write_cmd("TB52,2")
        self._write_cmd("TB51,400")
        self._write_cmd("TB53,10")
        self._write_cmd("TB55,1")
        self._write_cmd("TB23,%d,%d" % (SU(len_mm), SU(wid_mm)))
        r = self._read_resp(60000)
        return "(no response)" if r is None else r.strip()

    def dispose(self):
        try:
            import usb.util
            if self._dev is not None and self._intf is not None:
                usb.util.release_interface(self._dev, self._intf.bInterfaceNumber)
                usb.util.dispose_resources(self._dev)
        except Exception:
            pass
        self._dev = self._intf = self._out = self._in = None


# ---------------------------------------------------------------- shared state
class State:
    """What the routes read and write. Mirrors the statics at the top of SangalaServer.cs."""

    def __init__(self):
        self.cutter = None
        self.last_status = "idle"
        self.jog_x, self.jog_y = INSET, INSET   # current manual-jog head position (mm)
        self.framed = False                     # has the machine been setup() since connect
        self.snap_svg = None                    # a drawing Snap! has posted, waiting for the page
        self.snap_lock = threading.Lock()
        self.machine_lock = threading.Lock()    # one job at a time on the USB pipe


S = State()


def note(m):
    S.last_status = m


# ---------------------------------------------------------------- body parsing
def split_cut_score(lines, start, sub):
    """Split path lines into cut and score paths, separated by a "---SCORE---" line.

    Subtracts `sub` mm from each coordinate (to move page coords into the registered frame; pass 0
    for a plain cut). Mirrors SplitCutScore, including the error text.
    """
    cut, score = [], []
    target = cut
    for i in range(start, len(lines)):
        ln = lines[i].strip()
        if not ln:
            continue
        if ln == "---SCORE---":
            target = score
            continue
        arr = []
        for pt in lines[i].split(" "):
            if not pt:
                continue
            xy = pt.split(",")
            try:
                if len(xy) < 2:
                    raise ValueError
                fx, fy = float(xy[0]), float(xy[1])
            except ValueError:
                raise CutterError("Bad point at line %d: '%s'  (line: '%s')" % (i, pt, lines[i]))
            arr.append((fx - sub, fy - sub))
        if len(arr) >= 2:
            target.append(arr)
    return cut, score


def score_force(cut_force):
    """Fold/score lines get a lighter pass so paper creases instead of cutting through."""
    return max(1, cut_force // 2)


def parse_header(line):
    """First body line: "force,speed,depth,pen[,passes]". Returns (force, speed, depth, pen, passes)."""
    s = line.split(",")
    try:
        if len(s) < 4:
            raise ValueError
        force, speed, depth = int(s[0]), int(s[1]), int(s[2])
    except ValueError:
        raise CutterError("Bad settings header: '%s'" % line)
    pen = s[3] == "1"
    passes = 1
    if len(s) >= 5:
        try:
            passes = int(s[4])
        except ValueError:
            passes = 1
    return force, speed, depth, pen, max(1, min(4, passes))


# ---------------------------------------------------------------- routes
def need_cutter():
    if S.cutter is None:
        raise CutterError("Not connected to the Die Cutter.")
    return S.cutter


def do_connect():
    if S.cutter is not None:
        S.cutter.dispose()
        S.cutter = None
    c = Cutter()
    c.open()
    S.cutter = c
    S.framed = False
    fw = c.firmware()
    S.last_status = "connected to " + c.model_name
    return {"ok": True, "model": c.model_name, "fw": fw, "width": c.width_mm}


def do_cut(body):
    c = need_cutter()
    lines = body.replace("\r", "").split("\n")
    if len(lines) < 2:
        raise CutterError("No design received.")
    force, speed, depth, pen, passes = parse_header(lines[0])
    paths, scores = split_cut_score(lines, 1, 0.0)
    if not paths and not scores:
        raise CutterError("No cut paths in the design.")

    S.last_status = "getting ready"
    c.setup(speed, force, pen, depth, 0.9, MAT_H, note)
    verb = "drawing " if pen else "making "
    for p in range(passes if paths else 0):
        c.cut(paths, False, lambda pct: note(verb + str(pct) + "%"), note,
              p == passes - 1 and not scores)
    if scores:
        c.set_force(score_force(force))
        c.cut(scores, False, lambda pct: note("scoring " + str(pct) + "%"), note, True)
    try:
        c.unload(MAT_H)
    except CutterError:
        pass
    S.last_status = "done"
    return {"ok": True}


def do_unload():
    c = need_cutter()
    c.setup(8, 14, False, 3, 0.9, MAT_H, note)   # init so the machine accepts the feed
    c.unload(MAT_H)
    S.last_status = "unloaded"
    return {"ok": True}


def do_raw(body):
    c = need_cutter()
    cmd = (body or "").strip()
    if not cmd:
        raise CutterError("Empty command.")
    if not S.framed:
        c.setup(8, 14, False, 3, 0.9, MAT_H, note)
        S.framed = True
    if cmd[:4].lower() == "hex ":
        hexs = cmd[4:].replace(" ", "")
        if not hexs or len(hexs) % 2:
            raise CutterError("hex needs full byte pairs, e.g. hex 1B 0C")
        try:
            b = bytes.fromhex(hexs)
        except ValueError:
            raise CutterError("hex needs full byte pairs, e.g. hex 1B 0C")
        c.send_raw_bytes(b)
        S.last_status = "sent bytes: " + cmd
    else:
        c.send_raw(cmd)
        S.last_status = "sent: " + cmd
    return {"ok": True}


def do_scan(body):
    c = need_cutter()
    c.setup(8, 14, False, 3, 0.9, MAT_H, note)       # init + mat + boundary
    wid = PAGE_W - 2 * INSET                          # horizontal distance between marks
    length = PAGE_H - 2 * INSET                       # vertical distance between marks
    r = c.scan_reg_marks(length, wid, INSET, INSET)
    S.last_status = "scan: " + r
    return {"ok": True, "result": r}


def do_printcut(body):
    c = need_cutter()
    lines = body.replace("\r", "").split("\n")
    if len(lines) < 2:
        raise CutterError("No design received.")
    force, speed, depth, pen, passes = parse_header(lines[0])
    paths, scores = split_cut_score(lines, 1, INSET)
    if not paths and not scores:
        raise CutterError("No cut paths in the design.")

    c.setup(speed, force, pen, depth, 0.9, MAT_H, note)
    wid, length = PAGE_W - 2 * INSET, PAGE_H - 2 * INSET
    reg = c.scan_reg_marks(length, wid, INSET, INSET)
    if reg.strip() != "0":
        try:
            c.reset()
        except CutterError:
            pass
        S.framed = False
        S.last_status = "marks not found"
        return {"ok": False, "error": "Registration marks not found (reply " + reg + "). The "
                "machine was re-initialized; if a job still seems stuck, power-cycle the die cutter."}
    for p in range(passes if paths else 0):
        c.cut(paths, False, lambda pct: note("cutting " + str(pct) + "%"), note,
              p == passes - 1 and not scores)
    if scores:
        c.set_force(score_force(force))
        c.cut(scores, False, lambda pct: note("scoring " + str(pct) + "%"), note, True)
    try:
        c.unload(MAT_H)
    except CutterError:
        pass
    S.last_status = "done"
    return {"ok": True}


def do_manualstart(body):
    """The user jogs the tool over the top-left square, the machine reads it there, then finds the
    other two marks from the known spacing. Body: "force,speed,depth,pen"."""
    c = need_cutter()
    force, speed, depth, pen = 14, 8, 3, False
    s = (body or "").split(",")
    if len(s) >= 4:
        try:
            force, speed, depth = int(s[0]), int(s[1]), int(s[2])
        except ValueError:
            pass
        pen = s[3] == "1"
    c.setup(speed, force, pen, depth, 0.9, MAT_H, note)
    S.jog_x, S.jog_y = INSET, INSET               # nominal top-left square corner
    c.move_to_mm(S.jog_x, S.jog_y)
    S.last_status = "manual align: jog the tool onto the square, then Read marks"
    return {"ok": True, "x": S.jog_x, "y": S.jog_y}


def do_jog(body):
    """body: "dx,dy" (mm) to nudge the head from its current position."""
    c = need_cutter()
    s = (body or "").strip().split(",")
    dx, dy = float(s[0]), float(s[1])
    S.jog_x += dx
    S.jog_y += dy
    c.move_to_mm(S.jog_x, S.jog_y)
    S.last_status = "jog %.1f, %.1f mm" % (S.jog_x, S.jog_y)
    return {"ok": True, "x": S.jog_x, "y": S.jog_y}


def do_manualread(body):
    """body (optional): "lenY,widX" mm to override the mark-to-mark distances, used to dial out the
    blade-vs-optical-eye offset that makes the search overshoot. Empty body uses the true distances."""
    c = need_cutter()
    wid, length = PAGE_W - 2 * INSET, PAGE_H - 2 * INSET
    d = (body or "").strip().split(",")
    if len(d) >= 2:
        try:
            L, W = float(d[0]), float(d[1])
            if L > 0 and W > 0:
                length, wid = L, W
        except ValueError:
            pass
    r = c.manual_reg_marks(length, wid)
    S.last_status = "manual read: " + r
    return {"ok": True, "result": r, "found": r.strip() == "0"}


def do_manualcut(body):
    """Cut in the registered frame after a successful manual read. No setup and no scan here -- the
    manual read established the origin and do_manualstart configured the tool."""
    c = need_cutter()
    lines = (body or "").replace("\r", "").split("\n")
    if len(lines) < 2:
        raise CutterError("No design received.")
    h = lines[0].split(",")
    try:
        mforce = int(h[0])
    except (ValueError, IndexError):
        mforce = 14
    pen = len(h) >= 4 and h[3] == "1"
    passes = 1
    if len(h) >= 5:
        try:
            passes = int(h[4])
        except ValueError:
            passes = 1
    passes = max(1, min(4, passes))
    paths, scores = split_cut_score(lines, 1, INSET)
    if not paths and not scores:
        raise CutterError("No cut paths in the design.")
    verb = "drawing " if pen else "making "
    for p in range(passes if paths else 0):
        c.cut(paths, False, lambda pct: note(verb + str(pct) + "%"), note,
              p == passes - 1 and not scores)
    if scores:
        c.set_force(score_force(mforce))
        c.cut(scores, False, lambda pct: note("scoring " + str(pct) + "%"), note, True)
    try:
        c.unload(MAT_H)
    except CutterError:
        pass
    S.last_status = "done"
    return {"ok": True}


# Routes that drive the machine. Each is called with the request body and returns a dict.
# /status is deliberately NOT here: the page polls it every 400 ms DURING a cut, so it must never
# wait on the machine lock - it only reads the status string.
MACHINE_ROUTES = {
    "/connect": lambda body: do_connect(),
    "/cut": do_cut,
    "/scan": do_scan,
    "/printcut": do_printcut,
    "/manualstart": do_manualstart,
    "/jog": do_jog,
    "/manualread": do_manualread,
    "/manualcut": do_manualcut,
    "/unload": lambda body: do_unload(),
    "/raw": do_raw,
}


# ---------------------------------------------------------------- static files
MIME = {
    ".wasm": ("application/wasm", False),
    ".onnx": ("application/octet-stream", False),
    ".js": ("text/javascript", True),
    ".mjs": ("text/javascript", True),
    ".json": ("application/json", True),
    ".png": ("image/png", False),
    ".jpg": ("image/jpeg", False),
    ".jpeg": ("image/jpeg", False),
    ".txt": ("text/plain", True),
    ".md": ("text/plain", True),
}


def find_root():
    """Where SangalaStudio.html lives. The script normally sits in tools/ inside a clone, so look
    beside it first, then one level up."""
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (here, os.path.dirname(here), os.getcwd()):
        if os.path.isfile(os.path.join(cand, "SangalaStudio.html")):
            return cand
    return None


ROOT = None


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "SangalaBridge"

    def log_message(self, fmt, *args):
        pass                                   # the routes report what matters; per-request noise hides it

    # ---- replies
    def _send(self, ctype, body, status=200, cors=False):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if cors:
            # Snap! runs on a PUBLIC site and we are a LOCAL address, so the browser treats this as
            # a private-network request: it preflights, and refuses without this grant. The POST
            # never leaves Chrome otherwise, even though curl reaches us perfectly well.
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Private-Network", "true")
            self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _json(self, obj, status=200):
        self._send("application/json; charset=utf-8", json.dumps(obj), status)

    def _read_body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n).decode("utf-8") if n else ""

    # ---- dispatch
    def do_OPTIONS(self):
        self._send("text/plain; charset=utf-8", "", cors=True)

    def do_GET(self):
        self._route("GET")

    def do_POST(self):
        self._route("POST")

    def _route(self, method):
        path = self.path.split("?", 1)[0]
        body = self._read_body()

        # ---- Snap! bridge. These routes carry DESIGNS ONLY and are the only ones that answer a
        # cross-origin caller. Nothing here moves the die cutter: a Snap! script can put a drawing
        # on the mat, but a human still has to press Make It.
        if path == "/snap/svg":
            if method == "POST":
                with S.snap_lock:
                    S.snap_svg = body
                return self._send("text/plain; charset=utf-8", "ok", cors=True)
            with S.snap_lock:                  # reading takes the drawing off the spike
                s, S.snap_svg = S.snap_svg, None
            return self._send("image/svg+xml; charset=utf-8", s or "", cors=True)

        if path == "/snap/library.xml":
            full = os.path.join(ROOT, "Sangala for Snap.xml")
            if not os.path.isfile(full):
                return self._send("text/plain; charset=utf-8",
                                  "Sangala for Snap.xml not found next to the program.", 404, cors=True)
            with open(full, "rb") as f:
                return self._send("text/xml; charset=utf-8", f.read(), cors=True)

        if path in ("/", "/index.html"):
            return self._serve_html()

        if path.startswith("/assets/"):
            return self._serve_asset(path)

        if path == "/status":
            return self._json({"status": S.last_status})

        fn = MACHINE_ROUTES.get(path)
        if fn is None:
            return self._send("text/plain; charset=utf-8", "not found", 404)

        # One job at a time on the USB pipe. The C# has no such lock because the page never issues
        # two machine calls at once; the lock makes that assumption explicit rather than lucky.
        with S.machine_lock:
            try:
                return self._json(fn(body))
            except CutterError as e:
                S.last_status = "error"
                print("  ! %s: %s" % (path, e))
                return self._json({"ok": False, "error": str(e)})
            except Exception as e:             # a bug here must not take the bridge down mid-session
                S.last_status = "error"
                import traceback
                traceback.print_exc()
                return self._json({"ok": False, "error": "%s: %s" % (type(e).__name__, e)})

    def _serve_html(self):
        full = os.path.join(ROOT, "SangalaStudio.html")
        if not os.path.isfile(full):
            return self._send("text/plain; charset=utf-8",
                              "SangalaStudio.html not found next to the program.", 500)
        with open(full, "rb") as f:            # served fresh from disk, so a page edit needs only a refresh
            self._send("text/html; charset=utf-8", f.read())

    def _serve_asset(self, path):
        assets = os.path.realpath(os.path.join(ROOT, "assets"))
        from urllib.parse import unquote
        rel = unquote(path[len("/assets/"):])
        if ".." in rel or rel.startswith("/"):
            return self._send("text/plain; charset=utf-8", "bad asset path", 400)
        full = os.path.realpath(os.path.join(assets, rel))
        if not full.startswith(assets + os.sep) or not os.path.isfile(full):
            return self._send("text/plain; charset=utf-8", "asset not found", 404)
        ctype, is_text = MIME.get(os.path.splitext(full)[1].lower(), ("application/octet-stream", False))
        # Binary types (.wasm, .onnx) must NOT carry a charset, or WebAssembly refuses to instantiate.
        with open(full, "rb") as f:
            self._send(ctype + ("; charset=utf-8" if is_text else ""), f.read())


# ---------------------------------------------------------------- startup
def main():
    global ROOT
    ROOT = find_root()
    if ROOT is None:
        print("SangalaStudio.html was not found. Run this from a clone of the repository:")
        print("    python3 tools/sangala_bridge.py")
        return 1

    httpd = None
    for port in range(8787, 8808):
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    if httpd is None:
        print("Could not open a local port (8787-8807). Is another bridge already running?")
        return 1

    httpd.daemon_threads = True
    url = "http://localhost:%d/" % httpd.server_address[1]
    print("Sangala Studio bridge")
    print("  serving %s" % ROOT)
    print("  at      %s" % url)
    print("  Press Ctrl-C to stop.")
    print()
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping.")
    finally:
        if S.cutter is not None:
            S.cutter.dispose()
    return 0


if __name__ == "__main__":
    sys.exit(main())
