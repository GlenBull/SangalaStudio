"""Builds "Networked Weather Station - Commentary for the NTLS Demonstration" in _Drafts.

Asked for by Glen on the night of 2026-09-15, for a ten-minute demonstration the following morning:
John Wanda, Roger Wagner and Gerald Knezek. Gerald holds the sending unit - Yagi antenna, transceiver,
LoRa radio, weather sensors. Roger has the base receiving unit built on his MakerPort microcontroller.
John shows photographs of eastern Uganda and speaks the commentary that carries the live demonstration.

THE PHOTOGRAPHS ARE REAL AND WERE LOOKED AT. Glen's shared album "Sangala Initiative" opened in the
browser pane; the first six are a classroom of students in red uniforms around a 3D printer, five boys
on a red-dirt path, a thatched building on a cleared hillside, a mud-and-wattle house among banana and
mango trees, a lorry crowded with standing passengers, and a steep green mountain valley. The script
is cued to those rather than to imagined ones, and the cues are written so John can match them to
whatever order he ends up using.

WHAT IT DELIBERATELY DOES NOT DO: it does not put a casualty figure on the mudslides, and it does not
say the network predicts a landslide. One station measures rain; a mesh of them measures where and how
hard it is falling, which is the signal that precedes a slide and the information a farmer needs for
planting. Overclaiming in front of this audience would be the worst outcome of the ten minutes.

Three and a half minutes at a speaking pace of about 130 words a minute. The one-minute cut at the end
is there because three presenters in ten minutes run out of time, and the part that gets cut should be
chosen beforehand rather than in the moment.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from makedocx import Doc

DRAFTS = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts")

d = Doc()
d.title("Networked Weather Station: Commentary for the Demonstration")

d.body("The commentary below runs about three and a half minutes at an unhurried pace. Each section "
       "names the photograph it belongs with. A one-minute version follows at the end, for use if the "
       "ten minutes are running short.")

d.heading("The Place")
d.item("Photograph: ", "the steep green valley.", after=60)
d.body("This is the Mount Elgon region of eastern Uganda, on the border with Kenya. The mountain is "
       "an extinct volcano, and the soil on its slopes is deep and rich. That is why people farm "
       "there \u2014 on ground steep enough that a person plants standing sideways.")

d.heading("How People Live There")
d.item("Photographs: ", "the mud-and-wattle house, the thatched building on the hillside, the lorry "
       "crowded with passengers.", after=60)
d.body("There is no electrical grid here. There is no internet. A house is built from the mountain "
       "itself \u2014 earth, poles and thatch. When people travel, they travel together, standing on "
       "the back of a lorry, on roads the rain takes out.")

d.heading("The First Problem: The Season")
d.item("Photograph: ", "the boys on the path, with the cultivated slope behind them.", after=60)
d.body("A farming family here makes one decision each year on which everything else depends: when to "
       "plant. For generations that decision was made from experience, because the rains came when "
       "they had always come. They no longer do. Planting a few weeks early or a few weeks late now "
       "costs a family its year.")

d.heading("The Second Problem: The Slides")
d.body("The second problem is faster. When enough rain falls on a slope that is already saturated, "
       "the slope moves. Mudslides kill people on this mountain every year. They arrive without "
       "warning \u2014 and the reason there is no warning is simple. Nobody is measuring the rain.")

d.heading("What the Network Changes")
d.body("So that is what we are going to show you. Not a forecast made somewhere else. A measurement, "
       "taken where the people are, and carried out of a place that has no grid and no internet.")

d.heading("Handing Over to the Demonstration")
d.body("Gerald is holding the sending unit: the weather sensors, a transceiver, and the Yagi antenna "
       "he is pointing. It runs on LoRa radio \u2014 long range, very little power, and no "
       "infrastructure of any kind between the two ends. No tower, no subscription, no wire.")
d.body("Roger built the receiving station on his own MakerPort microcontroller. Watch his screen. "
       "What arrives there is the reading Gerald's unit just took.")
d.body("Now imagine that not once, but at a hundred points across a mountainside \u2014 each station "
       "passing what it measures to the next, until it reaches somebody who can act on it. One "
       "station tells you the weather. A mesh of them tells you where the rain is falling hardest, "
       "and how long it has been falling there. That is the thing nobody in this region has now.")

d.heading("What It Is Really For")
d.item("Photograph: ", "the students around the 3D printer.", after=60)
d.body("These are students in the region. The goal is not to go and install weather stations for "
       "them. It is to build a high school engineering program, so that students fabricate the "
       "stations, install them, and maintain them themselves.")
d.body("A weather station that arrives from outside lasts until the day it breaks. One built by the "
       "person who lives beside it lasts as long as it is needed. That is the difference we are "
       "trying to make, and it is why this begins in a classroom rather than at a supplier.")

d.heading("The One-Minute Version")
d.body("If time runs short, this is the part to keep.", before_list=True)
d.body("\u201cThis is the Mount Elgon region of eastern Uganda. There is no electrical grid and no "
       "internet. People farm the slopes of an extinct volcano, and two things are going wrong. The "
       "rains no longer come when they always came, so families no longer know when to plant. And "
       "when too much rain falls on a saturated slope, the slope moves \u2014 mudslides kill people "
       "there every year, without warning, because nobody is measuring the rain.")
d.body("\u201cWhat you are about to see is a measurement taken where the people are, and carried out "
       "of a place with no infrastructure at all. Gerald's unit takes the reading. Roger's station "
       "receives it over LoRa radio \u2014 no tower, no wire, no subscription. Multiply that across a "
       "mountainside and you have warning where there is none today.")
d.body("\u201cAnd the students in this photograph are the ones who will build it. That is the "
       "program: not stations delivered to a region, but engineers raised in it.\u201d")

print(d.save(DRAFTS, "Networked Weather Station Commentary"))
