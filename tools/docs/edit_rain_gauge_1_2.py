"""Rain Gauge (Ver 1.1) -> (Ver 1.2): adds "Open-Source Projects and Potential Collaborators".

Ver 1.1 is Glen's revision of the generated 1.0 (two wording edits, verified by diff), so it is
edited IN PLACE rather than regenerated: the new section's paragraphs are built with makedocx's
own paragraph and table machinery and spliced into document.xml before the References heading,
the new references are merged into the existing alphabetical list, and two sentences of running
text are touched (the introduction's list of what follows; the TAHMO citation gains an "-a" now
that a second TAHMO source exists). Everything else in the file is left as Glen saved it.

Sources for the section were gathered 2026-09-19.
"""

import os, re, shutil, sys, zipfile
import xml.dom.minidom

sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
from makedocx import Doc

W = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\Weather Station"
SRC = os.path.join(W, "Rain Gauge (Ver 1.1).docx")
OUT = os.path.join(W, "Rain Gauge (Ver 1.2).docx")
ARCHIVE = os.path.join(W, "Archive")

# ------------------------------------------------------------------ the new section
d = Doc()


def ref(*parts):
    runs = [(t, False, False) if isinstance(t, str) else (t[0], True, False) for t in parts]
    d._p(runs, after=60, ind=720)
    d.paras[-1] = d.paras[-1].replace('<w:ind w:left="720"/>',
                                      '<w:ind w:left="720" w:hanging="360"/>', 1)
    return d.paras.pop()


I = lambda t: (t,)

d.heading("Open-Source Projects and Potential Collaborators")
d.body(
    "Nobody building a rain gauge for a school in Uganda starts alone. The projects below have "
    "published designs, calibration methods, lesson plans or data practices under open terms, "
    "and several already operate in Kenya and Uganda. They fall into three groups: programs "
    "with stations and partners on the ground in east Africa, open hardware designs a class "
    "could adopt directly, and citizen science practices that show how student readings can "
    "become data others trust. Each entry states what the project offers, how it fits the "
    "MakerPort station, and how contact is made."
)

d.heading("Programs Already Working in East Africa")
d.item("3D-PAWS (UCAR/COMET). ", "The 3D-Printed Automatic Weather Station program of the "
       "University Corporation for Atmospheric Research is the closest match to this project: "
       "printable instruments, a tipping bucket gauge with a published calibration procedure, "
       "and a stated goal that partners build and sustain their own networks rather than buy "
       "commercial sensors. Stations run in Kenya, Uganda, Zambia and Barbados, and the program "
       "has grown to include ultrasonic stream and storm surge gauges (Branscombe, 2022). Paul "
       "Kucera leads the project and Martin Steinson designs the instruments (Branscombe, 2022). "
       "COMET runs on-site workshops on fabricating, calibrating and deploying the stations "
       "through its Innovative Capacity Development Program. Fit: the tipping bucket in Method B "
       "is theirs; a collaboration would put the MakerPort in place of their data logger and the "
       "LoRa link in place of their cellular one. Contact: through the COMET capacity development "
       "program at UCAR (UCAR/COMET, n.d.-b).")
d.item("TAHMO School2School. ", "The Trans-African Hydro-Meteorological Observatory places "
       "most of its 600 stations at secondary schools and pairs each with a sister school in "
       "Africa, Europe or the United States; both schools see the station's live data and share "
       "lesson plans built on it (Trans-African Hydro-Meteorological Observatory, n.d.-b). TAHMO "
       "is headquartered at the Kenya Meteorological Department in Nairobi and has stations in "
       "Uganda. Fit: a TAHMO station near Mount Elgon would be the professional reference the "
       "student gauges are checked against, and the sister-school structure is already the shape "
       "of the Virginia-to-Uganda course. Contact: s2s@tahmo.org (Trans-African "
       "Hydro-Meteorological Observatory, n.d.-b).")
d.item("The GLOBE Program. ", "GLOBE is the NASA-sponsored school science program whose "
       "precipitation protocol has students read a rain gauge daily, record trace amounts, and "
       "enter the readings into a global database (GLOBE Program, n.d.-b). Kenya's GLOBE office "
       "has trained teachers on the protocols and partnered with TAHMO in 2015 to install more "
       "than 25 automatic weather stations at GLOBE schools (GLOBE Program, n.d.-a); Uganda has "
       "its own country pages and teams. Fit: GLOBE supplies the daily reading protocol for the "
       "Method A reference gauge and a place for the readings to go, so that the students' data "
       "join a dataset scientists already use. Contact: the country coordinators listed on the "
       "GLOBE Kenya and Uganda pages.")

