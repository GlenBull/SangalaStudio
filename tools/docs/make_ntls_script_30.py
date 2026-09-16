"""The spoken script, one page, with a time mark against every block. Ver 3.0.

Glen: "You didn't provide timing marks or a script." Ver 2.0 gave a running-order table and the words
in separate sections; this puts the mark on the line, so John can read straight down the page and know
at a glance whether he is ahead or behind. The same words are in the deck's speaker notes.

Ver 2.0 archived.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from makedocx import Doc

DRAFTS = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts")

d = Doc()
d.title("Networked Weather Station: Script with Time Marks")

d.body("Ten minutes, hard stop. John speaks either side of the demonstration. The marks are where he "
       "should be, not where he must be; the only fixed point is that 6:30 to 7:30 stays empty, as the "
       "retry if the radio link does not take on the first attempt. The same words are in the speaker "
       "notes of the deck.")

d.heading("John \u2014 Before the Demonstration")
d.item("0:00 \u2014 ", "\u201cThis is the Mount Elgon region of eastern Uganda, on the border with "
       "Kenya. In a moment you are going to watch a weather reading leave it.\u201d")
d.item("0:20 \u2014 ", "\u201cPeople farm the slopes of an extinct volcano, on ground steep enough "
       "that you plant standing sideways. The soil is deep and rich. That is why they are there.\u201d")
d.item("0:45 \u2014 ", "\u201cThere is no electrical grid here. There is no internet. A house is "
       "built from the mountain itself \u2014 earth, poles and thatch.\u201d")
d.item("1:00 \u2014 ", "\u201cWhen people travel, they travel standing on the back of a lorry, on "
       "roads the rain takes out.\u201d  (Skip this one if the clock is ahead.)")
d.item("1:15 \u2014 ", "\u201cA family here makes one decision each year on which everything depends "
       "\u2014 when to plant. That used to be made from experience, because the rains came when they "
       "had always come. They no longer do. Planting a few weeks early or late now costs a family its "
       "year.\u201d")
d.item("1:40 \u2014 ", "\u201cThe second problem is faster. When enough rain falls on a slope already "
       "saturated, the slope moves.\u201d")
d.item("1:55 \u2014 ", "\u201cMudslides kill people on this mountain every year, and they arrive "
       "without warning. The reason there is no warning is simple. Nobody is measuring the rain.\u201d")
d.item("2:15 \u2014 ", "\u201cSo that is what we are about to show you. Not a forecast made somewhere "
       "else \u2014 a measurement, taken where the people are, and carried out of a place with no "
       "infrastructure at all. Gerald.\u201d", after=100)

d.heading("The Demonstration")
d.item("2:30 \u2014 Gerald. ", "The weather sensors, the transceiver, and the Yagi antenna. LoRa radio "
       "\u2014 long range, very little power, and nothing in between. No tower, no subscription, no "
       "wire. Takes a reading.")
d.item("4:30 \u2014 Roger. ", "The receiver built on the MakerPort microcontroller. The reading "
       "Gerald just took arrives on screen.")
d.item("6:30 \u2014 nobody. ", "This minute is deliberately empty. If the link did not take, this is "
       "the retry, and nothing is said about it. The room will wait once. It will not wait twice.",
       after=100)

d.heading("John \u2014 After the Demonstration")
d.item("7:30 \u2014 ", "\u201cNow imagine that not once, but at a hundred points across a mountainside, "
       "each station passing what it measures to the next. One station tells you the weather. A mesh "
       "of them tells you where the rain is falling hardest and how long it has been falling there. "
       "That is the thing nobody in this region has today.\u201d")
d.item("8:00 \u2014 ", "\u201cAnd these are the students who will build it. The goal is not to go and "
       "install weather stations for them. It is a high school engineering program, so that students "
       "fabricate the stations, install them, and maintain them. A station that arrives from outside "
       "lasts until the day it breaks. One built by the person who lives beside it lasts as long as "
       "it is needed.\u201d")
d.item("8:40 \u2014 ", "Questions. Stop on time.", after=100)

# GLEN RENAMED Ver 2.0 in the folder, dropping "Commentary" - a rename keeps the modification time,
# which is how it was spotted. His name wins, and it pairs the script with the deck of the same stem.
print(d.save(DRAFTS, "Networked Weather Station", version="3.0"))
