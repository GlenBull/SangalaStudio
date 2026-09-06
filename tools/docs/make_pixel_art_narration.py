r"""Narration script for the Pixel Art video (Camtasia + Audiate), built from Chapters\Pixel Art (Ver 1.2).docx.

Each scene has an italic "On screen" cue, which is NOT read aloud, and a narration paragraph, which is
the text pasted into Audiate. Numbers are spelled out where a voice would otherwise stumble.

Run:  python tools\docs\make_pixel_art_narration.py
Writes "Pixel Art Narration (Ver N.M).docx" into Design through Making\Video, taking the next free number.
"""
import sys
sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
from makedocx import Doc

OUT = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\Video"

SCENES = [
 ("Scene 1. From Photograph to Tiles",
  "Screen capture. Sangala Mosaic opens; the crane photograph is opened; Remove Background; Fit to Photo lays the grid over the bird; Build It!.",
  "Sangala Mosaic turns a photograph into a mosaic of LEGO tiles. A photograph of a crowned crane is opened, "
  "its background is removed, and a grid is laid over the bird. The grid is thirty-two tiles across and "
  "thirty-two tiles down, the size of the most common LEGO baseplate. When Build It is pressed, Mosaic reads the "
  "color under each cell of the grid and replaces it with the nearest LEGO tile color. The result is a "
  "representational mosaic: a literal translation of the photograph into tiles."),

 ("Scene 2. Forty-Five Colors",
  "Still: Figure 1, the Tile Colors palette.",
  "The palette is small. LEGO sells the flat one-by-one tile in forty-five colors, and Mosaic offers only those, so "
  "every tile in a design can actually be ordered. Forty-five colors and a grid of thirty-two by thirty-two are the "
  "two constraints that every mosaic must live within."),

 ("Scene 3. What Pixel Art Knows",
  "Still: Figure 2, both cranes, or a slow push into the symbolic crane.",
  "Those constraints are familiar to pixel artists. In pixel art the individual pixel is the unit of composition. "
  "Every pixel is placed deliberately, on a small canvas, with a tightly limited palette. The style grew out of the "
  "memory limits of early computers and game consoles, but it outlived those limits and is now a chosen aesthetic, "
  "in games such as Minecraft and Stardew Valley. At this scale, detail cannot be rendered, so it is suggested. A "
  "face might be five pixels, and a single pixel completes an eye. Every pixel is a decision with a visible "
  "consequence, and a good sprite shows exactly what the artist chose."),

 ("Scene 4. Two Levels of Abstraction",
  "Still: Figure 2. Hold on the left crane, then the right.",
  "Here is the crane at two levels of abstraction. On the left is the representational version, the literal "
  "translation of the photograph into the closest available colors. On the right is a symbolic version. It "
  "translates the parts of the crane into distinctive features, the features that make a viewer recognize a crane."),

 ("Scene 5. The Crown",
  "Still: Figure 3. Ken Burns from the photograph of the crown to the blob of tiles beside it.",
  "The most distinctive feature of the crowned crane is the crown of feathers on top of its head. A grid of "
  "thirty-two by thirty-two cannot show individual feathers, so in the representational version the crown becomes "
  "an indistinct blob. The blob contributes nothing to recognizing the bird."),

 ("Scene 6. Treating the Head Symbolically",
  "Still: Figure 4, the symbolic head and crown.",
  "The most important decision borrowed from pixel art is to treat the crown symbolically rather than literally. The "
  "blob is replaced by a gold crown. The black of the head becomes black tiles. The eye is three white tiles. The "
  "bill cannot be black, or it would merge with the shape of the head. The traditional color for a bill is yellow, "
  "but yellow already belongs to the crown, so the bill is red instead."),

 ("Scene 7. The Neck",
  "Still: Figure 5, head and neck, representational beside symbolic.",
  "The head has been sharpened and compacted to make its features distinct, and the translation continues with the "
  "neck. The head is seven tiles wide in both versions, but the red bill takes three of those tiles on the lowest "
  "row. For the head to extend past the neck on each side, the neck narrows from three tiles to two."),

 ("Scene 8. The Body and the Wing",
  "Still: Figure 6, body and wing, representational beside symbolic.",
  "Next, the body. The distinction between the body and the wing is sharpened by making the wing dark gray and the "
  "body light gray. One tile is removed between the body and the neck, so the neck reads as separate from the body."),

 ("Scene 9. The Legs",
  "Still: Figure 7, legs and feet, representational beside symbolic.",
  "The legs receive the same treatment. They collapse into two columns of black tiles, which will later become two "
  "columns of LEGO bricks in a three-dimensional figure. A field of green below the legs stands for grass."),

 ("Scene 10. The Symbolic Crane",
  "Still: Figure 8, the two cranes. Slow push into the symbolic crane.",
  "In this way the representational crane becomes a symbolic crane, suited to the reduced palette and resolution of "
  "LEGO tiles. Every part is still there. Each has been reduced to a simple shape in a single color, and the "
  "features that identify the crane have been made larger and clearer than the photograph showed them."),

 ("Scene 11. From Mosaic to Figure",
  "Still: the symbolic crane, or the LEGO brick crane if a photograph of it is available.",
  "The finished mosaic is more than a picture. It is a framework in which each part can be extruded into a "
  "three-dimensional LEGO figure. That translation works best from a side view, a profile, rather than a front or "
  "top view, which is why the crane is drawn in profile."),
]

d = Doc()
d.title("Pixel Art Narration")
d.body("A narration script for the Pixel Art video. Under each scene the italic On screen line is a cue for the "
       "editor and is not read aloud; the paragraph beneath it is the narration to generate in Audiate. Numbers are "
       "spelled out so the voice reads them as intended.")
for head, cue, narration in SCENES:
    d.heading(head)
    d.item("On screen. ", cue)
    d.body(narration)
print(d.save(OUT, "Pixel Art Narration"))
