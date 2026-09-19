"""Builds "Rain Gauge (Ver N.M).docx" in the _Drafts folder.

A survey of the ways a seventh-grade class could build a rain gauge for the MakerPort
weather station, judged against the conditions of the Mount Elgon region. Sources were
gathered 2026-09-19 and are listed in APA form in the References section at the end.

Rebuild with:  python tools\\docs\\make_rain_gauge.py
The version number is taken from the folder at write time (makedocx never overwrites).
"""

import sys

sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
from makedocx import Doc

OUT = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts"

d = Doc()
d.title("Rain Gauge Methods for a MakerPort Weather Station")

d.body(
    "This survey describes the ways a class of seventh-grade students could build a rain "
    "gauge for a weather station based on the MakerPort microcontroller, and judges each "
    "against the conditions of the Mount Elgon region of east Africa, where the station is "
    "meant to be deployed. The methods run from a marked bottle read by eye to a weighing "
    "gauge read by the board. For each, the survey states the principle, what the students "
    "build, how the MakerPort reads it, and what is likely to go wrong on the mountain. A "
    "comparison table and a recommended sequence follow, and a References section closes "
    "the document."
)

# ---------------------------------------------------------------- setting
d.heading("The Setting: Rainfall on Mount Elgon")
d.body(
    "Mount Elgon is an extinct volcano on the border of Uganda and Kenya. Its climate is "
    "bimodal, with long rains from March to May and short rains from October to November. "
    "Mean annual rainfall across the region runs from 687 mm on the dry northern side to "
    "2,544 mm on the wet southern and western slopes, and the slopes around the mountain "
    "itself typically receive 1,500 to 2,000 mm a year (Nile Basin Initiative, 2024). The "
    "station at Buginyanya, on the Ugandan slopes, averages 2,126 mm (Nile Basin "
    "Initiative, 2024). Rainfall in the Sipi sub-catchment varies strongly from year to "
    "year, and the number of extremely wet and dry events has risen since 2000 (Luwa et "
    "al., 2021). For a gauge, these figures mean two things: a single day can deliver tens "
    "of millimeters, and a wet season can deliver more than a meter."
)
d.body(
    "The rain matters because the slopes move. Landslides on the densely settled footslopes "
    "are triggered by rainfall, with land use and settlement on steep ground lowering the "
    "threshold at which they occur (Knapen et al., 2006; Mugagga et al., 2012). The "
    "landslide of 1 March 2010 at Nametsi, in Bududa District, followed days of continuous "
    "rain and was the worst recorded in Uganda. A study of the early warning systems now in "
    "place in Bududa found that the instrumented site holds one rain gauge, that its data are "
    "interpreted in Kampala rather than in the district, and that nearly half of residents "
    "surveyed did not know any warning system existed (Namwano et al., 2024)."
)
d.body(
    "Measurement is sparse everywhere in the country. Uganda operates 150 manual rain gauges "
    "and no automatic ones apart from those on its weather stations, and the manual gauges are "
    "read by observers who report every ten days (Systematic Observations Financing Facility, "
    "2024). Of 54 traditional climatological stations, 37 are partly operational (Systematic "
    "Observations Financing Facility, 2024). A student-built gauge that reports daily, or "
    "hourly, from a village school would therefore not duplicate an existing measurement. It "
    "would be the only one."
)
d.body(
    "There is a working model for how such a measurement reaches the people who need it. In "
    "five districts of the Mount Elgon region, 14 river gauges are read four times a day by "
    "trained community volunteers, who telephone a community radio station when the level "
    "is dangerous; the radio broadcasts the warning and village committees carry it to the "
    "households at risk (Oxfam in Uganda, 2024). The same report notes that readings stop at "
    "6:00 pm, so the night is unwatched. An automatic gauge is the answer to that gap, and "
    "it is the reason the survey favors methods the MakerPort can read without a person "
    "present."
)

# ---------------------------------------------------------------- requirements
d.heading("What the Gauge Must Do")
d.body("The conditions above, and the standards used by meteorological services, set the "
       "requirements below.", before_list=True)
d.item("Resolution. ", "The World Meteorological Organization standard for a rain gauge is "
       "0.2 mm, with 0.1 mm now preferred for professional use (Barani, 2020; World "
       "Meteorological Organization, 2023). A gauge that resolves 0.5 mm is still useful for "
       "a landslide warning, which turns on totals of tens of millimeters, but 0.2 mm is the "
       "figure to design toward.")