d.heading("Open Hardware Designs a Class Could Adopt")
d.item("FreeStation. ", "A collaboration between the Department of Geography at King's College "
       "London and the nonprofit AmbioTEK, FreeStation publishes open designs for data loggers, "
       "weather stations, rain gauges and water level sensors on ESP32 and Raspberry Pi Pico "
       "boards. More than 800 loggers have been built, with agricultural deployments in Burkina "
       "Faso, and the team holds a stock of several hundred loggers for monitoring initiatives "
       "(FreeStation, n.d.). Fit: a second source of printable gauge parts and a tropical "
       "deployment record. Contact: the contact page at freestation.org.")
d.item("OPEnS Lab, Oregon State University. ", "The Openly Published Environmental Sensing "
       "Lab published a 3D-printed calibrator that drips water through a gauge at three set "
       "rates, low, medium and high, so that a gauge can be checked at the intensities that "
       "matter (Lopez Alcala et al., 2019). The design is parametric and shared on GitHub. Fit: "
       "this is the calibration rig for Method B, printable on the same machine as the gauge, "
       "and a seventh-grade class can run it. Contact: the lab's GitHub wiki.")
d.item("OpenPluvio, Verona FabLab. ", "An open hardware and software tipping bucket gauge "
       "from a FabLab in Italy: printed mechanism, hardware-store parts, a reed switch, and a "
       "small Linux logger with a web interface, under a Creative Commons Attribution-ShareAlike "
       "license (Verona FabLab, n.d.). Fit: a FabLab-scale precedent for a class-built gauge; the "
       "logger is heavier than the MakerPort needs, but the mechanism is directly reusable. "
       "Contact: the maintainers named in the repository.")
d.item("Maker Designs for the Radio Link. ", "Two smaller projects solve pieces the station "
       "needs. The MySensors community's printed tipping bucket, designed by the member "
       "BulldogLowell, pairs the mechanism with an Arduino and a low-power radio (MySensors, "
       "n.d.). A LoRaWAN rain gauge by the developer kallemooo counts tips on a Feather board, "
       "sleeps for an hour when no rain falls, and reports battery voltage with each count, "
       "under the MIT license (kallemooo, n.d.). Fit: the second is a worked example of exactly "
       "the counting-and-sleeping program the MakerPort will run over LoRa.")
d.item("MicroBlocks. ", "The MakerPort is programmed in MicroBlocks, whose developers maintain "
       "the pin and sensor libraries the gauge will use (MicroBlocks, n.d.). Fit: a rain gauge "
       "library, or a weather station example, contributed back to MicroBlocks would reach every "
       "school using the language. Contact: the MicroBlocks community forum.")

d.heading("Citizen Science Practices for the Readings")
d.item("Smartphones4Water. ", "S4W runs citizen rainfall networks, most fully in Nepal's "
       "Kathmandu Valley, with gauges built from local materials for about $1.50 and readings "
       "entered through the free Open Data Kit application with a timestamp, a location and a "
       "photograph for quality control (Smartphones4Water, n.d.). A 2025 evaluation found the "
       "citizen readings reliable enough to complement the national network (Duwal et al., "
       "2025). Fit: the model for the Method A reference gauge, and for how a phone can carry a "
       "reading where there is no radio.")
d.item("CoCoRaHS and the Colorado Climate Center. ", "The Community Collaborative Rain, Hail "
       "and Snow Network has thirty years of side-by-side gauge comparisons and a manual-gauge "
       "protocol accepted by the National Weather Service (Colorado Climate Center, 2021). Fit: "
       "the standard for what a reference reading must be, and a network whose Virginia observers "
       "could read alongside the Uganda students.")

