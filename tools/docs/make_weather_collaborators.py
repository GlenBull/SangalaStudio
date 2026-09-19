"""Builds "Weather Station Collaborators (Ver N.M).docx" in Design through Making\\Weather Station.

Who is already in the networked weather station group, and which University of Virginia
faculty might be approached. Companion to the Rain Gauge survey, whose own collaborators
section covers the open-source projects beyond the University. Sources gathered 2026-09-19.

Glen's instructions, 2026-09-19: Frackson Mumba and Jennie Chiu have been asked and have other
projects, so they are left out. Rich Nguyen and his graduate students have worked with the
group for ten years and are part of it, not a prospect; he developed FloodWatch.io.

Rebuild with:  python tools\\docs\\make_weather_collaborators.py
"""

import sys

sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
from makedocx import Doc

OUT = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\Weather Station"

d = Doc()


def ref(*parts):
    """APA entry: italic runs where APA wants them; the 0.25 in hanging indent used in the
    Rain Gauge survey's reference list."""
    runs = [(t, False, False) if isinstance(t, str) else (t[0], True, False) for t in parts]
    d._p(runs, after=60, ind=720)
    d.paras[-1] = d.paras[-1].replace('<w:ind w:left="720"/>',
                                      '<w:ind w:left="720" w:hanging="360"/>', 1)


I = lambda t: (t,)

d.title("Weather Station Collaborators")

d.body(
    "The networked weather station for the Mount Elgon region of Uganda draws on a group "
    "already at work and on colleagues at the University of Virginia whose research bears on "
    "it. This document records both: the group as it stands, and the faculty who might be "
    "approached, with the reason in each case. It is a companion to the rain gauge survey, "
    "whose own section on open-source projects covers the potential collaborators beyond the "
    "University, from 3D-PAWS and TAHMO to the GLOBE Program."
)

# ---------------------------------------------------------------- the group
d.heading("The Group as It Stands")
d.item("Roger Wagner and Gerald Knezek. ", "Roger Wagner, of 1010 Technologies, makes the "
       "MakerPort microcontroller on which the station is built (MakerPort, n.d.). With Gerald "
       "Knezek, Regents Professor of Learning Technologies at the University of North Texas "
       "(University of North Texas, n.d.), he built the working prototype: a matched pair of MakerPort boards on 9-volt "
       "batteries, one carrying the sensors and a LoRa transceiver with a whip antenna, the "
       "other the receiver with a three-element Yagi. The pair was demonstrated at the National "
       "Technology Leadership Summit in September 2026, sending a reading across the room with "
       "no tower, no subscription and no wire.")
d.item("John Maloney. ", "The developer of MicroBlocks, the blocks language the station is "
       "programmed in (MicroBlocks, n.d.). The MakerPort was designed expressly to run "
       "MicroBlocks, in a long collaboration with him that predates this project, so the author "
       "of the language is a partner in the work rather than a prospect.")
d.item("Rich Nguyen and His Graduate Students. ", "Nhat (Rich) Nguyen is an Associate Professor "
       "in the Department of Computer Science at the University of Virginia (Nguyen, n.d.). He "
       "and his graduate students have worked with the group for ten years. He developed "
       "FloodWatch.io, a real-time flood forecasting and reporting platform on which residents "
       "of a flood-prone area submit and view flood reports for their locality, and whose "
       "accumulated reports train predictive models and inform city planners (FloodWatch, "
       "n.d.; Kim, 2022). The work has been recognized in the U.S.-ASEAN Smart Cities "
       "Partnership report of December 2023, a patent for validating crowdsourced flood images "
       "was filed in July 2024, and in August 2023 he ran a student workshop on LoRaWAN in "
       "flood prediction (Nguyen, n.d.). In 2026 he also received University funding under the "
       "3Cavs program for a project forecasting malaria outbreaks in Uganda under climate "
       "change, with collaborators in the School of Medicine and the College of Arts and "
       "Sciences (University of Virginia School of Engineering and Applied Science, 2026). "
       "Bearing on the station: FloodWatch is the reporting layer the station does not yet "
       "have. The rain gauge produces the measurement; FloodWatch is a proven way to carry an "
       "alert to the people at risk and to collect what they see. The LoRaWAN work and the "
       "Uganda malaria project, for which rainfall is a primary driver, put his group on both "
       "ends of the same data.")