d.item("Collecting Area. ", "The WMO recommends a collector opening of at least 200 cm², with "
       "a horizontal rim and vertical walls so that drops do not splash out (LSI LASTEM, n.d.; "
       "World Meteorological Organization, 2023). A 4-inch (10 cm) funnel gives 81 cm² and is "
       "accepted for the CoCoRaHS volunteer network because it agrees with the reference "
       "gauge to within a few percent (Colorado Climate Center, 2021); a 16 cm funnel gives "
       "the WMO 200 cm².")
d.item("Capacity and Intensity. ", "A storage gauge must hold a full day of the long rains "
       "without overflowing. An automatic gauge must keep counting during a downpour: above "
       "about 50 mm per hour, a tipping bucket loses water in the instant it tips, and the "
       "loss reaches 5 to 15 percent at 100 mm per hour (Dickson, 2026).")
d.item("Wind. ", "Wind is the largest single error in rainfall measurement. A conventional "
       "gauge mounted at 0.5 m on an exposed upland site caught 23 percent less than a "
       "reference gauge set in a pit; at a sheltered lowland site the loss was 9 percent "
       "(Pollock et al., 2018). Siting matters more than sensor choice.")
d.item("Evaporation, Debris and Insects. ", "Water that evaporates before it is measured is "
       "lost; leaves and insects block funnels; standing water breeds mosquitoes. The "
       "collector must be screened and emptied, and the funnel must drain into a narrow "
       "container that limits the exposed surface (Randall, 2026).")
d.item("Power and Communication. ", "The site has no electrical grid and no internet. The "
       "station runs from a battery and passes readings by LoRa radio, so the gauge must "
       "draw almost nothing and must produce a signal the MakerPort can read.")
d.item("Local Repair. ", "The station is meant to be built, installed and maintained by the "
       "students who live beside it. Every part should be something they can print, cut or "
       "buy in Mbale, and every calibration should be one they can repeat with a syringe and "
       "a kitchen scale. The 3D-PAWS program reached the same conclusion in Zambia, where the "
       "case for a 3D-printed station was that a broken part could be printed again locally "
       "(Hosansky, 2016).")

# ---------------------------------------------------------------- MakerPort
d.heading("What the MakerPort Can Read")
d.body(
    [("The MakerPort is a classroom microcontroller from 1010 Technologies, programmed in "
      "MicroBlocks, Scratch or Snap", False, False), ("!", True, False),
     (". The board offers one analog input, an extra four-pin port "
      "with digital input and output, an I2C connector for displays and sensors, two servo "
      "ports, a twelve-pin capacitive touch port, and USB-C or 9-volt battery power (MakerPort, "
      "n.d.). For a rain gauge, three of those matter:", False, False)],
    before_list=True)
d.item("A Digital Pin. ", "MicroBlocks reads a digital pin as true or false, with an "
       "optional pull-up that holds the line high until a switch pulls it to ground "
       "(MicroBlocks, n.d.). This is exactly what a reed switch or Hall-effect sensor on a "
       "tipping bucket produces: one closure per tip. A MicroBlocks loop that watches the "
       "pin, adds one to a counter when it closes, and waits for it to open again before "
       "counting the next, is a complete rain gauge program. The wait is the debounce; a reed "
       "switch chatters for a few tens of milliseconds on each closure (Dickson, 2026).")
d.item("The Analog Input. ", "MicroBlocks reads an analog pin as a number from 0 to 1023 "
       "(MicroBlocks, n.d.). A float on a potentiometer, a resistive level strip, or a "
       "distance sensor with an analog output can each report a water level this way.")
d.item("The I2C Connector. ", "Digital sensors with an I2C interface, such as a load-cell "
       "amplifier or an ultrasonic rangefinder module, connect here and are read through a "
       "MicroBlocks library. This is the route for a weighing gauge.")
d.body(
    "The prototype station built by Roger Wagner and Gerald Knezek pairs two MakerPort "
    "boards, each on a 9-volt battery, one carrying the sensors and a transceiver with a "
    "whip antenna, the other the receiver with a three-element Yagi. The rain gauge joins "
    "the sensing board. Whatever method is chosen, the number that crosses the radio link is "
    "a count of tips or a level reading; the conversion to millimeters can happen on either "
    "end."
)

