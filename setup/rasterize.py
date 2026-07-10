#!/usr/bin/env python3
"""Rasterize page 1 of a PDF to PNG with PyMuPDF (no Poppler needed).
Used by setup-windows.ps1 verification.

Usage: python rasterize.py <in.pdf> <out.png>
"""
import sys
import fitz  # PyMuPDF


def main():
    pdf, out = sys.argv[1], sys.argv[2]
    doc = fitz.open(pdf)
    doc[0].get_pixmap(dpi=110).save(out)
    print("  OK  rasterized page 1 -> %s" % out)


if __name__ == "__main__":
    main()
