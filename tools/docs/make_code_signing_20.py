"""Rebuilds "Securing a Code-Signing Certificate for Windows 11" as Ver 2.0 - the PROCESS only.

Glen, 2026-09-15, on Ver 1.0: "i don't want a general purpose document; i want a separate document
that focuses on the signing process. don't mix in all that other junk that is not relevant in this
document. stay focused on this one thing."

So Ver 2.0 is the procedure and nothing else. Removed wholesale: SmartScreen reputation theory, the
Microsoft Store, the three-route comparison table, the Extended Validation discussion (reduced to one
sentence where it bears on what to order), the release-count measurement, and "what signing does not
fix". Ver 1.0 is archived and still holds all of that if the strategy case is ever wanted separately.

This is a NEW document rather than an edit of Glen's file, which the in-place rule would normally
require - but Ver 1.0 is mine from three hours ago, he has not annotated it, and the change is a
wholesale change of scope rather than a revision.

EVERY COMMAND AND REQUIREMENT VERIFIED FROM MICROSOFT'S OWN DOCUMENTATION ON 2026-09-15:
  * "Set up signing integrations to use Artifact Signing" - the winget package id, the four
    prerequisites and the SignTool minimum version 10.0.2261.755 (20348 NOT supported), the
    metadata.json shape, the region endpoint table and the 403 it causes when mismatched, the exact
    signing command line, the three-day certificate validity and the timestamp URL.
  * "SignTool" (Win32 reference) - /fd /tr /td /a /n /f, verify /pa /v, and the exit codes. Note that
    /t and /tr cannot be used together, and that /fd and /td are now errors when omitted.
  * "Artifact Signing FAQ" - identity validation expires with reminders from 60 days; paid Azure
    subscription required.
  * InCommon / Sectigo - hardware token only; since 2026-02-23 certificates capped at 459 days with a
    replacement token shipped yearly.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from makedocx import Doc

DRAFTS = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts")

d = Doc()
d.title("Securing a Code-Signing Certificate for Windows 11")

d.body("This note sets out the procedure for obtaining a code-signing certificate and using it to "
       "sign a Windows program. It covers what must be assembled before applying, how the "
       "application and validation proceed, how the signing tools are installed and configured, the "
       "commands that sign and verify a file, and what renewal requires.")

d.heading("What Must Be Assembled Before Applying")
d.body("A code-signing certificate is issued to a legal entity, not to a person, and the validation "
       "that precedes it checks the entity against independent records. Assembling the following "
       "first avoids the most common cause of delay, which is a request returned for more "
       "information.", before_list=True)
d.item("The legal name, exactly as registered. ",
       "A trading name, an abbreviation or a departmental name will not validate. The certificate "
       "will carry this name and it cannot be customized afterward.")
d.item("The registered address. ",
       "As it appears in the public record, not a campus mailing address.")
d.item("A telephone number in a public directory. ",
       "Validation includes a call placed to a number the validator can find independently.")
d.item("A business registration record or D-U-N-S number. ",
       "This is the third-party source the entity is checked against.")
d.item("Three or more years of verifiable operating history. ",
       "Microsoft's service requires this of organizations, and an entity younger than that is "
       "declined. A long-established institution satisfies it without effort.")
d.item("A named person authorized to represent the entity, ",
       "reachable at an address that accepts external mail containing links. A distribution list "
       "will not work, and a filtered mailbox is a frequent cause of failure.", after=100)

d.heading("Deciding Where the Private Key Will Live")
d.body("Since June 2023 the private key for a publicly trusted code-signing certificate must be held "
       "in certified hardware. A key file that can be copied is no longer issued, so there is no "
       ".pfx to store and no password to share. Two arrangements satisfy the requirement, and the "
       "choice must be made before ordering because everything after it differs.", before_list=True)
d.item("A hardware token. ",
       "A physical device is shipped, and it must be present in the machine whenever a release is "
       "signed. This is the only arrangement a certificate authority such as InCommon supports.")
d.item("A managed signing service. ",
       "The key is held in the provider's hardware security modules and is never released. Signing "
       "is a request to the service, so it can run wherever the program is built, including in an "
       "automated build with no person present.", after=100)
d.body("An Extended Validation certificate is not required for either arrangement and should not be "
       "ordered by default; it costs several times an ordinary certificate and confers no advantage "
       "for this purpose.")

d.heading("Applying and Completing Validation")
d.new_list()
d.step("Place the order with the chosen provider, supplying the details assembled above.")
d.step("Watch for the verification message sent to the named address. The link in it expires after "
       "seven days, and a missed link cannot be resent \u2014 the request must be started again.")
d.step("Answer the verification call when it is placed.")
d.step("Supply any further documents the validator requests. The number of attempts is limited, and "
       "an exhausted request cannot be continued.")
d.body("Validation cannot be expedited, and submitting a second request for the same entity while "
       "the first is in progress does not help. A managed service additionally requires a paid "
       "subscription; free, trial and sponsored accounts are refused.")

d.heading("Installing the Signing Tools")
d.body("Signing on Windows is done by SignTool, from the Windows SDK. A managed service needs three "
       "further components: the .NET 8 runtime, the Microsoft Visual C++ Redistributable, and the "
       "provider's client library. For Microsoft's service all four install together:", before_list=True)
d.code("winget install -e --id Microsoft.Azure.ArtifactSigningClientTools")
d.body("Installing requires an administrator, which on a managed machine means raising a request "
       "rather than doing it directly. Two version constraints are easy to miss and produce errors "
       "that do not name their cause: SignTool must be version 10.0.2261.755 or later, and the "
       "SDK numbered 20348 is not supported.")

d.heading("Configuring the Account File")
d.body("A managed service is told which account and certificate to use through a small JSON file "
       "beside the build, conventionally named metadata.json:", before_list=True)
d.listing('{\n'
          '  "Endpoint": "https://eus.codesigning.azure.net",\n'
          '  "CodeSigningAccountName": "<the signing account name>",\n'
          '  "CertificateProfileName": "<the certificate profile name>"\n'
          '}')
d.body("The endpoint must match the region in which the account and the certificate profile were "
       "created. A mismatch is the usual cause of a 403 error during signing, and the error does not "
       "mention the region. The example above is the East United States endpoint; each region has "
       "its own.")
d.body("A certificate on a hardware token needs no such file. It is selected by its subject name or "
       "by letting SignTool choose automatically.")

d.heading("Signing a File")
d.body("With a managed service, giving SignTool the client library and the account file:", before_list=True)
d.code('signtool.exe sign /v /fd SHA256 /tr "http://timestamp.acs.microsoft.com" /td SHA256 '
       '/dlib "<dlib path>\\x64\\Azure.CodeSigning.Dlib.dll" /dmdf "<path>\\metadata.json" SangalaStudio.exe')
d.body("With a certificate on a token, naming the certificate instead:", before_list=True)
d.code('signtool.exe sign /v /fd SHA256 /tr "<timestamp URL>" /td SHA256 '
       '/n "<certificate subject name>" SangalaStudio.exe')
d.body("The digest options are no longer optional. SignTool now raises an error when /fd is omitted "
       "while signing or /td while time stamping. Use SHA256 for both. The x86 and x64 builds of "
       "SignTool both ship in the SDK, and the client library must match the one being used.")

d.heading("Why Time Stamping Is Not Optional")
d.body("A certificate issued by a managed service is valid for three days. Without a time stamp, "
       "every signature would stop validating almost immediately. A time stamp records when the "
       "signature was made, so the file remains valid long after the certificate expires. The /tr "
       "option names an RFC 3161 time stamp server and cannot be combined with the older /t option.")

d.heading("Verifying the Result")
d.body("Confirm the signature on the file that will actually be distributed, not on the build "
       "output before it was copied:", before_list=True)
d.code("signtool.exe verify /pa /v SangalaStudio.exe")
d.body("The /pa option applies the default authentication policy; without it SignTool applies the "
       "driver policy and can report a correctly signed program as invalid. SignTool returns 0 on "
       "success, 1 on failure, and 2 when it completes with warnings. The publisher name that "
       "appears here is what a user will see in place of \u201cUnknown publisher\u201d.")

d.heading("Renewal, and What Happens If It Lapses")
d.body("Neither the certificate nor the validation behind it is permanent.", before_list=True)
d.item("Identity validation expires. ",
       "When it does, certificate renewal stops and signing stops with it. Reminders begin sixty "
       "days ahead; a lapsed validation must be created again from the beginning.")
d.item("The certificate itself is short-lived. ",
       "Since 23 February 2026 a code-signing certificate may not exceed 459 days, roughly fifteen "
       "months, and on the token arrangement a replacement device is shipped each year.")
d.item("A lapse is not neutral. ",
       "Releases issued while the certificate is expired are unsigned, and an unsigned release "
       "cannot inherit anything the signed ones established. Renewal dates belong in a calendar, "
       "held by more than one person.", after=100)

d.heading("Where Signing Belongs in the Build")
d.new_list()
d.step("Sign as the last step before publication. Editing a file after it has been signed breaks "
       "the signature.")
d.step("Sign every release without exception.")
d.step("Sign with the same identity each time. Changing the certificate discards the standing the "
       "previous one had.")
d.step("Verify after signing, and before the file is copied anywhere.")

# Ver 2.0 explicitly: Ver 1.0 has been archived, so the folder scan would hand back 1.0 again.
print(d.save(DRAFTS, "Securing a Code-Signing Certificate for Windows 11", version="2.0"))