# ---------------------------------------------------------------- Method A
d.heading("Method A: The Storage Gauge Read by Eye")
d.item("Principle. ", "Rain falls through a funnel into a straight-sided container and the "
       "depth is read against a scale. If the funnel opening is larger than the container, "
       "the depth is magnified by the ratio of the two areas, so a small rainfall becomes a "
       "readable column. The CoCoRaHS 4-inch gauge works this way: a 4-inch funnel drains "
       "into a narrow inner tube so that one inch of rain stands ten inches tall, and an "
       "outer cylinder catches the overflow (Colorado Climate Center, 2021).")
d.item("What Students Build. ", "The classroom version is a two-liter bottle cut below the "
       "shoulder, its top inverted as a funnel, gravel in the base to bring the water level "
       "up to the straight-sided section, and a scale marked from the top of the gravel "
       "(NASA Global Precipitation Measurement Mission, n.d.). A seventh-grade class can go "
       "one step further and build the magnifying version: a wide funnel from a cut bottle "
       "or a 3D-printed ring, draining into a narrow tube such as a graduated cylinder or a "
       "length of clear pipe. The magnification is the area of the funnel divided by the "
       "area of the tube, and the students compute it, mark the scale, and then check it by "
       "pouring a known volume from a syringe. NASA's design challenge for this age group "
       "makes calibration the central lesson (NASA Global Precipitation Measurement Mission, "
       "n.d.).")
d.item("How the MakerPort Reads It. ", "It does not. This gauge is read by a person, once a "
       "day at a fixed hour, and the reading is entered by hand.")
d.item("Reliability on Mount Elgon. ", "This is the most reliable method on the list, and "
       "the reason is that it has nothing to fail. The CoCoRaHS network refuses automated "
       "readings because in three decades of side-by-side tests its manual gauge caught 101 "
       "to 105 percent of the reference gauge, while most automatic gauges under-read, by 10 "
       "percent or more on days of intense rain (Colorado Climate Center, 2021). The costs are "
       "the ones already seen in the river-gauge program: someone must be there, and nobody "
       "is there at night. A thin film of cooking oil on the water slows evaporation between "
       "readings; a screen over the funnel keeps out leaves and mosquitoes.")
d.item("Verdict. ", "Build it first, and keep it beside every automatic gauge for the life of "
       "the station. It is the calibration reference the other methods are checked against, "
       "and on the day the electronics fail it is the measurement.")

# ---------------------------------------------------------------- Method B
d.heading("Method B: The Tipping Bucket")
d.item("Principle. ", "A funnel drains onto a small seesaw with a bucket at each end. When "
       "one bucket holds a set volume it tips, empties, and brings the other bucket under "
       "the spout. A magnet on the seesaw passes a reed switch or Hall-effect sensor on each "
       "tip, and the count of tips times the depth per tip is the rainfall (Dickson, 2026). "
       "The depth per tip is set by the bucket volume and the funnel area: a 200 cm² funnel "
       "and a 4 cm³ bucket give 0.2 mm per tip.")
d.item("What Students Build. ", "The 3D-PAWS program of the University Corporation for "
       "Atmospheric Research publishes printable parts, assembly videos and a calibration "
       "spreadsheet for a tipping bucket gauge that uses an SS451A Hall-effect sensor "
       "(UCAR/COMET, n.d.-a). Students print the seesaw, funnel and frame, fit a magnet and "
       "the sensor, and mount the assembly level. A version with a reed switch instead of a "
       "Hall sensor needs no power at all on the sensor side. Calibration follows the "
       "3D-PAWS procedure: cycle the mechanism a thousand times to bed in the pivot, pour "
       "water through it for several hundred tips, weigh the water that came out, divide by "
       "the tips to get grams per tip, and then size the funnel rim so that one tip equals "
       "0.2 mm (UCAR/COMET, n.d.-a). The arithmetic is a cylinder volume, within reach of "
       "seventh grade. In the classroom the water comes from a syringe or a dripping bottle "
       "rather than a pump.")
