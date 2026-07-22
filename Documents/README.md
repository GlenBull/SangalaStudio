# Sangala Studio Documentation — working conventions

*Rev. 1.2 — 2026-07-21*

Start here before editing the User Guide or the Technical Manual. This file records
what lives in this folder and the conventions that keep both documents consistent
with each other and with the *Design through Making: Art and Engineering* book, so
they read as one product.

## What's in this folder

- **User Guide (Ver X.Y).docx** — the student-facing guide to Sangala Studio, organized
  around the application's features and tools. The `.docx` is the maintained, delivered artifact.
- **User Guide.md** — a markdown companion covering the Chapters 1–3 (2D) features. It's
  also the best worked example of the house voice; when in doubt about tone, read it.
- **Tech Manual (Ver X.Y).docx** — the technical / engine manual.
- **Abstract.docx**, **Sangala-MakerPort Integration Summary** — supporting project docs.
- **.Archive/** — every prior version of the guide and manual. It is git-ignored (keeping
  ~129 MB of old revisions out of every clone a school makes). The main folder shows only
  the current version of each document; superseded versions move into `.Archive/`.

## The consistency layer — must match the book (this matters more than fonts)

If these drift, the guide and the book read as different products no matter how the pages
are formatted. This is where "same look and feel" actually lives.

- **American spelling everywhere** — color, center, gray, canceled, behavior, millimeters.
- **Terminology, exact:** always "**die cutter**" in full — never "cutter" or "cutting,"
  because in a school setting the bare word can read as self-harm. "**Make it!**" for the
  green button. Product is **Sangala Studio**; subtitle **Digital Fabrication tool** — note
  the deliberate case: "Digital Fabrication" is capitalized for emphasis/prominence, but
  "tool" stays lowercase as an ordinary noun, not part of the emphasized term. Don't
  "correct" this to "Tool" — it's intentional, not a slip. The drag-snap feature is
  "*Snap to Fit*," set in italics, never bare "Snap" (it collides with the Snap!
  programming language). Mat and page sizes shown in whole inches.
- **Voice:** concise and direct; minimal formatting; prose over bullet lists unless a list is
  clearly warranted. Never write "honest / honestly / genuinely / straightforward."
- **Structure:** organized around the application's **features and tools** — one section per
  tool or workflow (Getting Started, Cut/Fold Lines, Drawing, Editing, Snap!, Combining,
  Aligning, Cutting Out, 3D mode, and so on), with jargon introduced in context the first time
  it's needed. As the tool set has grown, this keeps each tool documented in exactly one place
  rather than re-explained inside every activity that uses it. A short activity-framed opening
  (what a student is trying to make) and a closing "Tool Sequences for Specific Designs"
  appendix (mapping tools back to a Silhouette, a Collage, a Shadowbox Frame, etc.) bookend the
  reference so a student can still find the path through a specific project. *(This supersedes
  an earlier draft of this guidance that called for activity-first structure — the guide's own
  growth made the feature-first approach the better fit.)*

## Typographic spec

- **Body:** Times New Roman 11 pt, black, never below 11 pt. Code identifiers in Consolas.
- **Lists:** numbered for step sequences; **3 pt space after** each item. A label leading an
  item is *italic* (not bold); Title-Case every word **except** words in parentheses (lowercase).
- **Spacing** (set explicitly, don't inherit from the style): a heading or lead-in sits **tight**
  to the list it introduces — Heading 3 = 0 pt before / 3 pt after; a body paragraph immediately
  before a list = 0 pt before / 3 pt after; an ordinary body paragraph = 5 pt.
- **Figure captions** (all four): directly beneath the figure; "Figure N. <sentence>," numbered
  sequentially through the document (renumber later figures when inserting one); 3 pt above the
  caption; centered; the whole caption italic; if it wraps to two lines, balance them with a
  manual line break near the middle.
- **Tables** — two kinds of rule. *Conventions to apply:* a numbered descriptive title
  "Table N. <caption>," numbered sequentially, the column-heading row directly below the title.
  *Visual formatting* (clone the exact values from Table 8 of the Tech Manual): centered on the
  page; Arial 10 pt throughout; cell **paragraph** spacing 3 pt before / 2 pt after (paragraph
  spacing, not cell margins — the rule most often missed); label column slightly left-indented;
  title row merged across all columns, Arial 10 bold; column-heading row Arial 10 italic centered;
  body cells Arial 10 regular left; single-line grid with a **double** line dividing headings from body.
- **Pagination:** every heading paragraph carries `keepNext` **and** `keepLines`; never add
  autospacing (no `beforeAutospacing` / `afterAutospacing`); no orphaned headings, and no couple
  of lines spilling onto an otherwise-empty page.

## Process

- **Never regenerate a document to revise it** — edit the actual file in place, surgically.
  Regeneration wipes the manual formatting and has cost real rework.
- **Versioning:** copy to the next version number, edit, then move the prior version into
  `.Archive/` so this folder shows only the current one.
- **Verify pagination before delivering** — orphaned headings and ballooned gaps live in the
  pagination, not the XML, so a validator passes while the page looks broken.
- **Deliver** as a plain file path.

## Environment note (important for other tools)

The *mechanics* of editing these `.docx` files vary by environment. The specific recipe used
from Claude Code on the author's Windows machine (rezip with Python's `zipfile`, a Word-COM
pagination check via `tools/docxcheck.ps1`, and so on) is documented in the repo's `CLAUDE.md`
and is **not** portable — a different tool or thread should use its own document tooling. The
**style and process rules above are what transfer**, not the plumbing.

## Alignment with the book

A shared style guide is being developed alongside the *Design through Making* book to unify it
with these documents. Where a convention here differs from the book's, reconcile to one answer
and apply it to both. The consistency layer above (voice, terminology, spelling) is
non-negotiable; structure and the typographic specifics can go either way but must be unified.
