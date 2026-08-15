"""Notarizing the Mac version of Sangala Studio - for Jo (account) and Moses (Mac)."""
import sys
sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
from makedocx import Doc

OUT = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\Sangala Tools\Other Platforms\Mac"

d = Doc()
d.title("Notarizing Sangala Studio for macOS")

d.body("Notarization is Apple's check on software distributed outside the App Store. A developer submits a "
       "signed package, Apple scans it and returns a ticket, and the ticket is attached to the package so "
       "macOS accepts it without warning the person who installs it. The work divides cleanly: Jo holds the "
       "Apple Developer account and does everything inside it, and Moses does everything that happens on a "
       "Mac. Neither part can be done from Windows.")

# ---------------------------------------------------------------- what it buys
d.heading("Why This Is Needed Now")
d.body("macOS marks a file as quarantined according to how it arrived. A file downloaded through a web "
       "browser carries that mark and is checked; the same file arriving through the Dropbox application "
       "does not and is not. This is why Moses met no warning at all when he tested the Mac kit on "
       "14 August 2026: Dropbox delivered it.")
d.body("Distribution is moving to the Educational CAD Model Library, at cadlibrary.org/objects/V3LXPYQH "
       "(Glen, 2026-08-14). Every download from that page comes through a browser, so every download is "
       "quarantined, and an unsigned program is refused with a message its reader cannot act on. What was "
       "a later question is now the current one.")
d.body("Two consequences follow that are easy to miss.", before_list=True)
d.item("The Deposit Holds Zip Files. ",
       "The library serves a zip, and a quarantined zip yields quarantined files when it is unpacked. So the "
       "notarized thing has to be inside it: the zip contains a signed installer package, the reader unpacks "
       "the zip and double-clicks the package. A stapled ticket survives being zipped, so this works, but it "
       "does mean the Mac kit stops being a folder of files and becomes a package.")
d.item("Windows Does Not Have This Problem. ",
       "Tested by Glen on 2026-08-14: the zip downloads onto Windows without a security alert. The question "
       "raised here is a macOS one, and the Windows route needs nothing done to it.")

# ---------------------------------------------------------------- the obstacle
d.heading("What Is Being Built")
d.body("A seventh-grade student has to be able to start the program by clicking an icon on the Desktop "
       "(Glen, 2026-08-14). That requirement decides the shape of the package rather than any question of "
       "convenience, because a shell script cannot be a Desktop application on macOS. Finder will run a "
       ".command file with no typing, which is how the kit works today, but it is a document rather than an "
       "application: it cannot sit in the Dock, and it always opens a Terminal window. So the package "
       "installs an application, and creates the Desktop icon itself.")
d.body("Three parts, and the division between them is what allows a notarized application to coexist with "
       "an updater that rewrites files.", before_list=True)
d.item("The Application, in /Applications. ",
       "Sangala Studio.app, signed and notarized, and never written to again. Its executable is a two-line "
       "script that runs the Python bridge, so the application IS that process: the Dock shows it while "
       "Studio is open, and right-click then Quit stops it, which replaces pressing Control-C in a Terminal "
       "window. The student never meets a command line, and neither does the teacher once the installation "
       "is done. The icon is the buffalo, converted from Sangala.ico, so the Mac Desktop matches the "
       "Windows one.")
d.item("The Working Folder, in the User's Own Documents. ",
       "The page, the assets, the bridge itself, and the student's projects. This is what the updater "
       "rewrites, and nothing in it is signed, so rewriting it cannot invalidate a signature. Installing "
       "everything into /Applications instead would not work: the updater writes to that folder, and the "
       "schools have no administrator password.")
d.item("A Postinstall Script. ",
       "Part of the package. It puts the alias on the Desktop - the job Create Desktop Shortcut.cmd does on "
       "Windows. One caution for whoever writes it: a postinstall script runs as root, so it must find the "
       "logged-in user before writing to a Desktop rather than trusting $HOME.")