d.item("How the MakerPort Reads It. ", "One digital pin with the pull-up enabled, the "
       "switch between the pin and ground, and the counting loop described above. The count "
       "is sent by radio each interval and reset.")
d.item("Reliability on Mount Elgon. ", "The tipping bucket is the standard automatic gauge "
       "worldwide because it is simple, cheap and needs no emptying. Its weaknesses are "
       "known and each has a remedy. The base must be within one degree of level or one "
       "bucket tips before the other; the travel stops must be symmetric within half a "
       "millimeter (Dickson, 2026). Debris across the funnel screen stops the flow entirely, "
       "so the screen must be cleared after every storm season. In heavy rain, water "
       "arriving during the tip is lost, which on Mount Elgon will happen in every long-rains "
       "downpour; the loss is a few percent and is systematic, so the manual gauge beside it "
       "measures it and a correction can be applied (Dunn et al., 2025). The 3D-PAWS gauge "
       "held to less than 5 percent error at laboratory rates from 0.1 to 30 mm per hour and "
       "tracked a reference weighing gauge over 200 mm of field rainfall (UCAR/COMET, "
       "n.d.-b). Printed plastic softens in equatorial sun; a light-colored print in PETG or "
       "ASA, or a funnel cut from sheet aluminum, lasts longer than PLA.")
d.item("Verdict. ", "The recommended automatic gauge. Every part can be printed, the sensor "
       "costs a dollar, the program is a counter, and the calibration is a science lesson in "
       "itself.")

# ---------------------------------------------------------------- Method C
d.heading("Method C: The Weighing Gauge")
d.item("Principle. ", "The collecting container stands on a load cell and the electronics "
       "weigh it. One gram of water over a known funnel area is a known depth, so the weight "
       "is the rainfall, continuously, with no moving parts. Weighing gauges are the "
       "reference instruments of national services because they are accurate at every "
       "intensity, from drizzle to cloudburst (Randall, 2026); the 3D-PAWS field test used "
       "one as its reference (UCAR/COMET, n.d.-b).")
d.item("What Students Build. ", "A bar load cell of 1 to 5 kg capacity, an HX711 amplifier "
       "board, a platform, and a container with a funnel. The HX711 turns the microvolt "
       "output of the load cell into a 24-bit number; calibration is a single step, placing a "
       "known mass on the platform and dividing (Prabhu, 2026). A hobby scale of this kind "
       "reaches a resolution of a tenth of a gram, which on a 100 cm² funnel is a hundredth "
       "of a millimeter of rain.")
d.item("How the MakerPort Reads It. ", "The HX711 speaks a two-wire clock-and-data protocol "
       "rather than I2C, so it needs a MicroBlocks library and two digital pins from the "
       "extra port. An I2C load-cell amplifier avoids the library but costs more. This is "
       "the most demanding wiring on the list.")
d.item("Reliability on Mount Elgon. ", "The mechanism is the strong point and the "
       "electronics are the weak one. A load cell drifts with temperature and creeps under "
       "sustained load, and an outdoor gauge sees both every day; the fix is to read the "
       "difference between successive readings rather than the absolute weight, so slow "
       "drift cancels. The container fills and must be emptied by hand or by a siphon, and "
       "an open container evaporates. A wet season of 1,000 mm on a 100 cm² funnel is ten "
       "liters of water, so either the container is large or someone empties it weekly. Wind "
       "shakes the platform, so the readings must be averaged.")
d.item("Verdict. ", "The most accurate automatic method and the hardest to keep true "
       "outdoors. Suitable for a class that has already built a tipping bucket and wants to "
       "understand why the professionals weigh instead of tip; not the first gauge to deploy.")

# ---------------------------------------------------------------- Method D
d.heading("Method D: Level Sensing in a Collecting Tube")
d.item("Principle. ", "The magnifying storage gauge of Method A is kept, and a sensor "
       "replaces the eye. Three sensors fit the MakerPort's inputs:", )
d.item("A Float on a Potentiometer. ", "A float in the tube turns a lever on a rotary "
       "potentiometer, and the analog input reads the angle. This is the mechanism of a fuel "
       "gauge. It is cheap and readable, but the float sticks, the wiper corrodes, and the "
       "range is limited by the lever arc.", ind=720)
