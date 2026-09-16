"""Builds "Allowing the Sangala Studio Updater Through Windows Security" in _Drafts.

Asked for by Glen on 2026-09-15, so that others can follow the same procedure. The content is
NOT written from general knowledge about Windows. It comes from two verified sources:

  * "Update SangalaStudio.cmd" itself, read on 2026-09-15. It does `cd /d "%~dp0"` and creates
    SangalaStudio.html.new, SangalaStudio.exe.new and "Sangala for Snap.xml.new" IN ITS OWN
    FOLDER - not in the system temp directory, as an earlier note in the project guide loosely
    said. That is why a write block and a network failure produce the same message. The failure
    text in the document is quoted from the :failed label, character for character.

  * The diagnosis given to Glen on 2026-08-21 when Jo Watts's updater failed: the two Windows
    mechanisms that produce it, and the fix that needs no security settings touched at all.

WHAT IS NOT VERIFIED, and is flagged to Glen rather than buried: the click path through the
Windows Security application. Access to that application was requested on this machine so the
page and button names could be read from the screen, and was declined; Controlled folder access
is Off here (Get-MpPreference reports EnableControlledFolderAccess 0), so the condition cannot
be reproduced locally either. Those two paths should be confirmed once on a machine that shows
the problem before the document is circulated.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from makedocx import Doc

DRAFTS = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts")

d = Doc()
d.title("Allowing the Sangala Studio Updater Through Windows Security")

d.body("Sangala Studio is kept current by a small script, Update SangalaStudio.cmd, which "
       "downloads the newest files and puts them in place of the old ones. Everything it does is "
       "ordinary, and none of it requires administrator rights. It is also, from the point of view "
       "of Windows 11, an exact match for the behavior of software that should not be trusted: a "
       "script that fetches a program from the internet, closes a running program, and overwrites "
       "files in place. When Windows steps in, the update stops, and the message on screen names "
       "the internet rather than the real cause. This note explains how to tell the two apart, and "
       "what may be changed when Windows is the reason.")

d.heading("What the Failure Looks Like")
d.body("The window closes on three lines:", before_list=True)
d.listing("Update FAILED - could not download a complete copy.\n"
          "Your current Sangala Studio was NOT changed, so it still works.\n"
          "Check the internet connection and run this again.")
d.body("The second line is worth reading carefully. The updater is written so that nothing is "
       "replaced until every file has arrived complete, so a failed update leaves the working "
       "program exactly as it was. Nothing has been damaged, and running the update again costs "
       "nothing.")
d.body("The third line is the misleading one. The same message appears whether the download "
       "failed or Windows refused to let the files be written, because from inside the script the "
       "two are indistinguishable: in both cases the expected file is not there afterward.")

d.heading("Why Windows Security Can Be the Cause")
d.body("The updater works in its own folder. Before it changes anything, it creates three "
       "temporary files beside the program:", before_list=True)
d.listing("SangalaStudio.html.new\n"
          "SangalaStudio.exe.new\n"
          "Sangala for Snap.xml.new")
d.body("Only when all three are present and have passed their checks does it replace the real "
       "files, keeping the previous versions as .bak copies. So the very first thing the updater "
       "does is write into its own folder. If Windows will not permit that, every download "
       "\u201cfails\u201d while the network is working perfectly.")
d.body("Three behaviors attract attention, and any of them can produce the failure:", before_list=True)
d.item("Writing into its own folder. ",
       "Ransomware is recognized in part by a program rewriting files in place, which is also a "
       "fair description of an updater.")
d.item("Downloading a program file. ",
       "SangalaStudio.exe is not signed by a commercial certificate, because signing costs money "
       "annually and the program is free. An unsigned program fetched by a script is treated with "
       "more suspicion than the same file downloaded in a browser.")
d.item("Closing a running program. ",
       "The engine holds its own file open while it runs, so the updater closes it first. Ending "
       "another program is itself a watched behavior.", after=100)

d.heading("The First Check: Can Anything Be Written to the Folder")
d.body("This takes a few seconds and settles the simplest case.", before_list=True)
d.step("Open the folder that holds SangalaStudio.exe.")
d.step("Right-click an empty part of the window and choose New, then Text Document.")
d.step("If Windows refuses, or asks for an administrator, the folder is the whole problem.")
d.body("A program folder that cannot be written to is usually one in Program Files, one placed "
       "there by an administrator, or one inside a managed or synced location. Sangala Studio is "
       "designed to run entirely as an ordinary user, so it must live somewhere the person using "
       "it owns.")

d.heading("The Second Check: Controlled Folder Access")
d.body("If the text document was created without complaint and the update still fails, the likely "
       "cause is Controlled folder access. This is Windows 11's ransomware protection, and it "
       "behaves in a way that makes it easy to miss: it permits File Explorer to write to "
       "Documents, Desktop and Pictures, while silently refusing the same folders to a script. The "
       "first check therefore passes and the updater still cannot work.", before_list=True)
d.new_list()
d.step("Open Windows Security from the Start menu.")
d.step("Choose Virus & threat protection.")
d.step("Scroll to Ransomware protection and choose Manage ransomware protection.")
d.step("Read whether Controlled folder access is On or Off.")
d.body("If it is Off, this is not the cause and the next section does not apply. If it is On, and "
       "the Sangala Studio folder sits inside Documents, Desktop or Pictures, it is almost "
       "certainly the cause.")

d.heading("The Remedy That Changes No Settings")
d.body("The simplest resolution is to move the program rather than to weaken the protection. "
       "Controlled folder access guards a specific list of folders, and a folder outside that list "
       "is not affected.", before_list=True)
d.new_list()
d.step("Create a folder directly under the user folder, for example C:\\Users\\yourname\\Sangala.")
d.step("Move the entire Sangala Studio folder into it. Documents, settings and saved designs "
       "travel with the folder, so nothing is lost.")
d.step("Run Update SangalaStudio.cmd from its new location.")
d.body("The updater refreshes the Desktop shortcut on every run, including a run that finds "
       "nothing new to download, so the icon follows the folder to its new home without further "
       "attention.")
d.body("This is the recommended course in a school. It requires no administrator, no security "
       "setting is altered, and the protection stays fully in force for every other folder.")

d.heading("Adjusting Windows Security When the Folder Cannot Move")
d.body("Where the folder must stay where it is, Windows can be told that this particular program "
       "is permitted to write to protected folders. The permission is granted to one program, not "
       "to the folder, so everything else remains protected.", before_list=True)
d.new_list()
d.step("Open Windows Security, then Virus & threat protection, then Manage ransomware protection.")
d.step("Choose Allow an app through Controlled folder access.")
d.step("Choose Add an allowed app, then Browse all apps.")
d.step("Select SangalaStudio.exe in the Sangala Studio folder.")
d.body("Note that this step requires an administrator on most managed machines, and that the "
       "updater is a script rather than a program, so on some configurations the entry that has to "
       "be allowed is the Windows command processor rather than Sangala Studio itself. That is a "
       "much broader permission than it appears, and it is the reason the previous section is "
       "preferred wherever the folder can simply be moved.")
d.body("An exclusion, under Virus & threat protection settings, removes a folder from scanning "
       "altogether. It will also resolve the failure, and it is the least advisable of the three "
       "remedies: it turns protection off for that folder permanently, for every program, and it "
       "requires an administrator.")

d.heading("Two Warnings That Are Not This Failure")
d.body("Both are commonly reported alongside it and neither stops the updater.", before_list=True)
d.item("Windows protected your PC. ",
       "A blue panel shown the first time an unsigned program is run. Choose More info, then Run "
       "anyway. It appears once for a given file.")
d.item("A downloaded archive that behaves strangely. ",
       "A .zip fetched from the web carries a mark identifying it as having come from the "
       "internet, and that mark is copied to everything extracted from it. Right-click the .zip "
       "file, choose Properties, select Unblock at the foot of the General tab, and choose Apply "
       "before extracting. Doing this after extraction is too late; the archive has to be "
       "unblocked first.", after=100)

d.heading("What to Report If the Update Still Fails")
d.body("Three pieces of information identify the cause without further guesswork:", before_list=True)
d.new_list()
d.step("The exact wording on screen. A different message is a different problem, and the wording "
       "distinguishes them.")
d.step("Whether a text document could be created in the Sangala Studio folder.")
d.step("Whether Controlled folder access reads On or Off, and the full path of the folder that "
       "holds SangalaStudio.exe.")
d.body("A useful additional test is to paste the address below into a browser. If the browser "
       "downloads a file, the network and the repository are both working and the cause is on the "
       "machine; if it shows a warning or a block page, the wording of that page identifies what "
       "is intercepting the file.")
d.code("https://raw.githubusercontent.com/GlenBull/SangalaStudio/main/SangalaStudio.exe")

print(d.save(DRAFTS, "Updating Sangala Studio Through Windows Security"))