d.body("The alternative considered and rejected was an application bundle alone, with the page and assets "
       "inside it. A signed bundle whose contents the updater rewrites no longer matches its own signature, "
       "and macOS then refuses to run it. Splitting the parts as above is what avoids that.")

d.heading("Submit It Twice, on Purpose")
d.body("This plan adds three things to the signing step that a package of plain files does not have: a "
       "second certificate, the hardened runtime and timestamp flags, and a complete Info.plist. Each is a "
       "common reason a first submission is rejected, and each is diagnosable from the notary log in "
       "minutes. The content is still only scripts and data, with no compiled code for Apple's scanner to "
       "object to.")
d.body("The larger uncertainty is not whether Apple accepts the package but whether the program still runs "
       "under the hardened runtime, which restricts what a process may load - and the bridge loads a USB "
       "library Apple did not sign. The reasoning says this is safe, because the bundle's executable hands "
       "off to Apple's own python3 and the running process then carries Apple's signature rather than this "
       "project's. That is reasoning rather than evidence, and it is the point in the plan least worth "
       "being wrong about after the package has shipped.")
d.body("So separate the two questions with one extra submission, which costs minutes and no money.",
       before_list=True)
d.step("Submit a package of the plain files first - no application bundle, no Developer ID Application "
       "certificate, no hardened runtime. It proves the certificate, the stored credentials, the submission "
       "and the stapling all work, and it should pass without argument.")
d.step("Then submit the real package, with the application in it. If that one is rejected, the log points "
       "at the one thing that changed rather than at any of five.")
d.body("Both use the commands below. The first simply has less in its payload and skips the codesign line.")

# ---------------------------------------------------------------- division
d.heading("Who Does What")
d.table(
    "Table 1. The Division of Work",
    ["Step", "Who", "Where"],
    [
        ["Generate a certificate signing request", "Moses", "Keychain Access on his Mac"],
        ["Create the Developer ID certificates", "Jo", "developer.apple.com, in his account"],
        ["Create an app-specific password or an API key", "Jo", "appleid.apple.com or App Store Connect"],
        ["Install the certificate and store the credentials", "Moses", "his Mac, once"],
        ["Build and sign the package", "Moses", "his Mac, on each release"],
        ["Submit for notarization and staple the ticket", "Moses", "his Mac, on each release"],
        ["Confirm the result", "Moses, then a second Mac", "any Mac that has never seen the file"],
    ],
    weights=[46, 18, 36])

d.body("The certificate is the one place the two must coordinate, and it is where time is usually lost. The "
       "private key belongs to the Mac that will do the signing, so it must never travel. The order is: "
       "Moses creates the request, Jo turns it into a certificate, Moses installs the certificate.")

# ---------------------------------------------------------------- Jo's part
d.heading("Jo's Part, in the Developer Account")
d.step("Confirm the membership is active and that the current Program License Agreement has been accepted. "
       "An unaccepted agreement is the most common reason a first submission is rejected, and it says so in "
       "wording that does not obviously mean that.")
d.step("Note the Team ID — a ten-character code shown under Membership. Moses needs it in every command.")
d.step("When Moses sends a file ending in .certSigningRequest, go to Certificates, Identifiers & Profiles, "
       "choose Certificates, add a new one, and select Developer ID Installer. Upload his request, download "
       "the resulting .cer file, and send it back to him. Only the Account Holder can create a Developer ID "
       "certificate, which is why this step is Jo's and not Moses's.")
d.step("Create the credential Moses will submit with. The simpler option is an app-specific password, made "
       "at appleid.apple.com under Sign-In and Security; the tidier option for a team is an App Store "
       "Connect API key, made under Users and Access, Integrations, which can be handed over without "
       "sharing an Apple ID. Either way Moses also needs the Apple ID the account belongs to.")

# ---------------------------------------------------------------- Moses's part
d.heading("Moses's Part, on the Mac")
d.body("Once, at the start. Xcode's command line tools supply every command below; installing them is a "
       "single line, and macOS may offer to do it by itself the first time one is used.", before_list=True)