d.item("Capacitive Strips. ", "Two foil strips down the outside of the tube form a "
       "capacitor whose value rises with the water level between them. The MakerPort's "
       "touch port is a capacitance sensor with twelve inputs (MakerPort, n.d.), so a row of "
       "touch points along the tube reports which are wetted and the level is read as a "
       "count of points. It is the most MakerPort-native method here. Its limit is that "
       "capacitance also responds to humidity and to the condensation on the tube wall "
       "(Renke, n.d.), and both are constant companions in the tropics; the reading is a "
       "step function, not a depth.", ind=720)
d.item("An Ultrasonic Rangefinder. ", "A rangefinder above the tube measures the distance "
       "to the water surface. The 3D-PAWS program uses this arrangement for stream and "
       "storm-surge gauges (UCAR/COMET, n.d.-a), and a distance sensor is among the "
       "MakerPort's listed options. In a narrow tube echoes from the wall confuse the "
       "reading, so the tube must be wide, which undoes the magnification.", ind=720)
d.item("What Students Build. ", "The bottle gauge, plus the sensor of their choice, plus a "
       "way to empty the tube. Without emptying, the tube fills in a week of the long rains; "
       "a siphon that dumps the tube when it is full is a classic mechanism and a good "
       "problem for the class.")
d.item("How the MakerPort Reads It. ", "The analog input for the float, the touch port for "
       "the strips, the I2C connector or a digital pin for the rangefinder.")
d.item("Reliability on Mount Elgon. ", "Every version shares the storage gauge's exposure "
       "to evaporation and debris and adds a sensor in contact with, or above, standing "
       "water. None resolves 0.2 mm. The capacitive version is the one most likely to be "
       "attempted because the board makes it easy, and the one most likely to read the "
       "morning dew as rain.")
d.item("Verdict. ", "A good classroom experiment in how sensors work, and a fair way to "
       "compare an analog reading with a count. Not a deployment gauge.")

# ---------------------------------------------------------------- Method E
d.heading("Method E: Counting or Listening to the Drops")
d.item("Principle. ", "Instead of collecting the rain, the sensor registers each drop. An "
       "optical gauge passes a light beam across the funnel outlet and counts the "
       "interruptions. An impact gauge listens: a piezoelectric disc under a plate turns each "
       "drop into a voltage pulse whose size depends on the drop (Antonini et al., 2022), "
       "and an inductive gauge measures the vibration of a metal plate above a coil "
       "(Clemens et al., 2022).")
d.item("What Students Build. ", "A piezo disc, as used in a buzzer, glued under a metal "
       "lid, wired to the analog input. Students will see rain as a stream of pulses within "
       "an afternoon. Turning the pulses into millimeters is another matter: the "
       "piezoelectric prototype above needed a co-located commercial disdrometer and "
       "machine learning to calibrate (Antonini et al., 2022), and the inductive prototype "
       "cost about 150 euros in parts (Clemens et al., 2022).")
d.item("How the MakerPort Reads It. ", "The analog input, sampled as fast as MicroBlocks "
       "allows, with the program counting peaks above a threshold. Heavy rain merges the "
       "peaks and the count saturates.")
d.item("Reliability on Mount Elgon. ", "Drop sensors fail exactly where the station needs "
       "to work: in heavy rain, wind and thunder, where the background noise swamps the "
       "signal (Antonini et al., 2022). They have no moving parts and nothing to empty, "
       "which is attractive, but the calibration cannot be done in a classroom.")
d.item("Verdict. ", "An enrichment activity that shows a class what a research instrument "
       "looks like. It reports that it is raining, and roughly how hard; it does not report "
       "how much.")

