"""Appendix: Installation - for the Sangala Studio User Guide. Drafted into _Drafts for review."""
import sys
sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
from makedocx import Doc

OUT = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts"

d = Doc()
d.title("Installation")

d.body("Sangala Studio is published in the Educational CAD Model Library, where it is available to anyone "
       "without charge or registration. Nothing is installed in the usual sense: the program is a folder of "
       "files that is copied to the computer and started from an icon. It needs no administrator rights, no "
       "driver, and no internet connection once it has been copied.")

d.heading("Obtaining the Program")
d.step("Open the entry in a web browser:")
d.code("https://www.cadlibrary.org/objects/V3LXPYQH")
d.step("On the right of the page, under Download, click Computer Software. The program arrives as a single "
       "compressed file, usually in the Downloads folder.")
d.body("The link beside it, Instructional Resources, holds the teaching materials rather than the program. "
       "The entry may also be reached by its permanent identifier, which is the form to use in a citation "
       "or a syllabus:", before_list=True)
d.code("https://doi.org/10.18130/V3/LXPYQH")

d.heading("Installing It on Windows")
d.new_list()
d.step("Find the downloaded file, right-click it, and choose Extract All. Windows offers a location; the "
       "Desktop or the Documents folder are both suitable. Extracting produces a folder holding the "
       "program.")
d.step("Open that folder and double-click Create Desktop Shortcut.cmd. A window opens, reports that the "
       "shortcut was created, and waits; press any key to close it. A Sangala Studio icon now sits on the "
       "Desktop.")
d.step("Double-click that icon. The program starts and opens its page in the web browser.")
d.body("The folder has to stay whole. The program looks for its page and for the assets folder beside "
       "itself, so moving one file out of the folder, or copying only the icon to another computer, leaves "
       "an installation that cannot start. To move the program, move the entire folder and run Create "
       "Desktop Shortcut.cmd once more, which points the icon at the new location.")

d.heading("What the Folder Contains")
d.table(
    "Table 1. The Files That Matter to a New User",
    ["File", "What It Is"],
    [
        ["SangalaStudio.exe", "The program. The Desktop icon points here"],
        ["SangalaStudio.html", "The page the program opens in the browser"],
        ["assets", "The background-removal tools the page loads. Large, and required"],
        ["Create Desktop Shortcut.cmd", "Puts the icon on the Desktop. Run once, and again after moving the folder"],
        ["Update SangalaStudio.cmd", "Fetches a newer version"],
        ["Sangala for Snap.xml", "The blocks Sangala loads into Snap!"],
    ],
    weights=[34, 66])
d.body("The remaining files in the folder are the program's own source code and the license. They are "
       "there because the software is published openly, and nothing needs to be done with them.")

d.heading("Keeping It Up to Date")
d.body("Double-click Update SangalaStudio.cmd. It checks whether a newer version exists and, if one does, "
       "downloads the page and the program together and replaces them. If nothing has changed it reports "
       "that the copy is already current and downloads nothing. If a download fails partway, it changes "
       "nothing at all, so a failed update always leaves a working program.")
d.body("Close Sangala Studio before updating. Windows will not replace a program while it is running, and "
       "the update stops rather than leave the installation half-replaced.")

d.heading("If Windows Warns About the Program")
d.body("Windows may report that it protected the computer, because the program is not signed by a "
       "commercial publisher. Choose More info, then Run anyway. Windows asks once and remembers the "
       "answer.")

d.heading("Other Computers")
d.body("The program also runs on a Mac and on a Chromebook, from the same page and the same browser. Those "
       "versions are distributed separately at present and are not in the download above; the instructions "
       "for each are supplied with them.")

print(d.save(OUT, "Appendix - Installation"))
