"""Rebuilds the NTLS commentary as Ver 2.0: a ten-minute running order with a clock.

Glen, the night before: "we have a strict limit of no more than ten minutes. focus on this one thing."

Ver 1.0 gave John about three and a half minutes of commentary and left the rest of the ten minutes
unplanned. Ver 2.0 budgets the whole ten for all three presenters, and builds the clock BACKWARD FROM
THE LIVE DEMONSTRATION, because the radio link is both the reason the audience is there and the part
that can fail. A full minute is left unallocated ahead of the close so that a second attempt at the
link costs the demonstration nothing.

John's words are trimmed to fit that budget - about 1:50 before the demonstration and 1:10 after,
measured at 130 words a minute - and are split either side of it so that he closes.

The word counts under each block are there so the timing can be checked rather than trusted.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from makedocx import Doc

DRAFTS = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts")

d = Doc()
d.title("Networked Weather Station: A Ten-Minute Running Order")

d.body("Ten minutes, three presenters, and a live radio link that has to work. The clock below is "
       "built backward from the demonstration and leaves a full minute unassigned, so that a second "
       "attempt at the link costs nothing. John speaks either side of the demonstration rather than "
       "only before it, so that the last words in the room are his.")

d.table(
    "Table 1. The Ten Minutes",
    ["Time", "Who", "What"],
    [["0:00 \u2013 0:20", "John", "One sentence: where this is, and what the room is about to see"],
     ["0:20 \u2013 2:10", "John", "The place, how people live, and the two problems, with the photographs"],
     ["2:10 \u2013 2:30", "John", "Hands to Gerald"],
     ["2:30 \u2013 4:30", "Gerald", "The sending unit: sensors, transceiver, Yagi antenna, LoRa. Takes a reading"],
     ["4:30 \u2013 6:30", "Roger", "The base receiver on the MakerPort. The reading arrives on screen"],
     ["6:30 \u2013 7:30", "\u2014", "UNASSIGNED. Do not fill this. It is the retry if the link does not take"],
     ["7:30 \u2013 8:40", "John", "The mesh, and the engineering program, with the classroom photograph"],
     ["8:40 \u2013 10:00", "All", "Questions, and stop on time"]],
    weights=[16, 14, 70], center_cols=(0, 1))

d.heading("Before the Demonstration")
d.item("Photographs: ", "the valley; the mud-and-wattle house and the crowded lorry; the boys on the "
       "path.", after=60)
d.body("This is the Mount Elgon region of eastern Uganda, on the border with Kenya, and in a moment "
       "you are going to watch a weather reading leave it.")
d.body("People farm the slopes of an extinct volcano, on ground steep enough that you plant standing "
       "sideways. There is no electrical grid. There is no internet. A house is built from the "
       "mountain itself \u2014 earth, poles and thatch \u2014 and when people travel they travel "
       "standing on the back of a lorry, on roads the rain takes out.")
d.body("Two things are going wrong there. The first is the season. A family makes one decision each "
       "year on which everything depends: when to plant. That decision used to be made from "
       "experience, because the rains came when they had always come. They no longer do, and "
       "planting a few weeks early or late now costs a family its year.")
d.body("The second is faster. When enough rain falls on a slope already saturated, the slope moves. "
       "Mudslides kill people on this mountain every year, and they arrive without warning. The "
       "reason there is no warning is simple. Nobody is measuring the rain.")
d.body("So that is what we are about to show you. Not a forecast made somewhere else \u2014 a "
       "measurement, taken where the people are, and carried out of a place with no infrastructure "
       "at all. Gerald.")
d.item("About 230 words. ", "One minute fifty at an unhurried pace.", after=100)

d.heading("After the Demonstration")
d.item("Photograph: ", "the students around the 3D printer.", after=60)
d.body("Now imagine that not once, but at a hundred points across a mountainside, each station "
       "passing what it measures to the next. One station tells you the weather. A mesh of them tells "
       "you where the rain is falling hardest and how long it has been falling there. That is the "
       "thing nobody in this region has today.")
d.body("And these are the students who will build it. The goal is not to go and install weather "
       "stations for them. It is a high school engineering program, so that students fabricate the "
       "stations, install them, and maintain them. A station that arrives from outside lasts until "
       "the day it breaks. One built by the person who lives beside it lasts as long as it is "
       "needed.")
d.item("About 130 words. ", "One minute ten.", after=100)

d.heading("If the Clock Slips")
d.body("Decide this now rather than in the room.", before_list=True)
d.step("If the demonstration runs long, drop the second paragraph before it \u2014 the one about "
       "houses and the lorry. The two problems must stay; they are the case.")
d.step("If the link does not take on the first attempt, spend the unassigned minute and say nothing "
       "about it. The audience will wait once; it will not wait twice.")
d.step("If time is lost anyway, the closing words about the students are the last thing to cut. "
       "They are the reason the work exists.")

print(d.save(DRAFTS, "Networked Weather Station Commentary", version="2.0"))