# ---------------------------------------------------------------- comparison
d.heading("Comparison")
d.body("Table 1 sets the five methods against the requirements.", before_list=True)
d.table(
    "Table 1. Rain gauge methods compared against the requirements of a MakerPort station "
    "on Mount Elgon",
    ["Method", "Resolution", "Read by", "Parts", "Weak point on Mount Elgon", "Role"],
    [
        ["A. Storage gauge", "0.2 mm with a magnifying tube", "A person, once a day",
         "Bottle, tube, scale", "Nobody reads it at night; evaporation between readings",
         "Reference gauge beside every other"],
        ["B. Tipping bucket", "0.2 mm per tip", "Digital pin, counted",
         "Printed parts, magnet, reed or Hall sensor",
         "Loses a few percent in downpours; must stay level and unblocked",
         "The automatic gauge to deploy"],
        ["C. Weighing gauge", "0.01 mm", "HX711 on two digital pins, or I2C",
         "Load cell, amplifier, platform, container",
         "Drift and creep; must be emptied; wind shakes it",
         "Second-year project"],
        ["D. Level sensing", "1 mm or coarser", "Analog input, touch port, or I2C",
         "Bottle gauge plus a sensor and a siphon",
         "Reads humidity and dew; evaporation; no 0.2 mm resolution",
         "Classroom experiment"],
        ["E. Drop sensing", "Not a depth", "Analog input, peaks counted",
         "Piezo disc or optical gate",
         "Saturates in heavy rain; cannot be calibrated in class",
         "Enrichment"],
    ],
    weights=[1.1, 1.0, 1.1, 1.3, 1.7, 1.2],
)

# ---------------------------------------------------------------- siting
d.heading("Siting and Maintenance on the Mountain")
d.body("The gauge's accuracy is decided as much by where it stands as by how it is built. "
       "The practices below come from the WMO guide and from the undercatch literature.",
       before_list=True)
d.item("Height. ", "The WMO sets the orifice at least 30 cm above the ground, and 0.5 to 1.5 m "
       "is common practice (World Meteorological Organization, 2023). Lower is better for "
       "wind: the same gauge at 0.5 m caught 11 percent less than a pit gauge, and at 1.5 m "
       "17.5 percent less (Pollock et al., 2018). On a slope the ground itself shelters the "
       "downhill side, so a level bench cut into the slope, with the gauge at knee height, is "
       "a fair compromise.")
d.item("Exposure. ", "An open site, away from trees and buildings by at least twice their "
       "height, so that the wind is neither blocked nor funneled (Randall, 2026). A school "
       "compound usually offers one. The TAHMO network places most of its 600 African "
       "stations at secondary schools, because a school gives the instrument physical and "
       "social protection and gives the students a reason to look after it (Trans-African "
       "Hydro-Meteorological Observatory, n.d.).")
d.item("Level. ", "The rim horizontal, checked with a bubble level at installation and after "
       "every storm season. A tipping bucket out of level by one degree reads wrong (Dickson, "
       "2026).")
d.item("Screening. ", "A mesh over the funnel against leaves and insects, and a narrow outlet "
       "so that mosquitoes cannot reach standing water. Clear the mesh after each storm at "
       "first, and then at the interval experience shows.")
d.item("The Reference Gauge. ", "The Method A gauge beside the automatic one, read every "
       "morning by the same student at the same hour, with the two readings logged together. "
       "The ratio between them is the automatic gauge's catch efficiency, and a change in "
       "that ratio is the first sign that something has gone wrong.")
d.item("Records. ", "The WMO asks that the orifice dimensions, its height above ground and "
       "the site be documented (LSI LASTEM, n.d.). A page in the class notebook with a "
       "photograph, a sketch, the funnel diameter and the calibration figure makes the "
       "measurement usable by anyone who inherits the station.")

# ---------------------------------------------------------------- sequence
d.heading("A Recommended Sequence for a Seventh-Grade Class")
d.body("The methods build on one another, and the order below lets each one calibrate the "
       "next.", before_list=True)
d.step("Build the bottle gauge (Method A) and calibrate it with a syringe: pour 10 mL, read "
       "the depth, compare with the depth the funnel area predicts. This is the lesson in "
       "what a millimeter of rain is.")
d.step("Build the magnifying version, computing the area ratio, and stand the two side by "
       "side through a rain. The class now has a reference gauge.")
d.step("Print and assemble the tipping bucket (Method B), and calibrate it by counting tips "
       "while a known volume drips through. Adjust the funnel or the bucket stops until a "
       "tip is 0.2 mm.")
d.step("Write the MicroBlocks counter: read the pin with the pull-up on, add one on each "
       "closure, wait for the release, and show the running total on the display.")
d.step("Connect the counter to the sensing MakerPort of the weather station and send the "
       "count over the radio link with the other readings.")
d.step("Deploy the tipping bucket and the reference gauge together, level and screened, at "
       "the chosen site. Log both readings daily and compute the catch ratio.")