d.body("Table 2 sets the projects side by side.", before_list=True)
d.table(
    "Table 2. Open-source projects and their fit with the MakerPort rain gauge",
    ["Project", "Home", "Offers", "Fit", "Contact"],
    [
        ["3D-PAWS", "UCAR/COMET, Colorado; stations in Kenya, Uganda, Zambia",
         "Printed gauge, calibration, workshops", "The Method B gauge and its calibration",
         "COMET capacity development program"],
        ["TAHMO School2School", "Nairobi; stations at 600 African schools",
         "Reference stations, sister schools, lesson plans",
         "Professional reference; the sister-school shape", "s2s@tahmo.org"],
        ["GLOBE Program", "NASA; country offices in Kenya and Uganda",
         "Daily reading protocol, global database", "Where Method A readings go",
         "Country coordinators"],
        ["FreeStation", "King's College London and AmbioTEK",
         "Open logger and gauge designs, 800 built", "Second design source; tropical record",
         "freestation.org contact page"],
        ["OPEnS Lab", "Oregon State University", "Printed three-rate calibrator",
         "Calibration rig for Method B", "GitHub wiki"],
        ["OpenPluvio", "Verona FabLab, Italy", "CC BY-SA tipping bucket",
         "FabLab precedent; reusable mechanism", "Repository maintainers"],
        ["MySensors; kallemooo", "Maker community", "Printed bucket; LoRaWAN tip counter",
         "The counting-and-sleeping program", "GitHub, MySensors forum"],
        ["MicroBlocks", "Open-source project", "The language and its libraries",
         "A shared rain gauge library", "Community forum"],
        ["Smartphones4Water", "Chico, California; Nepal", "$1.50 gauge, ODK phone entry",
         "Model for Method A readings", "Join Us page"],
        ["CoCoRaHS", "Colorado Climate Center", "Manual protocol, gauge comparisons",
         "Standard for a reference reading", "cocorahs.org"],
    ],
    weights=[1.1, 1.5, 1.5, 1.5, 1.2],
)
d.body(
    "An approach in that order, from the programs already on the ground to the design sources "
    "to the data practices, gives the project three things it cannot build for itself: a "
    "professional station to calibrate against, a place for the readings to go, and a "
    "community that has already broken the parts this class is about to print."
)

section_xml = "".join(d.paras).replace("<w:tr><w:trPr>", "<w:tr><w:trPr><w:cantSplit/>")

new_refs = [
    ref("Branscombe, A. (2022, May 3). ", I("Project to bring affordable 3D-printed stream, snow, "
        "and storm surge sensors to remote communities"), ". NCAR & UCAR News. https://news.ucar.edu/"
        "132843/project-bring-affordable-3d-printed-stream-snow-and-storm-surge-sensors-remote-"
        "communities"),
    ref("Duwal, S., Prajapati, R., Upadhyay, S., Neupane, S., Lakhe, H., Thapa, B. R., Davids, "
        "J. C., & Talchabhadel, R. (2025). Leveraging a citizen science approach for rainfall "
        "monitoring: Evaluating performance and reliability to complement standard datasets. ",
        I("Earth Systems and Environment, 10"), "(5), 5523\u20135538. "
        "https://doi.org/10.1007/s41748-025-00920-8"),
    ref("FreeStation. (n.d.). ", I("Low-cost, DIY environmental monitoring for all"),
        ". King's College London and AmbioTEK CIC. https://www.freestation.org/"),
    ref("GLOBE Program. (n.d.-b). ", I("Precipitation"),
        ". https://www.globe.gov/web/atmosphere/protocols/precipitation"),
    ref("GLOBE Program. (n.d.-a). ", I("About & contacts: Kenya"),
        ". https://www.globe.gov/web/kenya/home/contact-info"),
    ref("kallemooo. (n.d.). ", I("rainGaugeLoraWan"), " [Computer software]. GitHub. "
        "https://github.com/kallemooo/rainGaugeLoraWan"),
    ref("Lopez Alcala, J. M., Udell, C. J., & Selker, J. S. (2019). A user-printable three-rate "
        "rain gauge calibration system. ", I("Frontiers in Earth Science, 7"), ", Article 338. "
        "https://doi.org/10.3389/feart.2019.00338"),
    ref("MySensors. (n.d.). ", I("Rain gauge"), ". https://www.mysensors.org/build/rain"),
    ref("Smartphones4Water. (n.d.). ", I("Collecting data with smartphones and citizen "
        "scientists"), ". https://smartphones4water.org/collecting-data-with-smartphones-and-"
        "citizen-scientists-science-story-2/"),
    ref("Trans-African Hydro-Meteorological Observatory. (n.d.-b). ", I("School 2 School"),
        ". https://tahmo.org/school-2-school/"),
    ref("Verona FabLab. (n.d.). ", I("OpenPluvio: Open source (hardware and software) tipping "
        "bucket rain gauge"), " [Computer software]. GitHub. "
        "https://github.com/VeronaFabLabRepo/OpenPluvio"),
]

