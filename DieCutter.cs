// DieCutter.cs - Silhouette Portrait 3/4 die cutter, no admin, no driver change.
//
// Talks straight to the cutter through the usbprint.sys device interface that
// Windows already loaded (the same method proven by the access test), so it
// needs no WinUSB/Zadig, no printer queue, no installation, and no admin.
//
// Build it once with the included "Build DieCutter.cmd" (uses the .NET
// compiler already present in Windows). After that, DieCutter.exe is a single
// portable file you can copy to any machine.
//
// Native window (no browser). SVG in, GPGL out, straight to the blade.

using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Globalization;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Xml;
using Microsoft.Win32.SafeHandles;

namespace DieCutterApp
{
    // ---------------------------------------------------------------- USB layer
    static class Native
    {
        public static Guid GUID_USBPRINT =
            new Guid("28d78fad-5a12-11d1-ae5b-0000f803a8c2");
        public const int DIGCF_PRESENT = 0x2, DIGCF_DEVICEINTERFACE = 0x10;

        [StructLayout(LayoutKind.Sequential)]
        public struct SP_DID { public int cbSize; public Guid g; public int Flags; public IntPtr Reserved; }

        [DllImport("setupapi.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        public static extern IntPtr SetupDiGetClassDevs(ref Guid c, IntPtr e, IntPtr w, int f);
        [DllImport("setupapi.dll", SetLastError = true)]
        public static extern bool SetupDiEnumDeviceInterfaces(IntPtr s, IntPtr d, ref Guid c, int i, ref SP_DID did);
        [DllImport("setupapi.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        public static extern bool SetupDiGetDeviceInterfaceDetail(IntPtr s, ref SP_DID did, IntPtr det, int size, ref int req, IntPtr dd);
        [DllImport("setupapi.dll", SetLastError = true)]
        public static extern bool SetupDiDestroyDeviceInfoList(IntPtr s);
        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        public static extern SafeFileHandle CreateFile(string n, uint a, uint sh, IntPtr sa, uint cd, uint fa, IntPtr t);
        [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();

        // Returns the device path of the first USB printer-class device whose
        // path contains the given substring (e.g. "vid_0b4d"), or null.
        public static string Find(string sub)
        {
            IntPtr h = SetupDiGetClassDevs(ref GUID_USBPRINT, IntPtr.Zero, IntPtr.Zero,
                                           DIGCF_PRESENT | DIGCF_DEVICEINTERFACE);
            if (h == (IntPtr)(-1)) return null;
            try
            {
                var did = new SP_DID(); did.cbSize = Marshal.SizeOf(did);
                for (int i = 0; SetupDiEnumDeviceInterfaces(h, IntPtr.Zero, ref GUID_USBPRINT, i, ref did); i++)
                {
                    int req = 0;
                    SetupDiGetDeviceInterfaceDetail(h, ref did, IntPtr.Zero, 0, ref req, IntPtr.Zero);
                    if (req <= 0) continue;
                    IntPtr det = Marshal.AllocHGlobal(req);
                    try
                    {
                        Marshal.WriteInt32(det, (IntPtr.Size == 8) ? 8 : 6);
                        int r2 = 0;
                        if (SetupDiGetDeviceInterfaceDetail(h, ref did, det, req, ref r2, IntPtr.Zero))
                        {
                            string p = Marshal.PtrToStringUni((IntPtr)(det.ToInt64() + 4));
                            if (p != null && (sub == null || p.ToLowerInvariant().Contains(sub)))
                                return p;
                        }
                    }
                    finally { Marshal.FreeHGlobal(det); }
                }
            }
            finally { SetupDiDestroyDeviceInfoList(h); }
            return null;
        }
    }

    // ---------------------------------------------------------------- cutter
    class Cutter : IDisposable
    {
        const byte ETX = 0x03, ESC = 0x1b, ENQ = 0x05, EOT = 0x04;
        FileStream _fs;
        public string ModelName = "Silhouette Portrait";
        public double WidthMm = 203.0;   // Portrait 3 usable width
        public string MatTG = "3";       // 8x12 mat

        static int SU(double mm) { return (int)Math.Round(mm * 20.0); }

        public void Open()
        {
            string path = Native.Find("vid_0b4d");
            if (path == null)
                throw new IOException("Die Cutter not found. Is it powered on and connected by USB, and is Silhouette Studio closed?");
            if (path.ToLowerInvariant().Contains("pid_113f")) { ModelName = "Silhouette Portrait 4"; WidthMm = 216.0; MatTG = "11"; }
            else { ModelName = "Silhouette Portrait 3"; WidthMm = 203.0; MatTG = "3"; }

            const uint GENERIC_RW = 0x80000000u | 0x40000000u;
            const uint SHARE_RW = 0x3, OPEN_EXISTING = 3, OVERLAPPED = 0x40000000u;
            var h = Native.CreateFile(path, GENERIC_RW, SHARE_RW, IntPtr.Zero, OPEN_EXISTING, OVERLAPPED, IntPtr.Zero);
            if (h.IsInvalid)
            {
                int e = Marshal.GetLastWin32Error();
                throw new IOException(e == 5
                    ? "Access denied opening the Die Cutter. This machine's policy blocks direct access."
                    : (e == 32
                        ? "The Die Cutter is busy - close Silhouette Studio (and any earlier tool), then retry."
                        : ("Could not open the Die Cutter (Windows error " + e + ").")));
            }
            _fs = new FileStream(h, FileAccess.ReadWrite, 1, true);
        }

        void WriteRaw(byte[] b) { if (!_fs.WriteAsync(b, 0, b.Length).Wait(8000)) throw new IOException("write timed out"); }
        void WriteCmds(IEnumerable<string> cmds)
        {
            var ms = new MemoryStream();
            foreach (var c in cmds) { var d = Encoding.ASCII.GetBytes(c); ms.Write(d, 0, d.Length); ms.WriteByte(ETX); }
            WriteRaw(ms.ToArray());
        }
        void WriteCmd(string c) { WriteCmds(new[] { c }); }

        string ReadResp(int ms)
        {
            var buf = new byte[64];
            var t = _fs.ReadAsync(buf, 0, buf.Length);
            if (!t.Wait(ms) || t.Result <= 0) return null;
            return Encoding.ASCII.GetString(buf, 0, t.Result).TrimEnd((char)ETX, (char)0, ' ');
        }

        public string Firmware()
        {
            WriteCmd("FG");
            return ReadResp(3000) ?? "(no response)";
        }

        string Status()
        {
            WriteRaw(new byte[] { ESC, ENQ });
            string r = ReadResp(2000);
            if (r == "0") return "ready";
            if (r == "1") return "moving";
            if (r == "2") return "unloaded";
            return r ?? "?";
        }

        public void WaitReady(Action<string> note, int timeoutMs = 120000)
        {
            var end = Environment.TickCount + timeoutMs;
            while (Environment.TickCount < end)
            {
                string s = Status();
                if (s == "ready") return;
                if (s == "unloaded" && note != null) note("Load the mat into the Die Cutter...");
                Thread.Sleep(60);
            }
            throw new IOException("Die Cutter never became ready");
        }

        public void Setup(int speed, int pressure, bool pen, int depth, double bladeMm, double mediaLenMm, Action<string> note)
        {
            speed = Math.Max(1, Math.Min(30, speed));
            pressure = Math.Max(1, Math.Min(33, pressure));
            WriteRaw(new byte[] { ESC, EOT });            // initialize
            Firmware();                                    // drain version reply
            WriteCmd("TG" + MatTG);
            WriteCmds(new[] { "FN0", "TB50,0" });
            WriteCmds(new[] { "\\0,0", "Z" + SU(mediaLenMm) + "," + SU(WidthMm) });
            WriteCmd("FX" + pressure + ",1");
            WriteCmd("TJ0");
            WriteCmd("!" + speed + ",1");
            WriteCmd("FC0,1,1");
            WriteCmd("FE0,1");
            if (pen) WriteCmds(new[] { "FF0,0,1", "FF0,0,1" });
            else WriteCmds(new[] { "FF1,0,1", "FF1,1,1" });
            WriteCmd("FX" + pressure + ",1");
            WriteCmd("TJ3");
            WriteCmd("FC" + (pen ? 0 : SU(bladeMm)) + ",1,1");
            // NOTE: AutoBlade reset (FY1) removed from Setup -- it runs before the
            // registration scan and disturbed it. Blade depth is set separately.
            if (!pen && depth > 0) WriteCmd("TF" + Math.Max(0, Math.Min(10, depth)) + ",1");
            WaitReady(note);
        }

        // paths: list of point arrays in mm (x across carriage, y feed direction)
        public void Cut(List<PointF[]> paths, bool returnToStart, Action<int> progress, Action<string> note, bool emitEnd = true)
        {
            var cmds = new List<string>();
            double maxY = 0;
            foreach (var p in paths)
            {
                if (p.Length < 2) continue;
                string last = SU(p[0].Y) + "," + SU(p[0].X);
                cmds.Add("M" + last);
                for (int i = 1; i < p.Length; i++)
                {
                    string pt = SU(p[i].Y) + "," + SU(p[i].X);
                    if (pt != last) { cmds.Add("D" + pt); last = pt; }
                    if (p[i].Y > maxY) maxY = p[i].Y;
                }
                if (p[0].Y > maxY) maxY = p[0].Y;
            }

            var ms = new MemoryStream();
            foreach (var c in cmds) { var d = Encoding.ASCII.GetBytes(c); ms.Write(d, 0, d.Length); ms.WriteByte(ETX); }
            byte[] data = ms.ToArray();

            int off = 0;
            while (off < data.Length)
            {
                int len = Math.Min(1024, data.Length - off);
                int cut = len;                             // trim to last ETX boundary
                for (int i = off + len - 1; i >= off; i--) { if (data[i] == ETX) { cut = i - off + 1; break; } }
                var chunk = new byte[cut];
                Array.Copy(data, off, chunk, 0, cut);
                WriteRaw(chunk);
                WaitReady(note);
                off += cut;
                if (progress != null) progress((int)(100L * off / Math.Max(1, data.Length)));
            }

            if (emitEnd)
            {
                if (returnToStart) WriteCmds(new[] { "L0", "\\0,0", "M0,0", "J0", "FN0", "TB50,0" });
                else WriteCmds(new[] { "M" + SU(maxY + 10) + ",0", "SO0" });
                WaitReady(note);
            }
        }

        // Experimental: print-and-cut registration scan (Cameo/Portrait GPGL).
        // Returns the machine's reply -- "0" means the marks were found.
        // TB123,height,width,top,left. height=reglength (Y distance between
        // marks), width=regwidth (X distance), top/left = the FIRST-mark search
        // start = mark origin minus a 10 mm search range. This mirrors exactly
        // the reverse-engineered Silhouette driver (fablabnbg/inkscape-silhouette
        // Graphtec.py: automatic_regmark_test_mm_cmd, origin - 10). Keep 10.
        public string ScanRegMarks(double lenMm, double widMm, double oxMm, double oyMm, double approachMm = 10, double eyeRightMm = 30)
        {
            // Caller must Setup() first (init + mat + boundary) so the machine has a coordinate frame.
            WriteCmd("TB50,0"); WriteCmd("TB99"); WriteCmd("TB52,2");   // type 2 = Cameo/Portrait
            WriteCmd("TB51,400"); WriteCmd("TB53,10"); WriteCmd("TB55,1"); // 20mm long, 0.5mm thick
            // The optical eye sits ~eyeRightMm to the RIGHT of the blade. The firmware
            // aims the blade, so start the search that much further LEFT (may go negative,
            // into the left margin) so the eye actually reaches the top-left square.
            double startY = Math.Max(oyMm - approachMm, 0);
            double startX = oxMm - approachMm - eyeRightMm;
            WriteCmd("TB123," + SU(lenMm) + "," + SU(widMm) + "," + SU(startY) + "," + SU(startX));
            string r = ReadResp(60000);          // "    0" = found
            return r == null ? "(no response)" : r.Trim();
        }

        // Change the tool force between passes (e.g. a lighter pass to score/crease).
        public void SetForce(int f) { WriteCmd("FX" + Math.Max(1, Math.Min(33, f)) + ",1"); }

        // Return the media to the front (load) position at the end of a job. FO fed
        // the wrong way, so use the origin return, which brings the mat forward.
        public void Unload(double mediaLenMm)
        {
            WaitReady(null);
            WriteCmds(new[] { "\\0,0", "M0,0", "FN0" });
            WaitReady(null);
        }

        // Set just the AutoBlade depth mid-job (reset then tap to depth) -- used to
        // drop to a shallow depth for a fold crease so it doesn't cut through.
        public void SetBladeDepth(int d)
        {
            WriteCmd("FY1");
            WriteCmd("TF" + Math.Max(1, Math.Min(10, d)) + ",1");
        }

        // Jog the tool head (pen UP) to an absolute position in mm. Caller must
        // Setup() first. Used by manual registration so the user can drive the
        // tool over the top-left square mark while watching it.
        public void MoveToMm(double xMm, double yMm)
        {
            // Allow x LEFT of the logical origin: the optical eye sits ~30mm right
            // of the blade, so reaching a left-edge mark needs the carriage in the
            // left margin (negative x). Studio drives it there too.
            double x = Math.Max(-60, Math.Min(WidthMm, xMm));
            double y = Math.Max(0, yMm);
            WriteCmd("M" + SU(y) + "," + SU(x));
            WaitReady(null);
        }

        // Manual print-and-cut registration. The caller has already jogged the
        // head so the tool sits over the top-left SQUARE mark. The machine reads
        // that mark from the current position, then locates the other two using
        // the mark spacing (lenMm down, widMm across). TB23 = manual regmark test
        // (fablabnbg/inkscape-silhouette Graphtec.py: manual_regmark_mm_cmd).
        // Same setup block as the automatic scan; only TB123 -> TB23 changes.
        // Returns the machine reply -- "0" means the marks were found.
        public string ManualRegMarks(double lenMm, double widMm)
        {
            WriteCmd("TB50,0"); WriteCmd("TB99"); WriteCmd("TB52,2");   // type 2 = Cameo/Portrait
            WriteCmd("TB51,400"); WriteCmd("TB53,10"); WriteCmd("TB55,1"); // 20mm long, 0.5mm thick
            WriteCmd("TB23," + SU(lenMm) + "," + SU(widMm));           // manual: read from current head position
            string r = ReadResp(60000);
            return r == null ? "(no response)" : r.Trim();
        }

        public void Dispose() { if (_fs != null) { try { _fs.Dispose(); } catch { } _fs = null; } }
    }

    // ---------------------------------------------------------------- SVG
    static class Svg
    {
        // Load an SVG file and return polylines in millimetres.
        public static List<PointF[]> Load(string file)
        {
            var doc = new XmlDocument();
            doc.Load(file);
            var svg = doc.DocumentElement;
            if (svg == null || svg.LocalName != "svg") throw new Exception("Not an SVG file.");

            double vbMinX = 0, vbMinY = 0, vbW = 0, vbH = 0;
            string vb = Attr(svg, "viewBox");
            if (vb != null)
            {
                var t = vb.Split(new[] { ' ', ',', '\t', '\n' }, StringSplitOptions.RemoveEmptyEntries);
                if (t.Length == 4) { vbMinX = D(t[0]); vbMinY = D(t[1]); vbW = D(t[2]); vbH = D(t[3]); }
            }
            double wMm = LenMm(Attr(svg, "width"));
            double hMm = LenMm(Attr(svg, "height"));
            double sx, sy;
            if (vbW > 0 && wMm > 0) sx = wMm / vbW; else sx = 25.4 / 96.0;
            if (vbH > 0 && hMm > 0) sy = hMm / vbH; else sy = 25.4 / 96.0;
            // root matrix: scale then shift viewBox origin to 0,0
            double[] root = Mul(new double[] { sx, 0, 0, sy, 0, 0 },
                                new double[] { 1, 0, 0, 1, -vbMinX, -vbMinY });

            var outp = new List<PointF[]>();
            Walk(svg, root, outp);
            return outp;
        }

        static void Walk(XmlNode node, double[] ctm, List<PointF[]> outp)
        {
            foreach (XmlNode ch in node.ChildNodes)
            {
                if (ch.NodeType != XmlNodeType.Element) continue;
                var e = (XmlElement)ch;
                double[] m = ctm;
                string tr = Attr(e, "transform");
                if (tr != null) m = Mul(ctm, ParseTransform(tr));

                switch (e.LocalName)
                {
                    case "g": case "svg": case "a": Walk(e, m, outp); break;
                    case "path": Emit(FlattenPath(Attr(e, "d")), m, outp); break;
                    case "rect": Emit(RectPts(e), m, outp); break;
                    case "circle": Emit(EllipsePts(D(Attr(e, "cx")), D(Attr(e, "cy")), D(Attr(e, "r")), D(Attr(e, "r"))), m, outp); break;
                    case "ellipse": Emit(EllipsePts(D(Attr(e, "cx")), D(Attr(e, "cy")), D(Attr(e, "rx")), D(Attr(e, "ry"))), m, outp); break;
                    case "line": Emit(new List<List<PointF>> { new List<PointF> { new PointF((float)D(Attr(e, "x1")), (float)D(Attr(e, "y1"))), new PointF((float)D(Attr(e, "x2")), (float)D(Attr(e, "y2"))) } }, m, outp); break;
                    case "polyline": case "polygon": Emit(PolyPts(Attr(e, "points"), e.LocalName == "polygon"), m, outp); break;
                    default: Walk(e, m, outp); break;   // descend unknown containers
                }
            }
        }

        static void Emit(List<List<PointF>> subpaths, double[] m, List<PointF[]> outp)
        {
            if (subpaths == null) return;
            foreach (var sp in subpaths)
            {
                if (sp.Count < 2) continue;
                var arr = new PointF[sp.Count];
                for (int i = 0; i < sp.Count; i++)
                {
                    double x = m[0] * sp[i].X + m[2] * sp[i].Y + m[4];
                    double y = m[1] * sp[i].X + m[3] * sp[i].Y + m[5];
                    arr[i] = new PointF((float)x, (float)y);
                }
                outp.Add(arr);
            }
        }

        // -------- shape helpers (return list of subpaths in local units) ------
        static List<List<PointF>> RectPts(XmlElement e)
        {
            double x = D(Attr(e, "x")), y = D(Attr(e, "y")), w = D(Attr(e, "width")), h = D(Attr(e, "height"));
            var l = new List<PointF> {
                new PointF((float)x,(float)y), new PointF((float)(x+w),(float)y),
                new PointF((float)(x+w),(float)(y+h)), new PointF((float)x,(float)(y+h)), new PointF((float)x,(float)y) };
            return new List<List<PointF>> { l };
        }
        static List<List<PointF>> EllipsePts(double cx, double cy, double rx, double ry)
        {
            var l = new List<PointF>(); int n = 96;
            for (int i = 0; i <= n; i++) { double a = 2 * Math.PI * i / n; l.Add(new PointF((float)(cx + rx * Math.Cos(a)), (float)(cy + ry * Math.Sin(a)))); }
            return new List<List<PointF>> { l };
        }
        static List<List<PointF>> PolyPts(string s, bool close)
        {
            var nums = Nums(s); var l = new List<PointF>();
            for (int i = 0; i + 1 < nums.Count; i += 2) l.Add(new PointF((float)nums[i], (float)nums[i + 1]));
            if (close && l.Count > 0) l.Add(l[0]);
            return new List<List<PointF>> { l };
        }

        // -------- SVG path 'd' flattening -------------------------------------
        static List<List<PointF>> FlattenPath(string d)
        {
            var outp = new List<List<PointF>>();
            if (string.IsNullOrEmpty(d)) return outp;
            var sc = new PathScanner(d);
            double cx = 0, cy = 0, sx = 0, sy = 0;   // current, subpath start
            double lastCx = 0, lastCy = 0; char lastCmd = ' ';
            List<PointF> cur = null;
            char cmd = ' ';
            while (sc.More())
            {
                char c = sc.PeekCmd();
                if (c != '\0') { cmd = sc.ReadCmd(); }
                bool rel = char.IsLower(cmd);
                char C = char.ToUpper(cmd);
                switch (C)
                {
                    case 'M':
                        {
                            double x = sc.Num(), y = sc.Num();
                            if (rel) { x += cx; y += cy; }
                            cx = x; cy = y; sx = x; sy = y;
                            cur = new List<PointF> { new PointF((float)x, (float)y) };
                            outp.Add(cur);
                            cmd = rel ? 'l' : 'L';   // subsequent implicit lineto
                            break;
                        }
                    case 'L':
                        {
                            double x = sc.Num(), y = sc.Num(); if (rel) { x += cx; y += cy; }
                            cx = x; cy = y; if (cur != null) cur.Add(new PointF((float)x, (float)y));
                            break;
                        }
                    case 'H':
                        {
                            double x = sc.Num(); if (rel) x += cx; cx = x;
                            if (cur != null) cur.Add(new PointF((float)cx, (float)cy));
                            break;
                        }
                    case 'V':
                        {
                            double y = sc.Num(); if (rel) y += cy; cy = y;
                            if (cur != null) cur.Add(new PointF((float)cx, (float)cy));
                            break;
                        }
                    case 'C':
                        {
                            double x1 = sc.Num(), y1 = sc.Num(), x2 = sc.Num(), y2 = sc.Num(), x = sc.Num(), y = sc.Num();
                            if (rel) { x1 += cx; y1 += cy; x2 += cx; y2 += cy; x += cx; y += cy; }
                            Cubic(cur, cx, cy, x1, y1, x2, y2, x, y);
                            lastCx = x2; lastCy = y2; cx = x; cy = y;
                            break;
                        }
                    case 'S':
                        {
                            double x1, y1;
                            if (lastCmd == 'C' || lastCmd == 'S') { x1 = 2 * cx - lastCx; y1 = 2 * cy - lastCy; } else { x1 = cx; y1 = cy; }
                            double x2 = sc.Num(), y2 = sc.Num(), x = sc.Num(), y = sc.Num();
                            if (rel) { x2 += cx; y2 += cy; x += cx; y += cy; }
                            Cubic(cur, cx, cy, x1, y1, x2, y2, x, y);
                            lastCx = x2; lastCy = y2; cx = x; cy = y;
                            break;
                        }
                    case 'Q':
                        {
                            double x1 = sc.Num(), y1 = sc.Num(), x = sc.Num(), y = sc.Num();
                            if (rel) { x1 += cx; y1 += cy; x += cx; y += cy; }
                            Quad(cur, cx, cy, x1, y1, x, y);
                            lastCx = x1; lastCy = y1; cx = x; cy = y;
                            break;
                        }
                    case 'T':
                        {
                            double x1, y1;
                            if (lastCmd == 'Q' || lastCmd == 'T') { x1 = 2 * cx - lastCx; y1 = 2 * cy - lastCy; } else { x1 = cx; y1 = cy; }
                            double x = sc.Num(), y = sc.Num(); if (rel) { x += cx; y += cy; }
                            Quad(cur, cx, cy, x1, y1, x, y);
                            lastCx = x1; lastCy = y1; cx = x; cy = y;
                            break;
                        }
                    case 'A':
                        {
                            double rx = sc.Num(), ry = sc.Num(), rot = sc.Num();
                            int laf = sc.Flag(), swf = sc.Flag();
                            double x = sc.Num(), y = sc.Num(); if (rel) { x += cx; y += cy; }
                            Arc(cur, cx, cy, rx, ry, rot, laf, swf, x, y);
                            cx = x; cy = y;
                            break;
                        }
                    case 'Z':
                        {
                            if (cur != null) cur.Add(new PointF((float)sx, (float)sy));
                            cx = sx; cy = sy;
                            break;
                        }
                    default: return outp;   // unknown -> stop
                }
                lastCmd = C;
            }
            return outp;
        }

        static void Cubic(List<PointF> o, double x0, double y0, double x1, double y1, double x2, double y2, double x3, double y3)
        {
            if (o == null) return;
            int n = 36;
            for (int i = 1; i <= n; i++)
            {
                double t = (double)i / n, u = 1 - t;
                double bx = u * u * u * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t * t * t * x3;
                double by = u * u * u * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t * t * t * y3;
                o.Add(new PointF((float)bx, (float)by));
            }
        }
        static void Quad(List<PointF> o, double x0, double y0, double x1, double y1, double x2, double y2)
        {
            if (o == null) return;
            int n = 28;
            for (int i = 1; i <= n; i++)
            {
                double t = (double)i / n, u = 1 - t;
                double bx = u * u * x0 + 2 * u * t * x1 + t * t * x2;
                double by = u * u * y0 + 2 * u * t * y1 + t * t * y2;
                o.Add(new PointF((float)bx, (float)by));
            }
        }
        static void Arc(List<PointF> o, double x0, double y0, double rx, double ry, double rotDeg, int laf, int swf, double x, double y)
        {
            if (o == null) return;
            if (rx == 0 || ry == 0) { o.Add(new PointF((float)x, (float)y)); return; }
            rx = Math.Abs(rx); ry = Math.Abs(ry);
            double phi = rotDeg * Math.PI / 180.0, cosP = Math.Cos(phi), sinP = Math.Sin(phi);
            double dx = (x0 - x) / 2, dy = (y0 - y) / 2;
            double x1p = cosP * dx + sinP * dy, y1p = -sinP * dx + cosP * dy;
            double l = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry);
            if (l > 1) { double s = Math.Sqrt(l); rx *= s; ry *= s; }
            double num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p;
            double den = rx * rx * y1p * y1p + ry * ry * x1p * x1p;
            double co = Math.Sqrt(Math.Max(0, num / den));
            if (laf == swf) co = -co;
            double cxp = co * rx * y1p / ry, cyp = -co * ry * x1p / rx;
            double ccx = cosP * cxp - sinP * cyp + (x0 + x) / 2;
            double ccy = sinP * cxp + cosP * cyp + (y0 + y) / 2;
            double a1 = Ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry);
            double ad = Ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry);
            if (swf == 0 && ad > 0) ad -= 2 * Math.PI;
            if (swf == 1 && ad < 0) ad += 2 * Math.PI;
            int n = Math.Max(8, (int)(Math.Abs(ad) / (Math.PI / 32)));
            for (int i = 1; i <= n; i++)
            {
                double a = a1 + ad * i / n;
                double px = cosP * rx * Math.Cos(a) - sinP * ry * Math.Sin(a) + ccx;
                double py = sinP * rx * Math.Cos(a) + cosP * ry * Math.Sin(a) + ccy;
                o.Add(new PointF((float)px, (float)py));
            }
        }
        static double Ang(double ux, double uy, double vx, double vy)
        {
            double dot = ux * vx + uy * vy, len = Math.Sqrt((ux * ux + uy * uy) * (vx * vx + vy * vy));
            double a = Math.Acos(Math.Max(-1, Math.Min(1, dot / len)));
            if (ux * vy - uy * vx < 0) a = -a;
            return a;
        }

        // -------- transform + number parsing ----------------------------------
        static double[] ParseTransform(string s)
        {
            double[] m = { 1, 0, 0, 1, 0, 0 };
            int i = 0;
            while (i < s.Length)
            {
                int op = i; while (op < s.Length && (char.IsLetter(s[op]))) op++;
                string name = s.Substring(i, op - i).Trim();
                int lp = s.IndexOf('(', op); if (lp < 0) break;
                int rp = s.IndexOf(')', lp); if (rp < 0) break;
                var a = Nums(s.Substring(lp + 1, rp - lp - 1));
                double[] t = { 1, 0, 0, 1, 0, 0 };
                switch (name)
                {
                    case "matrix": if (a.Count == 6) t = new[] { a[0], a[1], a[2], a[3], a[4], a[5] }; break;
                    case "translate": t = new double[] { 1, 0, 0, 1, a.Count > 0 ? a[0] : 0, a.Count > 1 ? a[1] : 0 }; break;
                    case "scale": { double sxv = a.Count > 0 ? a[0] : 1, syv = a.Count > 1 ? a[1] : sxv; t = new double[] { sxv, 0, 0, syv, 0, 0 }; } break;
                    case "rotate":
                        {
                            double ang = (a.Count > 0 ? a[0] : 0) * Math.PI / 180.0, cs = Math.Cos(ang), sn = Math.Sin(ang);
                            if (a.Count >= 3) { double[] t1 = { 1, 0, 0, 1, a[1], a[2] }, r = { cs, sn, -sn, cs, 0, 0 }, t2 = { 1, 0, 0, 1, -a[1], -a[2] }; t = Mul(Mul(t1, r), t2); }
                            else t = new double[] { cs, sn, -sn, cs, 0, 0 };
                        } break;
                    case "skewX": { double tn = Math.Tan((a.Count > 0 ? a[0] : 0) * Math.PI / 180.0); t = new double[] { 1, 0, tn, 1, 0, 0 }; } break;
                    case "skewY": { double tn = Math.Tan((a.Count > 0 ? a[0] : 0) * Math.PI / 180.0); t = new double[] { 1, tn, 0, 1, 0, 0 }; } break;
                }
                m = Mul(m, t);
                i = rp + 1;
            }
            return m;
        }
        // compose: apply b after a's frame  (result = a o b)
        static double[] Mul(double[] a, double[] b)
        {
            return new double[] {
                a[0]*b[0] + a[2]*b[1],
                a[1]*b[0] + a[3]*b[1],
                a[0]*b[2] + a[2]*b[3],
                a[1]*b[2] + a[3]*b[3],
                a[0]*b[4] + a[2]*b[5] + a[4],
                a[1]*b[4] + a[3]*b[5] + a[5] };
        }

        static string Attr(XmlElement e, string n) { var a = e.GetAttribute(n); return string.IsNullOrEmpty(a) ? null : a; }
        static string Attr(XmlNode e, string n) { return e is XmlElement ? Attr((XmlElement)e, n) : null; }
        static double D(string s) { double v; return (s != null && double.TryParse(s.Trim().TrimEnd('%'), NumberStyles.Any, CultureInfo.InvariantCulture, out v)) ? v : 0; }
        static List<double> Nums(string s)
        {
            var l = new List<double>(); if (s == null) return l;
            foreach (System.Text.RegularExpressions.Match mm in System.Text.RegularExpressions.Regex.Matches(s, @"[-+]?(\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?"))
                l.Add(double.Parse(mm.Value, CultureInfo.InvariantCulture));
            return l;
        }
        static double LenMm(string s)
        {
            if (s == null) return 0;
            s = s.Trim(); double v;
            string unit = "";
            int k = 0; while (k < s.Length && (char.IsDigit(s[k]) || s[k] == '.' || s[k] == '-' || s[k] == '+' || s[k] == 'e' || s[k] == 'E')) k++;
            if (!double.TryParse(s.Substring(0, k), NumberStyles.Any, CultureInfo.InvariantCulture, out v)) return 0;
            unit = s.Substring(k).Trim().ToLowerInvariant();
            switch (unit) { case "mm": return v; case "cm": return v * 10; case "in": return v * 25.4; case "pt": return v * 25.4 / 72; case "pc": return v * 25.4 / 6; default: return v * 25.4 / 96; }
        }
    }

    // scanner for path 'd' data
    class PathScanner
    {
        string s; int i;
        public PathScanner(string d) { s = d; i = 0; }
        void Skip() { while (i < s.Length && (s[i] == ' ' || s[i] == ',' || s[i] == '\t' || s[i] == '\n' || s[i] == '\r')) i++; }
        public bool More() { Skip(); return i < s.Length; }
        public char PeekCmd() { Skip(); if (i < s.Length && char.IsLetter(s[i])) return s[i]; return '\0'; }
        public char ReadCmd() { Skip(); return s[i++]; }
        public int Flag() { Skip(); char c = s[i++]; return c == '1' ? 1 : 0; }
        public double Num()
        {
            Skip();
            int st = i;
            if (i < s.Length && (s[i] == '-' || s[i] == '+')) i++;
            while (i < s.Length && (char.IsDigit(s[i]) || s[i] == '.')) i++;
            if (i < s.Length && (s[i] == 'e' || s[i] == 'E')) { i++; if (i < s.Length && (s[i] == '-' || s[i] == '+')) i++; while (i < s.Length && char.IsDigit(s[i])) i++; }
            double v; double.TryParse(s.Substring(st, i - st), NumberStyles.Any, CultureInfo.InvariantCulture, out v);
            return v;
        }
    }

    // ---------------------------------------------------------------- UI
    class MainForm : Form
    {
        Cutter _cutter;
        List<PointF[]> _design = new List<PointF[]>();     // normalized to origin, mm
        Button _connect, _open, _test, _cut;
        ComboBox _material;
        NumericUpDown _force, _speed, _depth, _offx, _offy, _scale;
        Label _status;
        Panel _preview, _host;
        ProgressBar _bar;
        const double MAT_H = 305;
        const string Ver = "1.2";

        class Mat { public int f, s, d; public bool pen; public Mat(int f, int s, int d, bool p) { this.f = f; this.s = s; this.d = d; pen = p; } }
        static readonly Dictionary<string, Mat> MATS = new Dictionary<string, Mat> {
            {"Paper", new Mat(14,8,3,false)}, {"Cardstock", new Mat(22,5,6,false)},
            {"Vinyl", new Mat(10,8,1,false)}, {"Pen (draw)", new Mat(12,8,0,true)} };

        public MainForm()
        {
            Text = "Sangala Studio  -  v" + Ver;
            Width = 940; Height = 700; StartPosition = FormStartPosition.CenterScreen;
            Font = new Font("Segoe UI", 9);
            BackColor = Color.FromArgb(245, 236, 214);

            // header banner
            var header = new Panel { Dock = DockStyle.Top, Height = 66, BackColor = Color.FromArgb(63, 107, 142) };
            header.Controls.Add(new Label { Text = "Sangala Studio", AutoSize = true, ForeColor = Color.White,
                Left = 16, Top = 8, Font = new Font("Segoe Print", 22, FontStyle.Bold) });
            header.Controls.Add(new Label { Text = "Digital Fabrication Tool", AutoSize = true,
                ForeColor = Color.FromArgb(205, 222, 236), Left = 20, Top = 46, Font = new Font("Segoe UI", 8) });
            _host = new Panel { Dock = DockStyle.Fill, BackColor = Color.FromArgb(245, 236, 214) };
            Controls.Add(_host);
            Controls.Add(header);

            _connect = MkButton("Connect to Die Cutter", 12, 12, 168); _connect.Click += (a, b) => DoConnect();
            _open = MkButton("Open SVG...", 188, 12, 110); _open.Click += (a, b) => DoOpen();
            _test = MkButton("Test square", 306, 12, 100); _test.Click += (a, b) => { _design = new List<PointF[]> { new[] { new PointF(0, 0), new PointF(30, 0), new PointF(30, 30), new PointF(0, 30), new PointF(0, 0) } }; _preview.Invalidate(); SetStatus("Test square loaded (30 mm)."); };
            Style(_connect, Color.FromArgb(47, 106, 168));
            Style(_open, Color.FromArgb(47, 106, 168));
            Style(_test, Color.FromArgb(180, 120, 60));

            AddLabel("Material", 12, 52);
            _material = new ComboBox { Left = 80, Top = 48, Width = 130, DropDownStyle = ComboBoxStyle.DropDownList };
            foreach (var k in MATS.Keys) _material.Items.Add(k);
            _material.SelectedIndex = 0; _material.SelectedIndexChanged += (a, b) => ApplyMaterial();
            _host.Controls.Add(_material);

            Label d1, d2, d3;
            _force = MkNum("Force", 230, 48, 1, 33, 14, out d1);
            _speed = MkNum("Speed", 360, 48, 1, 30, 8, out d2);
            _depth = MkNum("Blade", 490, 48, 0, 10, 3, out d3);

            AddLabel("From left", 12, 84); _offx = MkNumRaw(80, 80, 0, 210, 10);
            AddLabel("From top", 150, 84); _offy = MkNumRaw(214, 80, 0, 300, 10);
            AddLabel("Scale %", 290, 84); _scale = MkNumRaw(345, 80, 10, 1000, 100);
            _offx.ValueChanged += (a, b) => _preview.Invalidate();
            _offy.ValueChanged += (a, b) => _preview.Invalidate();
            _scale.ValueChanged += (a, b) => _preview.Invalidate();

            _preview = new Panel { Left = 12, Top = 118, Width = 470, Height = 470, BorderStyle = BorderStyle.FixedSingle, BackColor = Color.White };
            _preview.Paint += DrawPreview; _host.Controls.Add(_preview);

            _cut = MkButton("Make it!", 520, 120, 360); _cut.Height = 62; _cut.Enabled = false;
            _cut.Font = new Font("Segoe UI", 15, FontStyle.Bold);
            Style(_cut, Color.FromArgb(22, 150, 70)); _cut.FlatAppearance.BorderColor = Color.FromArgb(15, 110, 52);
            _cut.Click += (a, b) => DoCut();

            _bar = new ProgressBar { Left = 520, Top = 194, Width = 360, Height = 14 }; _host.Controls.Add(_bar);
            _status = new Label { Left = 520, Top = 220, Width = 380, Height = 340, Text = "Not connected.", Font = new Font("Segoe UI", 10) }; _host.Controls.Add(_status);

            ApplyMaterial();
        }

        Button MkButton(string t, int x, int y, int w) { var b = new Button { Text = t, Left = x, Top = y, Width = w, Height = 32 }; _host.Controls.Add(b); return b; }
        void AddLabel(string t, int x, int y) { _host.Controls.Add(new Label { Text = t, Left = x, Top = y + 3, Width = 66, AutoSize = true }); }
        NumericUpDown MkNum(string label, int x, int y, int min, int max, int val, out Label lbl) { lbl = new Label { Text = label, Left = x, Top = y + 3, AutoSize = true }; _host.Controls.Add(lbl); var n = new NumericUpDown { Left = x + 46, Top = y, Width = 55, Minimum = min, Maximum = max, Value = val }; _host.Controls.Add(n); return n; }
        NumericUpDown MkNumRaw(int x, int y, int min, int max, int val) { var n = new NumericUpDown { Left = x, Top = y, Width = 58, Minimum = min, Maximum = max, Value = val }; _host.Controls.Add(n); return n; }
        void Style(Button b, Color bg) { b.FlatStyle = FlatStyle.Flat; b.BackColor = bg; b.ForeColor = Color.White; b.FlatAppearance.BorderColor = ControlPaint.Dark(bg); b.FlatAppearance.BorderSize = 1; b.Cursor = Cursors.Hand; if (b.Font.Bold == false) b.Font = new Font("Segoe UI", 9, FontStyle.Bold); }

        void ApplyMaterial() { var m = MATS[(string)_material.SelectedItem]; _force.Value = m.f; _speed.Value = m.s; _depth.Value = m.d; }
        void SetStatus(string s) { if (InvokeRequired) BeginInvoke((Action)(() => _status.Text = s)); else _status.Text = s; }

        void DoConnect()
        {
            try
            {
                if (_cutter != null) { _cutter.Dispose(); _cutter = null; }
                _cutter = new Cutter(); _cutter.Open();
                string fw = _cutter.Firmware();
                SetStatus("Connected to " + _cutter.ModelName + ".\r\nFirmware: " + fw);
                Text = "Sangala Studio  -  " + _cutter.ModelName;
                _cut.Enabled = true; _preview.Invalidate();
            }
            catch (Exception ex) { _cut.Enabled = false; SetStatus("Could not connect:\r\n" + ex.Message); }
        }

        void DoOpen()
        {
            using (var d = new OpenFileDialog { Filter = "SVG files (*.svg)|*.svg|All files (*.*)|*.*" })
                if (d.ShowDialog() == DialogResult.OK)
                {
                    try
                    {
                        var raw = Svg.Load(d.FileName);
                        if (raw.Count == 0) { SetStatus("No shapes found in that SVG."); return; }
                        _design = Normalize(raw);
                        _preview.Invalidate();
                        var bb = BBox(_design);
                        SetStatus("Loaded " + _design.Count + " shape(s), " + Math.Round(bb.Width, 1) + " x " + Math.Round(bb.Height, 1) + " mm.");
                    }
                    catch (Exception ex) { SetStatus("Could not read SVG:\r\n" + ex.Message); }
                }
        }

        static List<PointF[]> Normalize(List<PointF[]> paths)
        {
            var bb = BBox(paths);
            var o = new List<PointF[]>();
            foreach (var p in paths) { var q = new PointF[p.Length]; for (int i = 0; i < p.Length; i++) q[i] = new PointF(p[i].X - bb.Left, p[i].Y - bb.Top); o.Add(q); }
            return o;
        }
        static RectangleF BBox(List<PointF[]> paths)
        {
            float minx = float.MaxValue, miny = float.MaxValue, maxx = float.MinValue, maxy = float.MinValue;
            foreach (var p in paths) foreach (var pt in p) { minx = Math.Min(minx, pt.X); miny = Math.Min(miny, pt.Y); maxx = Math.Max(maxx, pt.X); maxy = Math.Max(maxy, pt.Y); }
            if (minx == float.MaxValue) return RectangleF.Empty;
            return RectangleF.FromLTRB(minx, miny, maxx, maxy);
        }

        // scale + offset + nearest-neighbour ordering
        List<PointF[]> Placed()
        {
            double s = (double)_scale.Value / 100.0, ox = (double)_offx.Value, oy = (double)_offy.Value;
            var list = new List<PointF[]>();
            foreach (var p in _design) { var q = new PointF[p.Length]; for (int i = 0; i < p.Length; i++) q[i] = new PointF((float)(p[i].X * s + ox), (float)(p[i].Y * s + oy)); list.Add(q); }
            var ordered = new List<PointF[]>(); var todo = new List<PointF[]>(list); PointF cur = new PointF(0, 0);
            while (todo.Count > 0)
            {
                int bi = 0; double bd = double.MaxValue;
                for (int k = 0; k < todo.Count; k++) { double dx = todo[k][0].X - cur.X, dy = todo[k][0].Y - cur.Y, dd = dx * dx + dy * dy; if (dd < bd) { bd = dd; bi = k; } }
                var pk = todo[bi]; todo.RemoveAt(bi); ordered.Add(pk); cur = pk[pk.Length - 1];
            }
            return ordered;
        }

        void DrawPreview(object sender, PaintEventArgs e)
        {
            var g = e.Graphics; g.SmoothingMode = SmoothingMode.AntiAlias;
            double matW = _cutter != null ? _cutter.WidthMm : 203.0;
            double k = Math.Min(_preview.Width / matW, _preview.Height / MAT_H);
            g.DrawRectangle(Pens.LightGray, 0, 0, (float)(matW * k), (float)(MAT_H * k));
            g.DrawString("mat " + Math.Round(matW) + " x " + MAT_H + " mm", Font, Brushes.Silver, 4, 2);
            using (var pen = new Pen(Color.FromArgb(220, 38, 38), 1.4f))
                foreach (var p in Placed())
                    for (int i = 1; i < p.Length; i++)
                        g.DrawLine(pen, (float)(p[i - 1].X * k), (float)(p[i - 1].Y * k), (float)(p[i].X * k), (float)(p[i].Y * k));
        }

        void DoCut()
        {
            if (_cutter == null) { SetStatus("Connect to the Die Cutter first."); return; }
            if (_design.Count == 0) { SetStatus("Load a design or the test square first."); return; }
            var placed = Placed();
            var bb = BBox(placed);
            double matW = _cutter.WidthMm;
            if (bb.Right > matW || bb.Bottom > MAT_H) { SetStatus("Design goes off the mat - reduce Scale or move it."); return; }

            var mat = MATS[(string)_material.SelectedItem];
            int force = (int)_force.Value, speed = (int)_speed.Value, depth = (int)_depth.Value;
            _cut.Enabled = false; _connect.Enabled = false;
            Task.Run(() =>
            {
                try
                {
                    SetStatus("Getting ready...");
                    _cutter.Setup(speed, force, mat.pen, depth, 0.9, MAT_H, SetStatus);
                    _cutter.Cut(placed, false,
                        pct => SetStatus((mat.pen ? "Drawing... " : "Making... ") + pct + "%"),
                        SetStatus);
                    SetStatus("Done! Unload the mat.");
                }
                catch (Exception ex) { SetStatus("Problem: " + ex.Message); }
                finally { BeginInvoke((Action)(() => { _cut.Enabled = true; _connect.Enabled = true; })); }
            });
        }

        protected override void OnFormClosed(FormClosedEventArgs e) { if (_cutter != null) _cutter.Dispose(); base.OnFormClosed(e); }

        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.Run(new MainForm());
        }
    }
}