# ---------------------------------------------------------------- UVA faculty
d.heading("Faculty Who Might Be Approached")
d.body("Four members of the University's faculty work on the questions the station raises: "
       "low-cost environmental sensing, sensors that live without mains power, rainfall "
       "measurement at the scale of a catchment, and the validation of satellite rainfall "
       "against gauges on the ground. None has been approached; the fit is stated for each.",
       before_list=True)
d.item("Jonathan Goodall, Civil and Environmental Engineering. ", "Professor and director of "
       "the Link Lab, the University's cyber-physical systems laboratory. A water resources "
       "engineer working in hydroinformatics, he and his Hydroinformatics Research Group apply "
       "machine learning and cyber-physical systems to real-time flood monitoring and "
       "mitigation, including the retrofitting of stormwater systems with low-cost sensors, "
       "microcontrollers and wireless links (University of Virginia School of Engineering and "
       "Applied Science, n.d.-b). Fit: a student-built gauge network reporting by radio "
       "is a cyber-physical water system of exactly his kind, and the Link Lab is where the "
       "University's sensing and hydrology meet.")
d.item("Brad Campbell, Computer Science and Electrical and Computer Engineering. ",
       "Associate Professor and Link Lab member. His research is in low-power wireless embedded "
       "systems: energy-harvesting sensors, networks of connected devices, and "
       "application-driven sensing deployments, with batteries named as the limit on the "
       "lifetime of deployed sensors (University of Virginia School of Engineering and Applied "
       "Science, n.d.-a). Fit: the station stands where there is no grid, and how long "
       "a 9-volt battery lasts is the question that decides whether it stays up through a wet "
       "season. His group's answer to that question is the one the project needs.")
d.item("Venkataraman Lakshmi, Civil and Environmental Engineering. ", "John L. Newcomb "
       "Professor of Engineering and head of the Global Hydrology and Water Resources Group. He "
       "uses satellite observations of soil moisture, precipitation and vegetation to track "
       "water across the planet, and his election as a Fellow of the American Association for "
       "the Advancement of Science cited his monitoring of hydrological extremes including "
       "floods and landslides (University of Virginia School of Engineering and Applied "
       "Science, n.d.-c). Fit: satellite rainfall products are what the Mount Elgon region "
       "relies on in the absence of gauges, and they are validated against ground gauges the "
       "region does not have. A network of student gauges would supply the ground truth his "
       "field lacks over east Africa, and his landslide work is the hazard the station is "
       "meant to warn of.")
d.item("Todd Scanlon, Environmental Sciences. ", "Professor of Environmental Sciences whose "
       "research is in catchment hydrology and land-atmosphere interaction, combining field "
       "measurement, remote sensing and modeling, with field sites in Shenandoah National Park, "
       "Ireland and southern Africa (University of Virginia Department of Environmental "
       "Sciences, n.d.). Fit: rainfall variability on an African slope is his subject, and he "
       "brings the field experience of keeping instruments running in Africa that the "
       "engineering candidates do not.")

# ---------------------------------------------------------------- routes
d.heading("Institutional Routes")
d.body(
    "Two units of the University connect these people. The Link Lab, which Goodall directs and "
    "Campbell belongs to, is the home of the University's cyber-physical systems research and "
    "the natural host for the sensing side of the station. The Environmental Institute, with "
    "more than a hundred affiliated faculty across ten schools, is the hub for environmental "
    "resilience research and is already funding community-partnered climate resilience projects "
    "in Lesotho and Mozambique (University of Virginia Environmental Institute, n.d.). A station "
    "built by students in Uganda and reporting rainfall where none is measured fits the "
    "Institute's stated program, and it is the route by which Lakshmi and Scanlon would most "
    "naturally be reached."
)

