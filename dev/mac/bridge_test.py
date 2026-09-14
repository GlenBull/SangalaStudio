"""Check the Mac bridge against DieCutter.cs by hand-derived expected transcripts.

No machine and no USB: the transport is faked, so what is under test is exactly the part that has
to stay identical to the C# -- the GPGL bytes.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                os.pardir, os.pardir, "tools"))
import sangala_bridge as B

fails = []


def check(name, got, want):
    if got != want:
        fails.append(name)
        print("FAIL %s\n  got  %r\n  want %r" % (name, got, want))
    else:
        print("ok   %s" % name)


class FakeCutter(B.Cutter):
    """Records every byte written; answers every status read with 'ready'."""

    def __init__(self, replies=None):
        B.Cutter.__init__(self)
        self.log = bytearray()
        self.writes = []                # each _write_raw call, kept separate: chunking is under test
        self.replies = list(replies or [])

    def _write_raw(self, b):
        self.log += b
        self.writes.append(bytes(b))

    def _read_resp(self, ms):
        if self.replies:
            return self.replies.pop(0)
        return "0"          # ready / marks found

    def transcript(self):
        """Bytes as a readable string: ETX shown as |, ESC pairs named."""
        s = self.log.decode("ascii", "replace")
        return s.replace("\x1b\x04", "<ESC EOT>").replace("\x1b\x05", "<ESC ENQ>").replace("\x03", "|")


# ---- SU: the millimetre -> Silhouette Unit conversion
check("SU(1mm)", B.SU(1), 20)
check("SU(0.9mm blade)", B.SU(0.9), 18)
check("SU(305 mat)", B.SU(305.0), 6100)
check("SU(203 width)", B.SU(203.0), 4060)
check("SU negative", B.SU(-24.1), -482)
check("SU half-to-even", (B.SU(0.025), B.SU(0.075)), (0, 2))   # 0.5 and 1.5 SU -> ties to even

# ---- Setup, against DieCutter.cs lines 191-214
c = FakeCutter()
c.setup(8, 14, False, 3, 0.9, 305.0, None)
check("setup", c.transcript(),
      "<ESC EOT>FG|TG3|FN0|TB50,0|\\0,0|Z6100,4060|FX14,1|TJ0|!8,1|FC0,1,1|FE0,1|"
      "FF1,0,1|FF1,1,1|FX14,1|TJ3|FC18,1,1|TF3,1|<ESC ENQ>")

# pen mode: FF pair differs, FC0, and no TF at all
c = FakeCutter()
c.setup(8, 14, True, 3, 0.9, 305.0, None)
check("setup (pen)", c.transcript(),
      "<ESC EOT>FG|TG3|FN0|TB50,0|\\0,0|Z6100,4060|FX14,1|TJ0|!8,1|FC0,1,1|FE0,1|"
      "FF0,0,1|FF0,0,1|FX14,1|TJ3|FC0,1,1|<ESC ENQ>")

# clamps: speed 1..30, pressure 1..33, depth 0..10
c = FakeCutter()
c.setup(99, 99, False, 99, 0.9, 305.0, None)
t = c.transcript()
check("setup clamps speed", "!30,1|" in t, True)
check("setup clamps pressure", "FX33,1|" in t, True)
check("setup clamps depth", "TF10,1|" in t, True)

# ---- Cut: y-first coordinates, duplicate points dropped, end move clear of the cut.
# DieCutter.cs lines 239-258: ONE WaitReady per chunk, then one more after the end move.
c = FakeCutter()
c.cut([[(10.0, 20.0), (30.0, 40.0), (30.0, 40.0)]], False, None, None, True)
check("cut", c.transcript(), "M400,200|D800,600|<ESC ENQ>M1000,0|<ESC ENQ>")

c = FakeCutter()
c.cut([[(10.0, 20.0), (30.0, 40.0)]], True, None, None, True)
check("cut (return to start)", c.transcript(),
      "M400,200|D800,600|<ESC ENQ>L0|\\0,0|M0,0|J0|FN0|TB50,0|<ESC ENQ>")

c = FakeCutter()
c.cut([[(1.0, 1.0)]], False, None, None, True)      # a 1-point path emits no geometry, so no chunk
check("cut (short path skipped)", c.transcript(), "M200,0|<ESC ENQ>")

# chunking: a design bigger than 1024 bytes splits on an ETX boundary, never mid-command
pts = [(float(i % 100), float(i)) for i in range(400)]
c = FakeCutter()
c.cut([pts], False, None, None, False)
data = [w for w in c.writes if w != b"\x1b\x05"]     # the design chunks, without the status polls
check("design was chunked", len(data) > 1, True)
check("every chunk within 1024", max(len(w) for w in data) <= 1024, True)
check("every chunk ends on ETX", all(w.endswith(b"\x03") for w in data), True)
check("no command was split", b"".join(data).count(b"\x03"), 400)
check("one status poll per chunk", c.writes.count(b"\x1b\x05"), len(data))

# ---- Registration, against DieCutter.cs lines 278-292
c = FakeCutter(["0"])
wid, length = B.PAGE_W - 2 * B.INSET, B.PAGE_H - 2 * B.INSET
r = c.scan_reg_marks(length, wid, B.INSET, B.INSET)
check("scan reply", r, "0")
check("scan (Portrait, eye 30)", c.transcript(),
      "TB50,0|TB99|TB52,2|TB51,400|TB53,10|TB55,1|TB123,4952,3682,118,-482|")

c = FakeCutter(["0"])
c.eye_right_mm = 0.0                                  # Cameo
c.scan_reg_marks(length, wid, B.INSET, B.INSET)
check("scan (Cameo, eye 0)", c.transcript(),
      "TB50,0|TB99|TB52,2|TB51,400|TB53,10|TB55,1|TB123,4952,3682,118,118|")

c = FakeCutter(["0"])
c.manual_reg_marks(length, wid)
check("manual read", c.transcript(),
      "TB50,0|TB99|TB52,2|TB51,400|TB53,10|TB55,1|TB23,4952,3682|")

# ---- the small ones
c = FakeCutter(); c.set_force(40);           check("set_force clamp", c.transcript(), "FX33,1|")
c = FakeCutter(); c.set_force(0);            check("set_force floor", c.transcript(), "FX1,1|")
c = FakeCutter(); c.set_blade_depth(7);      check("set_blade_depth", c.transcript(), "FY1|TF7,1|")
c = FakeCutter(); c.unload(305.0);           check("unload", c.transcript(), "<ESC ENQ>M0,0|<ESC ENQ>")
c = FakeCutter(); c.reset();                 check("reset", c.transcript(), "<ESC EOT>FG|")
c = FakeCutter(); c.move_to_mm(15.9, 15.9);  check("move_to_mm", c.transcript(), "M318,318|<ESC ENQ>")
c = FakeCutter(); c.move_to_mm(-999, -999);  check("move_to_mm clamps", c.transcript(), "M0,-1200|<ESC ENQ>")
c = FakeCutter(); c.move_to_mm(9999, 5);     check("move_to_mm clamps right", c.transcript(), "M100,4060|<ESC ENQ>")

# ---- body parsing, against SplitCutScore
cut, score = B.split_cut_score(["hdr", "1,2 3,4", "---SCORE---", "5,6 7,8"], 1, 0.0)
check("split cut", cut, [[(1.0, 2.0), (3.0, 4.0)]])
check("split score", score, [[(5.0, 6.0), (7.0, 8.0)]])
cut, score = B.split_cut_score(["hdr", "20,30 40,50"], 1, 15.9)
check("split subtracts inset", cut, [[(4.1, 14.1), (24.1, 34.1)]])
cut, score = B.split_cut_score(["hdr", "1,2", "", "3,4 5,6"], 1, 0.0)
check("split drops 1-point path", cut, [[(3.0, 4.0), (5.0, 6.0)]])
try:
    B.split_cut_score(["hdr", "1,2 bad"], 1, 0.0)
    check("split rejects bad point", "no error", "CutterError")
except B.CutterError as e:
    check("split rejects bad point", "Bad point at line 1" in str(e), True)

check("header", B.parse_header("33,8,3,0,2"), (33, 8, 3, False, 2))
check("header pen", B.parse_header("14,8,3,1"), (14, 8, 3, True, 1))
check("header clamps passes", B.parse_header("14,8,3,0,9"), (14, 8, 3, False, 4))
try:
    B.parse_header("nonsense")
    check("header rejects junk", "no error", "CutterError")
except B.CutterError:
    check("header rejects junk", True, True)

check("score_force", (B.score_force(33), B.score_force(1)), (16, 1))


# ---- zero-length packets. A bulk transfer ends on a SHORT packet, so a write that exactly fills
# its last packet leaves the transfer unterminated and the device may wait for more. Off by default;
# --zlp closes it. These drive the REAL _write_raw, which FakeCutter above deliberately bypasses.
class FakeEndpoint:
    def __init__(self, packet=64):
        self.wMaxPacketSize = packet
        self.bEndpointAddress = 0x01
        self.writes = []

    def write(self, data, timeout=None):
        self.writes.append(bytes(data))
        return len(data)


def wired(zlp, packet=64):
    c = B.Cutter(zlp=zlp)
    c._out = FakeEndpoint(packet)
    c._max_packet = packet
    return c, c._out


c, ep = wired(False); c._write_raw(b"x" * 64)
check("zlp off: exact multiple is not closed", ep.writes, [b"x" * 64])
c, ep = wired(True); c._write_raw(b"x" * 64)
check("zlp on: exact multiple is closed", ep.writes, [b"x" * 64, b""])
c, ep = wired(True); c._write_raw(b"x" * 128)
check("zlp on: two whole packets closed", ep.writes, [b"x" * 128, b""])
c, ep = wired(True); c._write_raw(b"x" * 63)
check("zlp on: short packet needs nothing", ep.writes, [b"x" * 63])
c, ep = wired(True); c._write_raw(b"x" * 65)
check("zlp on: partial second packet needs nothing", ep.writes, [b"x" * 65])
c, ep = wired(True); c._write_raw(b"")
check("zlp on: an empty write is not doubled", ep.writes, [b""])
c, ep = wired(True, 512); c._write_raw(b"x" * 512)
check("zlp on: honors a 512-byte endpoint", ep.writes, [b"x" * 512, b""])
c, ep = wired(True, 512); c._write_raw(b"x" * 64)
check("zlp on: 64 is not a multiple of 512", ep.writes, [b"x" * 64])
c, ep = wired(True); c._max_packet = 0; c._write_raw(b"x" * 64)
check("zlp on: unknown packet size does nothing", ep.writes, [b"x" * 64])

# the default must stay OFF, so the behavior already tested above is what runs unless asked
check("default is off", B.Cutter().zlp, False)
check("flag reaches the cutter", B.Cutter(zlp=True).zlp, True)

print()
print("FAILURES: %d" % len(fails))
sys.exit(1 if fails else 0)