d.step("Offer Methods C, D and E as investigations for students who finish early, with the "
       "deployed pair as the standard they are measured against.")
d.body("Deployed this way, the station reports rainfall through the night, when the river "
       "readers have gone home, and the students who built it hold the calibration record, "
       "the spare parts and the knowledge to fix it. That is the difference between a gauge "
       "that arrives and a gauge that lasts.")

# ---------------------------------------------------------------- references
d.heading("References")


def ref(*parts):
    """One APA reference: italic runs where APA wants them, hanging indent of 0.5 in.

    Doc._p takes a left indent only, so the hanging value is patched into the paragraph
    it just appended; this stays in the generator rather than growing makedocx for one
    document.
    """
    runs = [(t, False, False) if isinstance(t, str) else (t[0], True, False) for t in parts]
    d._p(runs, after=60, ind=720)
    d.paras[-1] = d.paras[-1].replace('<w:ind w:left="720"/>',
                                      '<w:ind w:left="720" w:hanging="720"/>', 1)


I = lambda t: (t,)   # marks an italic run

ref("Antonini, A., Melani, S., Mazza, A., Baldini, L., Adirosi, E., & Ortolani, A. (2022). "
    "Development and calibration of a low-cost, piezoelectric rainfall sensor through "
    "machine learning. ", I("Sensors, 22"), "(17), Article 6638. "
    "https://doi.org/10.3390/s22176638")
ref("Barani, J. (2020, January 20). ", I("Rain gauge accuracy and WMO/NWS standards"),
    ". BARANI DESIGN Technologies. https://www.baranidesign.com/faq-articles/2020/1/19/"
    "rain-gauge-accuracy-and-wmonws-standards")
ref("Clemens, C., Jobst, A., Radschun, M., Himmel, J., Kanoun, O., & Quirmbach, M. (2022). "
    "Development of an inductive rain gauge. ", I("Sensors, 22"), "(15), Article 5486. "
    "https://doi.org/10.3390/s22155486")
ref("Colorado Climate Center. (2021). ", I("Why CoCoRaHS requires manual measurements"),
    ". Community Collaborative Rain, Hail and Snow Network. "
    "https://media.cocorahs.org/docs/WhyManualGauge_3-21.pdf")
ref("Dickson, R. (2026, April 26). ", I("Tipping bucket rain gauge mechanism: How it works, "
    "parts, diagram, and formula explained"), ". FIRGELLI Automations. "
    "https://www.firgelliauto.com/blogs/mechanisms/tipping-bucket-rain-gauge")
ref("Dunn, R. E., Fowler, H. J., Green, A. C., & Lewis, E. (2025). Tipping-bucket rain "
    "gauges: A review of the undercatch phenomenon, and methods for its reduction and "
    "correction. ", I("Weather, 80"), "(6), 196\u2013205. https://doi.org/10.1002/wea.7736")
ref("Hosansky, D. (2016, June 2). ", I("3D-printed weather stations fill gaps in developing "
    "world"), ". NCAR & UCAR News. https://news.ucar.edu/21287/3d-printed-weather-stations-"
    "fill-gaps-developing-world")
ref("Knapen, A., Kitutu, M. G., Poesen, J., Breugelmans, W., Deckers, J., & Muwanga, A. "
    "(2006). Landslides in a densely populated county at the footslopes of Mount Elgon "
    "(Uganda): Characteristics and causal factors. ", I("Geomorphology, 73"), "(1\u20132), "
    "149\u2013165. https://doi.org/10.1016/j.geomorph.2005.07.004")
ref("LSI LASTEM. (n.d.). ", I("Why the size of a rain gauge orifice is crucial: WMO guidance "
    "and risks of oversized openings"), ". https://lsi-lastem.com/blog/rain-gauge-orifice-wmo/")
ref("Luwa, J. K., Majaliwa, J. G. M., Bamutaze, Y., Kabenge, I., Pilesj\u00f6, P., Oriangi, "
    "G., & Bagula Mukengere, E. (2021). Variabilities and trends of rainfall, temperature, "
    "and river flow in Sipi sub-catchment on the slopes of Mt. Elgon, Uganda. ",
    I("Water, 13"), "(13), Article 1834. https://doi.org/10.3390/w13131834")
