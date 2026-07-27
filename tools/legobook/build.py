"""Build a LEGO-kit instruction booklet from a model.

    python build.py crane                     -> the HTML booklet, beside this script
    python build.py crane --docx              -> also a Word document (needs Microsoft Edge)
    python build.py crane --out "D:\\...\\Documents"   -> write them somewhere else
    python build.py --list                    -> the models available

Adding an animal: copy models/crane.py, change the pieces and the prose, run it. See README.md.
"""
import argparse, importlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "models"))

import engine, docxout


def load(name):
    try:
        return importlib.import_module(name)
    except ImportError:
        raise SystemExit('No model called "%s". Available: %s' % (name, ", ".join(available())))


def available():
    d = os.path.join(HERE, "models")
    return sorted(f[:-3] for f in os.listdir(d)
                  if f.endswith(".py") and not f.startswith("_"))


def main():
    ap = argparse.ArgumentParser(description="Build a LEGO instruction booklet.")
    ap.add_argument("model", nargs="?", help="which figure to build (e.g. crane)")
    ap.add_argument("--out", default=HERE, help="folder to write into")
    ap.add_argument("--docx", action="store_true", help="also write a Word document")
    ap.add_argument("--list", action="store_true", help="list the available models")
    a = ap.parse_args()

    if a.list or not a.model:
        print("Models: " + ", ".join(available()))
        return

    m = load(a.model)
    book = engine.Book(m.TITLE, m.SUBTITLE, getattr(m, "NOTE", ""),
                       m.INVENTORY, m.STEPS, getattr(m, "CLOSING", None))

    os.makedirs(a.out, exist_ok=True)
    html_path = os.path.join(a.out, m.TITLE + ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(book.html())
    print("wrote %s  (%d steps, %d pieces)"
          % (html_path, len(book.steps), sum(len(s["pieces"]) for s in book.steps)))

    if a.docx:
        imgs = book.rasterize(os.path.join(a.out, "_images_" + a.model))
        docx_path = os.path.join(a.out, m.TITLE + ".docx")
        docxout.write(book, imgs, docx_path, table=getattr(m, "TABLE", None))
        print("wrote %s" % docx_path)


if __name__ == "__main__":
    main()
