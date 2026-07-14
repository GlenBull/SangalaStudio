// SangalaServer.cs -- local no-admin helper for Sangala Studio.
//
// Serves the polished SangalaStudio.html page to the browser on a loopback
// port (127.0.0.1) and holds the USB die-cutter connection. The page's
// "Make it" button POSTs the cut paths here; this helper drives the machine
// using the proven Cutter engine in DieCutter.cs.
//
// Loopback TcpListener needs no admin and no firewall exception. Compiled
// in-box with csc together with DieCutter.cs (see Build SangalaStudio.cmd).

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace DieCutterApp
{
    static class Server
    {
        const double MAT_H = 305.0;
        static Cutter _cutter;
        static string _lastStatus = "idle";
        static int _port = 0;
        static string _htmlPath;
        static string _snapLibPath;
        static string _snapSvg;                      // a drawing Snap! has posted, waiting for the page to collect it
        static readonly object _snapLock = new object();
        static double _jogX = 15.9, _jogY = 15.9;   // current manual-jog head position (mm)
        static bool _framed = false;                 // has the machine been Setup() since connect (for /raw debug)
        static readonly System.Globalization.CultureInfo INV = System.Globalization.CultureInfo.InvariantCulture;

        [STAThread]
        static void Main()
        {
            _htmlPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "SangalaStudio.html");
            _snapLibPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Sangala for Snap.xml");

            TcpListener listener = null;
            for (int p = 8787; p <= 8807 && listener == null; p++)
            {
                try { var l = new TcpListener(IPAddress.Loopback, p); l.Start(); listener = l; _port = p; }
                catch (SocketException) { }
            }
            if (listener == null) { MessageBox.Show("Could not open a local port (8787-8807)."); return; }

            var t = new Thread(() => AcceptLoop(listener)) { IsBackground = true };
            t.Start();

            try { Process.Start("http://127.0.0.1:" + _port + "/"); } catch { }

            Application.EnableVisualStyles();
            Application.Run(new TrayContext(_port));
        }

        static void AcceptLoop(TcpListener listener)
        {
            while (true)
            {
                TcpClient c = null;
                try { c = listener.AcceptTcpClient(); }
                catch { break; }
                var client = c;
                ThreadPool.QueueUserWorkItem(_ => { try { Handle(client); } catch { } });
            }
        }

        // ---- minimal HTTP ----
        static void Handle(TcpClient client)
        {
            using (client)
            using (var ns = client.GetStream())
            {
                var head = new MemoryStream();
                int prev = -1, b; int matched = 0;
                // read until CRLF CRLF
                while ((b = ns.ReadByte()) != -1)
                {
                    head.WriteByte((byte)b);
                    if ((matched == 0 || matched == 2) && b == '\r') matched++;
                    else if ((matched == 1 || matched == 3) && b == '\n') matched++;
                    else matched = (b == '\r') ? 1 : 0;
                    if (matched == 4) break;
                    prev = b;
                }
                string header = Encoding.ASCII.GetString(head.ToArray());
                string[] lines = header.Split(new[] { "\r\n" }, StringSplitOptions.None);
                if (lines.Length == 0) return;
                string[] rl = lines[0].Split(' ');
                if (rl.Length < 2) return;
                string method = rl[0], path = rl[1];
                int qi = path.IndexOf('?'); if (qi >= 0) path = path.Substring(0, qi);

                int contentLen = 0;
                foreach (var ln in lines)
                    if (ln.ToLowerInvariant().StartsWith("content-length:"))
                        int.TryParse(ln.Substring(15).Trim(), out contentLen);

                string body = "";
                if (contentLen > 0)
                {
                    var buf = new byte[contentLen]; int got = 0;
                    while (got < contentLen) { int r = ns.Read(buf, got, contentLen - got); if (r <= 0) break; got += r; }
                    body = Encoding.UTF8.GetString(buf, 0, got);
                }

                // ---- Snap! bridge. These routes carry DESIGNS ONLY and are the only ones that answer a
                // cross-origin caller (Snap! runs on another origin, so nothing reaches us without CORS).
                // Nothing here moves the die cutter: a Snap! script can put a drawing on the mat, but a
                // human still has to press Make It.
                if (method == "OPTIONS") { RespondCors(ns, "text/plain", ""); }
                else if (method == "POST" && path == "/snap/svg") { lock (_snapLock) { _snapSvg = body; } RespondCors(ns, "text/plain", "ok"); }
                else if (method == "GET" && path == "/snap/svg")     // the page polls this; reading takes the drawing off the spike
                { string s; lock (_snapLock) { s = _snapSvg; _snapSvg = null; } RespondCors(ns, "image/svg+xml", s ?? ""); }
                else if (method == "GET" && path == "/snap/library.xml") ServeSnapLibrary(ns);
                else if (method == "GET" && (path == "/" || path == "/index.html")) ServeHtml(ns);
                else if (method == "GET" && path.StartsWith("/assets/", StringComparison.Ordinal)) ServeAsset(ns, path);
                else if (path == "/connect") Respond(ns, "application/json", DoConnect());
                else if (path == "/status") Respond(ns, "application/json", "{\"status\":\"" + Esc(_lastStatus) + "\"}");
                else if (path == "/cut") Respond(ns, "application/json", DoCut(body));
                else if (path == "/scan") Respond(ns, "application/json", DoScan(body));
                else if (path == "/printcut") Respond(ns, "application/json", DoPrintCut(body));
                else if (path == "/manualstart") Respond(ns, "application/json", DoManualStart(body));
                else if (path == "/jog") Respond(ns, "application/json", DoJog(body));
                else if (path == "/manualread") Respond(ns, "application/json", DoManualRead(body));
                else if (path == "/manualcut") Respond(ns, "application/json", DoManualCut(body));
                else if (path == "/unload") Respond(ns, "application/json", DoUnload());
                else if (path == "/raw") Respond(ns, "application/json", DoRaw(body));
                else Respond(ns, "text/plain", "not found", "404 Not Found");
            }
        }

        static void ServeHtml(NetworkStream ns)
        {
            if (!File.Exists(_htmlPath)) { Respond(ns, "text/plain", "SangalaStudio.html not found next to the program.", "500 Error"); return; }
            byte[] html = File.ReadAllBytes(_htmlPath);
            var head = Encoding.ASCII.GetBytes(
                "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: " + html.Length +
                "\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n");
            ns.Write(head, 0, head.Length); ns.Write(html, 0, html.Length);
        }

        // Serve a static file from the assets/ folder (next to the exe) with the correct
        // MIME type. Binary types (.wasm, .onnx) must NOT carry a charset, or WebAssembly
        // refuses to instantiate. Single-threaded WASM build -> no COOP/COEP headers needed.
        static void ServeAsset(NetworkStream ns, string path)
        {
            string assetsDir = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "assets"));
            string rel = Uri.UnescapeDataString(path.Substring("/assets/".Length));
            if (rel.Contains("..") || rel.Contains(":") || rel.StartsWith("/") || rel.StartsWith("\\"))
            { Respond(ns, "text/plain", "bad asset path", "400 Bad Request"); return; }
            string full = Path.GetFullPath(Path.Combine(assetsDir, rel.Replace('/', Path.DirectorySeparatorChar)));
            if (!full.StartsWith(assetsDir + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase) || !File.Exists(full))
            { Respond(ns, "text/plain", "asset not found", "404 Not Found"); return; }
            string ext = Path.GetExtension(full).ToLowerInvariant();
            string ctype; bool isText = false;
            switch (ext)
            {
                case ".wasm": ctype = "application/wasm"; break;
                case ".onnx": ctype = "application/octet-stream"; break;
                case ".js": case ".mjs": ctype = "text/javascript"; isText = true; break;
                case ".json": ctype = "application/json"; isText = true; break;
                case ".png": ctype = "image/png"; break;
                case ".jpg": case ".jpeg": ctype = "image/jpeg"; break;
                case ".txt": case ".md": ctype = "text/plain"; isText = true; break;
                default: ctype = "application/octet-stream"; break;
            }
            byte[] data = File.ReadAllBytes(full);
            string ct = ctype + (isText ? "; charset=utf-8" : "");
            var head = Encoding.ASCII.GetBytes(
                "HTTP/1.1 200 OK\r\nContent-Type: " + ct + "\r\nContent-Length: " + data.Length +
                "\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n");
            ns.Write(head, 0, head.Length); ns.Write(data, 0, data.Length);
        }

        // Serve the Snap! blocks library from the helper itself, so a student loads it with
        // extensions.snap.berkeley.edu/snap/snap.html#open:http://127.0.0.1:<port>/snap/library.xml
        // - no internet, no download, no file dialog.
        static void ServeSnapLibrary(NetworkStream ns)
        {
            if (!File.Exists(_snapLibPath)) { RespondCors(ns, "text/plain", "Sangala for Snap.xml not found next to the program.", "404 Not Found"); return; }
            RespondCors(ns, "text/xml", File.ReadAllText(_snapLibPath, Encoding.UTF8));
        }

        static void RespondCors(NetworkStream ns, string ctype, string bodyText, string statusLine = "200 OK")
        {
            byte[] body = Encoding.UTF8.GetBytes(bodyText ?? "");
            // Snap! runs on a PUBLIC site and we are a LOCAL address, so the browser treats this as a private-network
            // request: it preflights, and refuses unless we say so. Without the Allow-Private-Network grant the POST
            // never leaves Chrome, even though curl reaches us perfectly well.
            var head = Encoding.ASCII.GetBytes(
                "HTTP/1.1 " + statusLine + "\r\nContent-Type: " + ctype + "; charset=utf-8\r\nContent-Length: " +
                body.Length + "\r\nAccess-Control-Allow-Origin: *\r\nAccess-Control-Allow-Methods: GET, POST, OPTIONS\r\n" +
                "Access-Control-Allow-Headers: Content-Type\r\nAccess-Control-Allow-Private-Network: true\r\n" +
                "Access-Control-Max-Age: 86400\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n");
            ns.Write(head, 0, head.Length); ns.Write(body, 0, body.Length);
        }

        static void Respond(NetworkStream ns, string ctype, string bodyText, string statusLine = "200 OK")
        {
            byte[] body = Encoding.UTF8.GetBytes(bodyText);
            var head = Encoding.ASCII.GetBytes(
                "HTTP/1.1 " + statusLine + "\r\nContent-Type: " + ctype + "; charset=utf-8\r\nContent-Length: " +
                body.Length + "\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n");
            ns.Write(head, 0, head.Length); ns.Write(body, 0, body.Length);
        }

        static string Esc(string s) { return (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\""); }

        // ---- endpoints ----

        // Split path lines into cut and score paths, separated by a "---SCORE---" line.
        // Subtracts `sub` mm from each coordinate (to move page coords into the
        // registered frame; pass 0 for a plain cut).
        static void SplitCutScore(string[] lines, int start, float sub, out List<PointF[]> cut, out List<PointF[]> score)
        {
            cut = new List<PointF[]>(); score = new List<PointF[]>();
            var target = cut;
            for (int i = start; i < lines.Length; i++)
            {
                string ln = lines[i].Trim();
                if (ln.Length == 0) continue;
                if (ln == "---SCORE---") { target = score; continue; }
                var arr = new List<PointF>();
                foreach (var pt in lines[i].Split(' '))
                {
                    if (pt.Length == 0) continue;
                    var xy = pt.Split(',');
                    float fx, fy;
                    if (xy.Length < 2
                        || !float.TryParse(xy[0], System.Globalization.NumberStyles.Float, INV, out fx)
                        || !float.TryParse(xy[1], System.Globalization.NumberStyles.Float, INV, out fy))
                        throw new Exception("Bad point at line " + i + ": '" + pt + "'  (line: '" + lines[i] + "')");
                    arr.Add(new PointF(fx - sub, fy - sub));
                }
                if (arr.Count >= 2) target.Add(arr.ToArray());
            }
        }

        // Fold/score lines get a lighter pass so paper creases instead of cutting through.
        static int ScoreForce(int cutForce) { return Math.Max(1, cutForce / 2); }
        static string DoConnect()
        {
            try
            {
                if (_cutter != null) { _cutter.Dispose(); _cutter = null; }
                _cutter = new Cutter(); _cutter.Open();
                _framed = false;
                string fw = _cutter.Firmware();
                _lastStatus = "connected to " + _cutter.ModelName;
                return "{\"ok\":true,\"model\":\"" + Esc(_cutter.ModelName) + "\",\"fw\":\"" + Esc(fw) +
                       "\",\"width\":" + _cutter.WidthMm.ToString(System.Globalization.CultureInfo.InvariantCulture) + "}";
            }
            catch (Exception ex) { return "{\"ok\":false,\"error\":\"" + Esc(ex.Message) + "\"}"; }
        }

        // body: first line "force,speed,depth,pen"; then one path per line, "x,y x,y ..." in mm
        static string DoCut(string body)
        {
            if (_cutter == null) return "{\"ok\":false,\"error\":\"Not connected to the Die Cutter.\"}";
            try
            {
                var lines = body.Replace("\r", "").Split('\n');
                if (lines.Length < 2) return "{\"ok\":false,\"error\":\"No design received.\"}";
                var s = lines[0].Split(',');
                int force, speed, depth;
                if (s.Length < 4 || !int.TryParse(s[0], out force) || !int.TryParse(s[1], out speed) || !int.TryParse(s[2], out depth))
                    throw new Exception("Bad settings header: '" + lines[0] + "'");
                bool pen = s[3] == "1";
                int passes = 1; if (s.Length >= 5) int.TryParse(s[4], out passes); passes = Math.Max(1, Math.Min(4, passes));
                List<PointF[]> paths, scores;
                SplitCutScore(lines, 1, 0f, out paths, out scores);
                if (paths.Count == 0 && scores.Count == 0) return "{\"ok\":false,\"error\":\"No cut paths in the design.\"}";

                Action<string> note = m => { _lastStatus = m; };
                _lastStatus = "getting ready";
                _cutter.Setup(speed, force, pen, depth, 0.9, MAT_H, note);
                for (int pass = 0; paths.Count > 0 && pass < passes; pass++)
                    _cutter.Cut(paths, false, pct => { _lastStatus = (pen ? "drawing " : "making ") + pct + "%"; }, note, (pass == passes - 1) && scores.Count == 0);
                if (scores.Count > 0) { _cutter.SetForce(ScoreForce(force)); _cutter.Cut(scores, false, pct => { _lastStatus = "scoring " + pct + "%"; }, note, true); }
                try { _cutter.Unload(MAT_H); } catch { }
                _lastStatus = "done";
                return "{\"ok\":true}";
            }
            catch (Exception ex) { _lastStatus = "error"; return "{\"ok\":false,\"error\":\"" + Esc(ex.Message) + "\"}"; }
        }

        // Eject the mat (same routine run at the end of a cut). Exposed so it can be
        // triggered on its own for testing/manual unload.
        static string DoUnload()
        {
            if (_cutter == null) return "{\"ok\":false,\"error\":\"Not connected to the Die Cutter.\"}";
            try
            {
                _cutter.Setup(8, 14, false, 3, 0.9, MAT_H, m => { _lastStatus = m; });   // init so the machine accepts the feed
                _cutter.Unload(MAT_H);
                _lastStatus = "unloaded";
                return "{\"ok\":true}";
            }
            catch (Exception ex) { _lastStatus = "error"; return "{\"ok\":false,\"error\":\"" + Esc(ex.Message) + "\"}"; }
        }

        // Debug: init the coordinate frame once (so moves take), then send a raw GPGL
        // command. Used to find the eject command interactively without rebuilding.
        static string DoRaw(string body)
        {
            if (_cutter == null) return "{\"ok\":false,\"error\":\"Not connected to the Die Cutter.\"}";
            try
            {
                string cmd = (body ?? "").Trim();
                if (cmd.Length == 0) return "{\"ok\":false,\"error\":\"Empty command.\"}";
                if (!_framed) { _cutter.Setup(8, 14, false, 3, 0.9, MAT_H, m => { _lastStatus = m; }); _framed = true; }
                if (cmd.StartsWith("hex ", StringComparison.OrdinalIgnoreCase))
                {
                    string hex = cmd.Substring(4).Replace(" ", "");
                    if (hex.Length == 0 || hex.Length % 2 != 0) return "{\"ok\":false,\"error\":\"hex needs full byte pairs, e.g. hex 1B 0C\"}";
                    byte[] b = new byte[hex.Length / 2];
                    for (int i = 0; i < b.Length; i++) b[i] = Convert.ToByte(hex.Substring(i * 2, 2), 16);
                    _cutter.SendRawBytes(b);
                    _lastStatus = "sent bytes: " + cmd;
                }
                else { _cutter.SendRaw(cmd); _lastStatus = "sent: " + cmd; }
                return "{\"ok\":true}";
            }
            catch (Exception ex) { _lastStatus = "error"; return "{\"ok\":false,\"error\":\"" + Esc(ex.Message) + "\"}"; }
        }

        // Experimental: ask the machine to scan for print-and-cut registration marks.
        static string DoScan(string body)
        {
            if (_cutter == null) return "{\"ok\":false,\"error\":\"Not connected to the Die Cutter.\"}";
            try
            {
                _cutter.Setup(8, 14, false, 3, 0.9, MAT_H, m => { _lastStatus = m; });  // init + mat + boundary
                const double inset = 15.9, pageW = 215.9, pageH = 279.4;   // Letter, 15.9mm inset
                double wid = pageW - 2 * inset;   // horizontal distance between marks
                double len = pageH - 2 * inset;   // vertical distance between marks
                string r = _cutter.ScanRegMarks(len, wid, inset, inset);
                _lastStatus = "scan: " + r;
                return "{\"ok\":true,\"result\":\"" + Esc(r) + "\"}";
            }
            catch (Exception ex) { return "{\"ok\":false,\"error\":\"" + Esc(ex.Message) + "\"}"; }
        }

        // Print-and-cut: register to the printed marks, then cut the paths (page coords) in that frame.
        static string DoPrintCut(string body)
        {
            if (_cutter == null) return "{\"ok\":false,\"error\":\"Not connected to the Die Cutter.\"}";
            try
            {
                var lines = body.Replace("\r", "").Split('\n');
                if (lines.Length < 2) return "{\"ok\":false,\"error\":\"No design received.\"}";
                var s = lines[0].Split(',');
                int force, speed, depth;
                if (s.Length < 4 || !int.TryParse(s[0], out force) || !int.TryParse(s[1], out speed) || !int.TryParse(s[2], out depth))
                    throw new Exception("Bad settings header: '" + lines[0] + "'");
                bool pen = s[3] == "1";
                int passes = 1; if (s.Length >= 5) int.TryParse(s[4], out passes); passes = Math.Max(1, Math.Min(4, passes));
                const double inset = 15.9, pageW = 215.9, pageH = 279.4;
                List<PointF[]> paths, scores;
                SplitCutScore(lines, 1, (float)inset, out paths, out scores);
                if (paths.Count == 0 && scores.Count == 0) return "{\"ok\":false,\"error\":\"No cut paths in the design.\"}";
                Action<string> note = m => { _lastStatus = m; };
                _cutter.Setup(speed, force, pen, depth, 0.9, MAT_H, note);
                double wid = pageW - 2 * inset, len = pageH - 2 * inset;
                string reg = _cutter.ScanRegMarks(len, wid, inset, inset);
                if (reg.Trim() != "0") { _lastStatus = "marks not found"; return "{\"ok\":false,\"error\":\"Registration marks not found (reply " + Esc(reg) + ").\"}"; }
                for (int pass = 0; paths.Count > 0 && pass < passes; pass++)
                    _cutter.Cut(paths, false, pct => { _lastStatus = "cutting " + pct + "%"; }, note, (pass == passes - 1) && scores.Count == 0);
                if (scores.Count > 0) { _cutter.SetForce(ScoreForce(force)); _cutter.Cut(scores, false, pct => { _lastStatus = "scoring " + pct + "%"; }, note, true); }
                try { _cutter.Unload(MAT_H); } catch { }
                _lastStatus = "done";
                return "{\"ok\":true}";
            }
            catch (Exception ex) { _lastStatus = "error"; return "{\"ok\":false,\"error\":\"" + Esc(ex.Message) + "\"}"; }
        }

        // ---- Manual print-and-cut registration ----
        // The user jogs the tool over the top-left square, the machine reads it
        // there, then finds the other two marks from the known spacing. This
        // removes the load-position guesswork that makes the automatic search
        // flaky. Body of /manualstart and /manualcut: "force,speed,depth,pen".

        static string DoManualStart(string body)
        {
            if (_cutter == null) return "{\"ok\":false,\"error\":\"Not connected to the Die Cutter.\"}";
            try
            {
                int force = 14, speed = 8, depth = 3; bool pen = false;
                var s = (body ?? "").Split(',');
                if (s.Length >= 4) { int.TryParse(s[0], out force); int.TryParse(s[1], out speed); int.TryParse(s[2], out depth); pen = s[3] == "1"; }
                _cutter.Setup(speed, force, pen, depth, 0.9, MAT_H, m => { _lastStatus = m; });
                _jogX = 15.9; _jogY = 15.9;                 // nominal top-left square corner
                _cutter.MoveToMm(_jogX, _jogY);
                _lastStatus = "manual align: jog the tool onto the square, then Read marks";
                return "{\"ok\":true,\"x\":" + _jogX.ToString(INV) + ",\"y\":" + _jogY.ToString(INV) + "}";
            }
            catch (Exception ex) { _lastStatus = "error"; return "{\"ok\":false,\"error\":\"" + Esc(ex.Message) + "\"}"; }
        }

        // body: "dx,dy" (mm) to nudge the head from its current position
        static string DoJog(string body)
        {
            if (_cutter == null) return "{\"ok\":false,\"error\":\"Not connected to the Die Cutter.\"}";
            try
            {
                var s = (body ?? "").Trim().Split(',');
                double dx = double.Parse(s[0], INV), dy = double.Parse(s[1], INV);
                _jogX += dx; _jogY += dy;
                _cutter.MoveToMm(_jogX, _jogY);
                _lastStatus = "jog " + _jogX.ToString("0.0", INV) + ", " + _jogY.ToString("0.0", INV) + " mm";
                return "{\"ok\":true,\"x\":" + _jogX.ToString(INV) + ",\"y\":" + _jogY.ToString(INV) + "}";
            }
            catch (Exception ex) { return "{\"ok\":false,\"error\":\"" + Esc(ex.Message) + "\"}"; }
        }

        // body (optional): "lenY,widX" mm to override the mark-to-mark distances,
        // used to dial out the blade-vs-optical-eye offset that makes the search
        // overshoot the second mark. Empty body uses the true printed distances.
        static string DoManualRead(string body)
        {
            if (_cutter == null) return "{\"ok\":false,\"error\":\"Not connected to the Die Cutter.\"}";
            try
            {
                const double inset = 15.9, pageW = 215.9, pageH = 279.4;   // Letter, 15.9mm inset
                double wid = pageW - 2 * inset, len = pageH - 2 * inset;
                var d = (body ?? "").Trim().Split(',');
                double L, W;
                if (d.Length >= 2 && double.TryParse(d[0], System.Globalization.NumberStyles.Float, INV, out L)
                                  && double.TryParse(d[1], System.Globalization.NumberStyles.Float, INV, out W)
                                  && L > 0 && W > 0) { len = L; wid = W; }
                string r = _cutter.ManualRegMarks(len, wid);
                _lastStatus = "manual read: " + r;
                bool found = r.Trim() == "0";
                return "{\"ok\":true,\"result\":\"" + Esc(r) + "\",\"found\":" + (found ? "true" : "false") + "}";
            }
            catch (Exception ex) { return "{\"ok\":false,\"error\":\"" + Esc(ex.Message) + "\"}"; }
        }

        // Cut in the registered frame after a successful manual read. No Setup and
        // no scan here -- the manual read already established the origin, and the
        // tool was configured by DoManualStart. Body: "force,speed,depth,pen" then
        // one path per line, "x,y x,y ..." in page (mm) coords.
        static string DoManualCut(string body)
        {
            if (_cutter == null) return "{\"ok\":false,\"error\":\"Not connected to the Die Cutter.\"}";
            try
            {
                var lines = (body ?? "").Replace("\r", "").Split('\n');
                if (lines.Length < 2) return "{\"ok\":false,\"error\":\"No design received.\"}";
                int mforce = 14; var h = lines[0].Split(','); if (h.Length >= 1) int.TryParse(h[0], out mforce);
                bool pen = h.Length >= 4 && h[3] == "1";
                int passes = 1; if (h.Length >= 5) int.TryParse(h[4], out passes); passes = Math.Max(1, Math.Min(4, passes));
                const double inset = 15.9;
                List<PointF[]> paths, scores;
                SplitCutScore(lines, 1, (float)inset, out paths, out scores);
                if (paths.Count == 0 && scores.Count == 0) return "{\"ok\":false,\"error\":\"No cut paths in the design.\"}";
                for (int pass = 0; paths.Count > 0 && pass < passes; pass++)
                    _cutter.Cut(paths, false, pct => { _lastStatus = (pen ? "drawing " : "making ") + pct + "%"; }, m => { _lastStatus = m; }, (pass == passes - 1) && scores.Count == 0);
                if (scores.Count > 0) { _cutter.SetForce(ScoreForce(mforce)); _cutter.Cut(scores, false, pct => { _lastStatus = "scoring " + pct + "%"; }, m => { _lastStatus = m; }, true); }
                try { _cutter.Unload(MAT_H); } catch { }
                _lastStatus = "done";
                return "{\"ok\":true}";
            }
            catch (Exception ex) { _lastStatus = "error"; return "{\"ok\":false,\"error\":\"" + Esc(ex.Message) + "\"}"; }
        }

        // ---- runs quietly in the system tray (no desktop window) ----
        class TrayContext : ApplicationContext
        {
            NotifyIcon _icon;
            public TrayContext(int port)
            {
                string url = "http://127.0.0.1:" + port + "/";
                var menu = new ContextMenuStrip();
                menu.Items.Add("Open Sangala Studio", null, (a, b) => { try { Process.Start(url); } catch { } });
                menu.Items.Add("Quit Sangala Studio", null, (a, b) => { _icon.Visible = false; Application.Exit(); });
                _icon = new NotifyIcon
                {
                    Icon = System.Drawing.SystemIcons.Application,
                    Text = "Sangala Studio (running)",
                    Visible = true,
                    ContextMenuStrip = menu
                };
                _icon.DoubleClick += (a, b) => { try { Process.Start(url); } catch { } };
                _icon.ShowBalloonTip(4000, "Sangala Studio", "Running in the tray. Right-click the icon to open or quit.", ToolTipIcon.Info);
            }
            protected override void Dispose(bool disposing)
            {
                if (disposing && _icon != null) { _icon.Dispose(); _icon = null; }
                base.Dispose(disposing);
            }
        }
    }
}