# ------------------------------------------------------------------ splice into Glen's file
z = zipfile.ZipFile(SRC)
names = z.namelist()
parts = {n: z.read(n) for n in names}
z.close()
dx = parts["word/document.xml"].decode("utf8")

P = re.compile(r"<w:p[ >].*?</w:p>", re.S)


def text(p):
    return "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, flags=re.S))


paras = list(P.finditer(dx))
heads = [m for m in paras if text(m.group(0)).strip() == "References"]
assert len(heads) == 1, "References heading not found once"
ref_head = heads[0]

# 0. UCAR/COMET: "Testing and data validation" sorts before "Tipping bucket rain gauge", so the
# letters in Glen's text were the wrong way round; swap the citations and reorder the two entries
assert dx.count("(UCAR/COMET, n.d.-a)") >= 1 and dx.count("(UCAR/COMET, n.d.-b)") >= 1
dx = (dx.replace("(UCAR/COMET, n.d.-a)", "@@A@@").replace("(UCAR/COMET, n.d.-b)", "(UCAR/COMET, n.d.-a)")
        .replace("@@A@@", "(UCAR/COMET, n.d.-b)"))
pa = [m for m in P.finditer(dx) if text(m.group(0)).startswith("UCAR/COMET. (n.d.-a). Tipping")]
pb = [m for m in P.finditer(dx) if text(m.group(0)).startswith("UCAR/COMET. (n.d.-b). Testing")]
assert len(pa) == 1 and len(pb) == 1 and pa[0].end() <= pb[0].start()
xa = pa[0].group(0).replace("UCAR/COMET. (n.d.-a). Tipping", "UCAR/COMET. (n.d.-b). Tipping")
xb = pb[0].group(0).replace("UCAR/COMET. (n.d.-b). Testing", "UCAR/COMET. (n.d.-a). Testing")
dx = dx[:pa[0].start()] + xb + dx[pa[0].end():pb[0].start()] + xa + dx[pb[0].end():]

# 1. the new section goes immediately before the References heading
dx = dx[:ref_head.start()] + section_xml + dx[ref_head.start():]

# 2. the TAHMO home page becomes (n.d.-a) now that a second TAHMO source exists (before the
#    merge below, so the entry sorts by its final text)
n = dx.count("Trans-African Hydro-Meteorological Observatory, n.d.)")
assert n == 1, n
dx = dx.replace("Trans-African Hydro-Meteorological Observatory, n.d.)",
                  "Trans-African Hydro-Meteorological Observatory, n.d.-a)")
n = dx.count("Trans-African Hydro-Meteorological Observatory. (n.d.). ")
assert n == 1, n
dx = dx.replace("Trans-African Hydro-Meteorological Observatory. (n.d.). ",
                  "Trans-African Hydro-Meteorological Observatory. (n.d.-a). ")

# 3. merge the new references into the alphabetical list after the heading
paras = list(P.finditer(dx))
idx = next(i for i, m in enumerate(paras) if text(m.group(0)).strip() == "References")
existing = [m for m in paras[idx + 1:] if text(m.group(0)).strip()]


def key(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


inserts = {}                                   # insertion point -> refs, alphabetical
for r in sorted(new_refs, key=lambda r: key(text(r))):
    k = key(text(r))
    before = next((m for m in existing if key(text(m.group(0))) > k), None)
    pos = before.start() if before else existing[-1].end()
    inserts.setdefault(pos, []).append(r)
for pos in sorted(inserts, reverse=True):
    dx = dx[:pos] + "".join(inserts[pos]) + dx[pos:]

# 4. the introduction's list of what follows
old = ("A comparison table and a recommended sequence follow, and a References section closes "
       "the document.")
new = ("A comparison table and a recommended sequence follow, then a survey of open-source "
       "projects and potential collaborators, and a References section closes the document.")
assert dx.count(old) == 1
dx = dx.replace(old, new)

parts["word/document.xml"] = dx.encode("utf8")

# ------------------------------------------------------------------ write, then archive 1.1
xml.dom.minidom.parseString(parts["word/document.xml"])
assert not os.path.exists(OUT), OUT
with zipfile.ZipFile(OUT, "x", zipfile.ZIP_DEFLATED) as zo:
    zo.writestr("[Content_Types].xml", parts["[Content_Types].xml"])
    for n in names:
        if n != "[Content_Types].xml":
            zo.writestr(n, parts[n])
os.makedirs(ARCHIVE, exist_ok=True)
shutil.move(SRC, os.path.join(ARCHIVE, os.path.basename(SRC)))
print(OUT)
