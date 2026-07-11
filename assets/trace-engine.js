/* Sangala Studio — in-browser photo -> silhouette engine (CC0).
 *
 * Background removal via U^2-Net (u2netp) on ONNX Runtime Web, then tracing via
 * ImageTracer.js. Shared by the app AND the parity regression test (dev/parity),
 * so the test guards the exact code the app runs.
 *
 * The preprocessing/postprocessing MIRRORS rembg's u2netp session byte-for-byte
 * (rembg/sessions/base.py::normalize and u2netp.py::predict) — see dev/parity.
 * The one unavoidable difference from the Python reference is the image resize
 * (canvas high-quality vs PIL LANCZOS); parity is verified by IoU, not identity.
 *
 * Requires ONNX Runtime Web (window.ort) to be loaded first.
 */
(function (global) {
  "use strict";

  const MEAN = [0.485, 0.456, 0.406];   // ImageNet, matches rembg
  const STD  = [0.229, 0.224, 0.225];
  const SIZE = 320;

  const BG = {
    assetsBase: "/assets/",   // where ort-wasm-*.wasm and u2netp.onnx live; app/test may override
    _session: null,

    async session() {
      if (this._session) return this._session;
      if (!global.ort) throw new Error("ONNX Runtime Web (ort) not loaded");
      const base = new URL(this.assetsBase, location.href).href;   // absolute, so ORT resolves the .mjs/.wasm from assets/ (not relative to ort.wasm.min.js)
      ort.env.wasm.numThreads = 1;      // single-threaded -> no SharedArrayBuffer / COOP / COEP
      ort.env.wasm.proxy = false;
      ort.env.wasm.wasmPaths = base;
      this._session = await ort.InferenceSession.create(
        base + "u2netp.onnx", { executionProviders: ["wasm"] });
      return this._session;
    },

    // Draw src (Image or canvas) stretched to 320x320 and return the ImageData.
    _to320(src) {
      const c = document.createElement("canvas"); c.width = SIZE; c.height = SIZE;
      const cx = c.getContext("2d", { willReadFrequently: true });
      cx.imageSmoothingEnabled = true; cx.imageSmoothingQuality = "high";
      cx.drawImage(src, 0, 0, SIZE, SIZE);   // rembg resizes to (320,320) ignoring aspect -> we stretch too
      return cx.getImageData(0, 0, SIZE, SIZE).data;
    },

    // rembg normalize(): scale by the image's MAX pixel value (not /255), then (x-mean)/std, CHW.
    _preprocess(d) {
      let mx = 0;
      for (let i = 0; i < d.length; i += 4) {
        if (d[i]   > mx) mx = d[i];
        if (d[i+1] > mx) mx = d[i+1];
        if (d[i+2] > mx) mx = d[i+2];
      }
      const denom = Math.max(mx, 1e-6), plane = SIZE * SIZE;
      const t = new Float32Array(3 * plane);
      for (let p = 0, i = 0; p < plane; p++, i += 4) {
        t[p]             = (d[i]   / denom - MEAN[0]) / STD[0];   // R plane
        t[plane + p]     = (d[i+1] / denom - MEAN[1]) / STD[1];   // G plane
        t[2 * plane + p] = (d[i+2] / denom - MEAN[2]) / STD[2];   // B plane
      }
      return t;
    },

    // Run u2netp on src (Image/canvas); return a grayscale mask <canvas> at src's natural size.
    async mask(src) {
      const W = src.naturalWidth || src.width, H = src.naturalHeight || src.height;
      const t = this._preprocess(this._to320(src));
      const sess = await this.session();
      const feeds = {}; feeds[sess.inputNames[0]] = new ort.Tensor("float32", t, [1, 3, SIZE, SIZE]);
      const out = await sess.run(feeds);
      const o = out[sess.outputNames[0]].data;        // first output d0, [1,1,320,320] -> Float32Array(320*320)
      const plane = SIZE * SIZE;
      let mi = Infinity, ma = -Infinity;
      for (let i = 0; i < plane; i++) { const v = o[i]; if (v < mi) mi = v; if (v > ma) ma = v; }
      const rng = (ma - mi) || 1e-6;
      // rembg: (pred - mi)/(ma - mi) * 255 -> uint8 grayscale at 320x320
      const mc = document.createElement("canvas"); mc.width = SIZE; mc.height = SIZE;
      const mctx = mc.getContext("2d"); const img = mctx.createImageData(SIZE, SIZE);
      for (let i = 0, j = 0; i < plane; i++, j += 4) {
        const g = Math.round(((o[i] - mi) / rng) * 255);
        img.data[j] = img.data[j+1] = img.data[j+2] = g; img.data[j+3] = 255;
      }
      mctx.putImageData(img, 0, 0);
      // resize mask back to the original size (rembg: mask.resize(img.size, LANCZOS))
      const fc = document.createElement("canvas"); fc.width = W; fc.height = H;
      const fctx = fc.getContext("2d");
      fctx.imageSmoothingEnabled = true; fctx.imageSmoothingQuality = "high";
      fctx.drawImage(mc, 0, 0, W, H);
      return fc;
    },

    // Trace a grayscale mask <canvas> to vector outline(s) of the subject via ImageTracer
    // (public domain). Thresholds to binary, traces, and returns the subject-region path
    // 'd' strings in mask-pixel coordinates: { paths:[dString], width, height }.
    trace(maskCanvas, opt) {
      opt = opt || {};
      if (!global.ImageTracer) throw new Error("ImageTracer not loaded");
      const W = maskCanvas.width, H = maskCanvas.height;
      const md = maskCanvas.getContext("2d").getImageData(0, 0, W, H).data;
      const thr = opt.threshold != null ? opt.threshold : 128;
      const bin = new Uint8ClampedArray(W * H * 4);
      for (let i = 0; i < W * H; i++) {
        const v = (md[i * 4] >= thr) ? 0 : 255;   // subject (mask bright) -> black, background -> white
        bin[i*4] = bin[i*4+1] = bin[i*4+2] = v; bin[i*4+3] = 255;
      }
      const options = Object.assign(
        { numberofcolors: 2, colorsampling: 0, pathomit: (opt.pathomit != null ? opt.pathomit : 8),
          ltres: 1, qtres: 1, rightangleenhance: false, roundcoords: 1, blurradius: 0, strokewidth: 0 },
        opt.tracer || {});
      const svg = ImageTracer.imagedataToSVG({ width: W, height: H, data: bin }, options);
      const doc = new DOMParser().parseFromString(svg, "image/svg+xml");
      const paths = [];
      doc.querySelectorAll("path").forEach(function (p) {
        const m = /rgb\((\d+),(\d+),(\d+)/.exec((p.getAttribute("fill") || "").replace(/\s+/g, ""));
        const lum = m ? (+m[1] + +m[2] + +m[3]) / 3 : 255;
        if (lum < 128) { const d = p.getAttribute("d"); if (d) paths.push(d); }   // keep the dark (subject) region
      });
      return { paths: paths, width: W, height: H };
    }
  };

  global.SangalaBg = BG;
})(window);