d.body("Table 1 sets out the group and the prospects together.", before_list=True)
d.table(
    "Table 1. The weather station group and the University faculty who might join it",
    ["Name", "Affiliation", "Bearing on the station", "Standing"],
    [
        ["Roger Wagner", "1010 Technologies", "Makes the MakerPort; built the prototype",
         "In the group"],
        ["Gerald Knezek", "Learning Technologies, University of North Texas",
         "Built and demonstrated the prototype",
         "In the group"],
        ["John Maloney", "MicroBlocks", "The language the station runs; the MakerPort was "
         "designed to run it", "In the group"],
        ["Rich Nguyen and students", "Computer Science, UVA",
         "FloodWatch.io reporting platform; LoRaWAN; Uganda malaria forecasting",
         "In the group, ten years"],
        ["Jonathan Goodall", "Civil and Environmental Engineering; Link Lab director",
         "Low-cost sensing for real-time flood monitoring", "To approach"],
        ["Brad Campbell", "Computer Science and ECE; Link Lab",
         "Low-power and energy-harvesting sensors", "To approach"],
        ["Venkataraman Lakshmi", "Civil and Environmental Engineering",
         "Satellite rainfall, floods and landslides; ground validation", "To approach"],
        ["Todd Scanlon", "Environmental Sciences",
         "Catchment hydrology; field sites in Africa", "To approach"],
    ],
    weights=[1.2, 1.5, 2.0, 1.0],
)
# a row never splits across a page
d.paras = [p.replace("<w:tr><w:trPr>", "<w:tr><w:trPr><w:cantSplit/>") for p in d.paras]

# ---------------------------------------------------------------- references
d.heading("References")
ref("FloodWatch. (n.d.). ", I("Floodwatch: Real-time flood monitoring"),
    ". https://www.floodwatch.io/")
ref("Kim, A. (2022). ", I("FloodWatch: A mobile application for real time flood response and "
    "analysis; Understanding the non-technical challenges of gray flooding solutions in coastal "
    "cities"), " [Bachelor's thesis, University of Virginia]. LibraETD. "
    "https://libraetd.lib.virginia.edu/public_view/5h73px14q")
ref("MakerPort. (n.d.). ", I("MakerPort Basic Kit"), ". 1010 Technologies. "
    "https://makerport.fun/shop/makerport-basic-kit/")
ref("MicroBlocks. (n.d.). ", I("MicroBlocks"), ". https://microblocks.fun/")
ref("Nguyen, N. (n.d.). ", I("Rich Nguyen: Home"), ". University of Virginia Department of "
    "Computer Science. https://www.cs.virginia.edu/~nn4pj/")
ref("University of North Texas. (n.d.). ", I("Gerald Knezek, Ph.D."), ". Institute for the "
    "Integration of Technology into Teaching and Learning. "
    "https://iittl.unt.edu/content/gerald-knezek-phd")
ref("University of Virginia Department of Environmental Sciences. (n.d.). ", I("Todd Scanlon"),
    ". https://evsc.as.virginia.edu/people/todd-scanlon")
ref("University of Virginia Environmental Institute. (n.d.). ", I("From Virginia to Africa: New "
    "UVA-led projects pioneer community partnerships for climate resilience"),
    ". https://environment.virginia.edu/news/virginia-africa-new-uva-led-projects-pioneer-"
    "community-partnerships-climate-resilience")
ref("University of Virginia School of Engineering and Applied Science. (2026). ",
    I("13 UVA Engineering faculty funded under University's innovative 3Cavs program"),
    ". https://engineering.virginia.edu/news-events/news/13-uva-engineering-faculty-funded-"
    "under-universitys-innovative-3cavs-program")
ref("University of Virginia School of Engineering and Applied Science. (n.d.-a). ",
    I("Brad Campbell"), ". https://engineering.virginia.edu/faculty/brad-campbell")
ref("University of Virginia School of Engineering and Applied Science. (n.d.-b). ",
    I("Jonathan L. Goodall"), ". https://engineering.virginia.edu/faculty/jonathan-l-goodall")
ref("University of Virginia School of Engineering and Applied Science. (n.d.-c). ",
    I("Venkataraman Lakshmi"),
    ". https://engineering.virginia.edu/faculty/venkataraman-lakshmi")

print(d.save(OUT, "Weather Station Collaborators"))
