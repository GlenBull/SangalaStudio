# Third-party assets shipped in `assets/`

These binaries are fetched **once** from official sources and committed to the repo so
Sangala Studio runs **fully offline** — nothing is fetched from a CDN at runtime, which is a
hard requirement for the Uganda classrooms. Each asset's exact source, version, license, and
SHA-256 (as shipped) is recorded below. Full license texts are in `assets/licenses/`.

| File | Purpose | Version | License | SHA-256 |
|------|---------|---------|---------|---------|
| `ort.wasm.min.js` | ONNX Runtime Web loader (WASM backend, single-threaded) | 1.19.2 | MIT | `98e831517582c08fc1b729def487a8b0152c83fc641746137eb4c7ad46032f1c` |
| `ort-wasm-simd-threaded.mjs` | ONNX Runtime Web WASM glue module (imported by the loader) | 1.19.2 | MIT | `d870a377322c3053fb97432d548423f165dd15e2af232947592fc07b0d2f3639` |
| `ort-wasm-simd-threaded.wasm` | ONNX Runtime Web WebAssembly (SIMD, run single-threaded via `numThreads=1`) | 1.19.2 | MIT | `1bf0b9ed7ad025cf9ca88ce6da29e54df3f128a169f8241d71823e81f078d578` |
| `u2netp.onnx` | U²-Net (lightweight) salient-object model — background-removal mask | u2netp | Apache-2.0 | `309c8469258dda742793dce0ebea8e6dd393174f89934733ecc8b14c76f4ddd8` |
| `imagetracer_v1.2.6.js` | Raster mask → vector paths (replaces GPL Potrace; this repo is CC0) | 1.2.6 | Unlicense (public domain) | _added in step 4_ |

## Sources

- **ONNX Runtime Web** — official npm package published by Microsoft.
  `https://registry.npmjs.org/onnxruntime-web/-/onnxruntime-web-1.19.2.tgz`
  Files taken verbatim from `package/dist/`. License: MIT © Microsoft Corporation.
- **u2netp.onnx** — official rembg model release by Daniel Gatis.
  `https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.onnx`
  Model: U²-Net (u2netp) by Xuebin Qin et al. ("U²-Net: Going Deeper with Nested
  U-Structure for Salient Object Detection"). License: Apache-2.0.
- **ImageTracer.js** — official repo by András Jankovics (added in step 4).
  `https://github.com/jankovicsandras/imagetracerjs`  License: The Unlicense (public domain).

## Why not Potrace

Potrace is GPL-licensed; this repository is CC0. Shipping GPL code in a CC0 app we
distribute to schools is a copyleft conflict, so tracing uses the public-domain
**ImageTracer.js** instead.

## Re-verifying

`Get-FileHash <file> -Algorithm SHA256` must match the values above. If a file is ever
re-fetched, update its hash here in the same commit.