d.listing("xcode-select --install")
d.body("Create the certificate request in Keychain Access: from its menu, Certificate Assistant, then "
       "Request a Certificate From a Certificate Authority. Enter the account's email address, choose Saved "
       "to disk, and send the resulting .certSigningRequest to Jo. When his .cer file comes back, "
       "double-click it to install it. Confirm it is there:", before_list=True)
d.listing("security find-identity -v -p codesigning")
d.body("Store the notarization credentials once, so that no password appears in any later command. The "
       "profile name is arbitrary; SangalaNotary is used throughout this document.", before_list=True)
d.listing('xcrun notarytool store-credentials "SangalaNotary" \\\n'
          '    --apple-id "jo@example.com" \\\n'
          '    --team-id  "ABCDE12345" \\\n'
          '    --password "abcd-efgh-ijkl-mnop"')

d.body("On each release, four commands. The first builds an unsigned package from a folder holding exactly "
       "what the kit contains today; the second signs it; the third submits it and waits for the answer; "
       "the fourth attaches the ticket so the package validates on a Mac with no internet connection.",
       before_list=True)
CMDS = r'''codesign --force --options runtime --timestamp \
         --sign "Developer ID Application: NAME (ABCDE12345)" \
         "payload/Applications/Sangala Studio.app"

pkgbuild --root "payload" --scripts "scripts" \
         --identifier "org.sangala.studio" --version "2026.08.14" \
         --install-location "/" "SangalaStudio-unsigned.pkg"

productsign --sign "Developer ID Installer: NAME (ABCDE12345)" \
            "SangalaStudio-unsigned.pkg" "SangalaStudio.pkg"

xcrun notarytool submit "SangalaStudio.pkg" \
      --keychain-profile "SangalaNotary" --wait

xcrun stapler staple "SangalaStudio.pkg"'''
d.listing(CMDS)

d.body("The submission usually answers within a few minutes. If it comes back Invalid, the reason is in the "
       "log, which is fetched with the submission identifier the command printed:", before_list=True)
d.listing('xcrun notarytool log <submission-id> --keychain-profile "SangalaNotary"')

# ---------------------------------------------------------------- verifying
d.heading("Confirming It Worked")
d.body("Two checks on Moses's own Mac, then one that matters more than either.", before_list=True)
d.listing('xcrun stapler validate "SangalaStudio.pkg"\n'
          'spctl --assess --type install -vvv "SangalaStudio.pkg"')
d.body("The check that matters is a Mac that has never seen the file, reached the way a real user will "
       "reach it: put the package on a web page or in a GitHub release, download it through a browser so "
       "that it is quarantined, and install it. A file copied by Dropbox or a memory stick is not "
       "quarantined and therefore proves nothing about notarization.")

# ---------------------------------------------------------------- unknowns
d.heading("What Is Not Yet Known")
d.body("Three things this document cannot settle in advance, all of which the first submission will "
       "answer.", before_list=True)
d.step("Whether a package containing only scripts, a Python file and a web page notarizes without "
       "complaint. There is no compiled code in it for Apple's scanner to object to, so it should pass, but "
       "no one has submitted one from this project.")
d.step("Exactly which folder in the user's Documents the working files go to, and whether the postinstall "
       "script creates it or the application creates it the first time it runs. The division itself is "
       "settled - application in /Applications, working files in the user's own Documents - because the "
       "updater has to be able to write to them and the schools have no administrator password. What is "
       "not settled is the folder's name and who makes it, which matters on a shared computer where several "
       "students log in.")
d.step("Whether the Python libraries the bridge installs on first run interact with any of this. They are "
       "installed by the user into their own account and are not part of the package, so they should not, "
       "but it is worth watching on the first clean Mac.")

d.body("The last of those is the same open question that De'Quan's Mac will answer about the first run "
       "generally, and it would be sensible to settle that before packaging anything.")

print(d.save(OUT, "Notarizing Sangala Studio for macOS"))