ref("MakerPort. (n.d.). ", I("MakerPort Basic Kit"), ". 1010 Technologies. "
    "https://makerport.fun/shop/makerport-basic-kit/")
ref("MicroBlocks. (n.d.). ", I("Pins"), ". MicroBlocks Wiki. "
    "https://wiki.microblocks.fun/en/reference_manual/pins")
ref("Mugagga, F., Kakembo, V., & Buyinza, M. (2012). Land use changes on the slopes of "
    "Mount Elgon and the implications for the occurrence of landslides. ",
    I("Catena, 90"), ", 39\u201346. https://doi.org/10.1016/j.catena.2011.11.004")
ref("Namwano, S., Lubega, J., Mirembe, D., & Akwango-Aliau, D. (2024). Analysis of existing "
    "landslide early detection and warning systems \u201ca case of Bududa District, "
    "Uganda\u201d. ", I("Discover Geoscience, 2"), ", Article 59. "
    "https://doi.org/10.1007/s44288-024-00063-9")
ref("NASA Global Precipitation Measurement Mission. (n.d.). ",
    I("Rain gauge design challenge"),
    ". https://gpm.nasa.gov/education/interactive/rain-gauge-design-challenge")
ref("Nile Basin Initiative. (2024). ", I("Mt. Elgon aquifer: Final shared aquifer diagnostic "
    "analysis (SADA) report"), ". IGAD Ground Water Resources Centre. "
    "https://water.igad.int/resources/2024/11/Mount_Elgon_SADA_Report__002_.pdf")
ref("Oxfam in Uganda. (2024, February 1). ", I("River gauges providing early warnings on "
    "floods to communities in the Mt Elgon region"), ". https://uganda.oxfam.org/latest/"
    "stories/river-gauges-providing-early-warnings-floods-communities-mt-elgon-region")
ref("Pollock, M. D., O\u2019Donnell, G., Quinn, P., Dutton, M., Black, A., Wilkinson, M. E., "
    "Colli, M., Stagnaro, M., Lanza, L. G., Lewis, E., Kilsby, C. G., & O\u2019Connell, "
    "P. E. (2018). Quantifying and mitigating wind-induced undercatch in rainfall "
    "measurements. ", I("Water Resources Research, 54"), "(6), 3863\u20133875. "
    "https://doi.org/10.1029/2017WR022421")
ref("Prabhu, S. (2026, January 20). ", I("Build a digital weighing scale with HX711 and "
    "Arduino"), ". Last Minute Engineers. https://lastminuteengineers.com/hx711-load-cell-"
    "digital-weighing-scale-arduino-tutorial/")
ref("Randall, K. (2026, February 17). ", I("Why measuring rainfall is harder than you "
    "think"), ". Campbell Scientific. "
    "https://www.campbellsci.com/blog/measuring-rainfall-geoprofessionals")
ref("Renke. (n.d.). ", I("Top 5 rain sensor types and selection guide"),
    ". https://www.renkeer.com/rain-sensor-types-and-selection-guide/")
ref("Systematic Observations Financing Facility. (2024, May 8). ", I("GBON national gap "
    "analysis: Uganda"), ". World Meteorological Organization. https://un-soff.org/"
    "wp-content/uploads/2024/05/Uganda-GBON-National-Gap-Analysis.pdf")
ref("Trans-African Hydro-Meteorological Observatory. (n.d.). ", I("Home"),
    ". https://tahmo.org/")
ref("UCAR/COMET. (n.d.-a). Tipping bucket rain gauge. In ", I("3D-PAWS manual"),
    ". University Corporation for Atmospheric Research. https://3dpaws.comet.ucar.edu/"
    "building-3d-paws/building-the-core-instruments/tipping-bucket-rain-gauge")
ref("UCAR/COMET. (n.d.-b). Testing and data validation. In ", I("3D-PAWS manual"),
    ". University Corporation for Atmospheric Research. https://3dpaws.comet.ucar.edu/"
    "3d-printed-automatic-weather-station-3d-paws/testing-and-data-validation")
ref("World Meteorological Organization. (2023). ", I("Guide to instruments and methods of "
    "observation: Volume I \u2013 Measurement of meteorological variables"),
    " (WMO-No. 8, 2023 ed.). https://library.wmo.int/")

print(d.save(OUT, "Rain Gauge"))
