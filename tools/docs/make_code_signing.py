"""Builds "Securing a Code-Signing Certificate for Windows 11" in _Drafts.

Asked for by Glen on 2026-09-15 after the updater's Windows Security failures: "We're going to need
to do this."

EVERY FACT IN THIS DOCUMENT WAS READ FROM THE SOURCE ON 2026-09-15, not from memory, because the
landscape changed twice since the model's training and the old advice is now actively wrong:

  * Microsoft, "SmartScreen reputation for Windows app developers" (learn.microsoft.com, page dated
    2026-05-04): "EV certificates no longer bypass SmartScreen ... Paying a premium for EV solely to
    avoid SmartScreen warnings is no longer justified." Also the table of certificate types and
    first-download behavior, and "When a file is not signed, SmartScreen reputation must build for
    each new version of your files, starting with zero reputation."
  * Microsoft, "What is Artifact Signing?" - the service was renamed from Trusted Signing to Azure
    Artifact Signing; FIPS 140-3 Level 3.
  * Microsoft, "Artifact Signing FAQ" - no EV certificates ever; paid Azure subscription required
    (no free, trial or sponsored); certificates are never released to the holder; identity
    validation expires; SmartScreen reputation still builds by download history.
  * Microsoft Q&A on Artifact Signing eligibility - US and Canada organizations with three or more
    years of verifiable operating history.
  * InCommon / Sectigo, and Indiana University's IT pages - higher-education members may already
    have code signing included; InCommon requires a hardware token, and since 23 February 2026 the
    CA/Browser Forum caps code-signing certificates at 459 days with a token shipped yearly.

The repository counts in the document were measured here: git log over SangalaStudio.html gives 358
commits, over SangalaStudio.exe gives 8, the last on 2026-08-02. The engine carries no version
resource (0.0.0.0) and Get-AuthenticodeSignature reports NotSigned.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from makedocx import Doc

DRAFTS = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts")

d = Doc()
d.title("Securing a Code-Signing Certificate for Windows 11")

d.body("Sangala Studio is distributed as an unsigned program. Windows 11 treats an unsigned program "
       "with suspicion at three separate points \u2014 SmartScreen warns before it runs, Smart App "
       "Control blocks it outright where that feature is switched on, and a script that downloads one "
       "is a pattern security software is built to interrupt. Signing the program addresses all "
       "three, but not in the way it is commonly described, and the difference decides which "
       "certificate is worth buying. This note sets out what signing actually achieves, the three "
       "routes to a certificate, and the order in which they should be examined.")

d.heading("What Signing Does, and What It Does Not Do")
d.body("The common belief is that a signed program stops the warning. It does not. Microsoft's own "
       "guidance for application developers states that a newly created binary can still show a "
       "SmartScreen warning even when signed, until its hash or its publisher certificate has "
       "accumulated evidence of good reputation. What signing changes is where that reputation "
       "lives.", before_list=True)
d.item("Reputation becomes cumulative. ",
       "An unsigned file starts from zero reputation with every new version, and reputation cannot "
       "carry across from earlier versions. A signed file builds reputation against the publisher "
       "certificate, so each release inherits what the ones before it earned.")
d.item("The publisher is named. ",
       "Where a warning does appear, a signed program shows the verified organization rather than "
       "\u201cUnknown publisher,\u201d which is the difference between a teacher proceeding and a "
       "teacher stopping.")
d.item("Smart App Control stops blocking. ",
       "That feature blocks unsigned files outright rather than warning about them, and it applies "
       "to every executable, not only downloaded ones. Signing is the only remedy.", after=100)
d.body([("One widely repeated instruction is now wrong. ", True, False),
        ("An Extended Validation certificate used to "
        "confer immediate SmartScreen reputation, and much advice still says so. Microsoft's current "
        "documentation states plainly that this behavior no longer exists, and that paying a premium "
        "for Extended Validation solely to avoid SmartScreen warnings is no longer justified. An "
        "Extended Validation certificate costs several times an ordinary one and, for this purpose, "
        "now buys nothing.", False, False)])

d.heading("Why This Matters for a Program That Releases Often")
d.body("The arithmetic is what makes the case. In this project's history the browser page has been "
       "changed by 358 commits and the engine by 8, the last of them on 2 August 2026. Because the "
       "engine is unsigned, every one of those releases begins at zero reputation and can never "
       "accumulate any. A signed engine would have been building reputation continuously since the "
       "first release, and by now the warning would in all likelihood have stopped appearing.")
d.body("This is also why signing is worth more here than its price suggests. The cost is not "
       "measured against one release; it is measured against every release from now on, and against "
       "the teachers and students who meet a warning at each one.")

d.heading("The Three Routes")
d.table(
    "Table 1. Routes to a Signed Program, and What Each Costs",
    ["Route", "Cost", "What It Requires", "First-Download Warning"],
    [["Microsoft Store", "No certificate fee",
      "Packaging the program for the Store and passing review",
      "None. Store applications are re-signed by Microsoft and are never subject to a warning"],
     ["Azure Artifact Signing", "From $9.99 a month",
      "A paid Azure subscription and organization identity validation",
      "Warning until reputation accumulates; publisher name shown"],
     ["University certificate through InCommon", "Possibly none",
      "Membership, a hardware token, and renewal each year",
      "Warning until reputation accumulates; publisher name shown"]],
    weights=[22, 16, 30, 32])

d.heading("The Route to Examine First")
d.body("Before any certificate is purchased, the University's own provision should be checked. "
       "InCommon, the higher-education identity and certificate consortium, includes code-signing "
       "certificates in its certificate service, and at some member institutions these are issued to "
       "departments at no charge. If the University of Virginia's Information Technology Services "
       "already subscribes, the certificate may cost nothing and the identity validation is already "
       "done, because the institution is the subscriber.", before_list=True)
d.body("Two complications should be raised in the same conversation.", before_list=True)
d.item("A hardware token is mandatory. ",
       "Since June 2023 the private key for any publicly trusted code-signing certificate must live "
       "in certified hardware, and InCommon supports only the hardware route. Somebody must hold "
       "that token, and it must be present whenever a release is signed.")
d.item("The certificate is now short-lived. ",
       "Since 23 February 2026 a code-signing certificate may not exceed 459 days, roughly fifteen "
       "months, and a replacement token is shipped each year. A lapse means unsigned releases, and "
       "unsigned releases start again from zero reputation.", after=100)
d.body("The consortium is also in the middle of a change of certificate authority, from Sectigo to "
       "CertiNext as of 17 July 2026, which is worth confirming rather than assuming.")

d.heading("Azure Artifact Signing, in Detail")
d.body("Microsoft's own service, until recently called Trusted Signing, is the route that fits an "
       "automated release best, because it holds the key rather than handing anyone a token. Signing "
       "then happens wherever the release is built \u2014 including in a GitHub Action, so that every "
       "release is signed without anyone remembering to do it.", before_list=True)
d.item("Cost. ", "From $9.99 a month for the Basic tier, which covers several thousand signatures.")
d.item("Eligibility. ",
       "Organizations in the United States and Canada with at least three years of verifiable "
       "operating history. A university satisfies this comfortably; a new company does not.")
d.item("A paid subscription is required. ",
       "Free, trial and sponsored Azure subscriptions are refused. The institution's existing "
       "agreement would have to cover it.")
d.item("No hardware token. ",
       "Keys are held in certified hardware security modules at FIPS 140-3 Level 3, and the "
       "certificate itself is never released to the holder \u2014 it exists only at the moment of "
       "signing.")
d.item("No Extended Validation. ",
       "The service does not issue Extended Validation certificates and has no plan to, which given "
       "the SmartScreen change above costs nothing.")
d.item("Validation expires. ",
       "Identity validation must be renewed or certificate renewal stops and signing stops with it. "
       "Reminders begin sixty days ahead.", after=100)

d.heading("What Changes in the Build")
d.body("Signing is one added step, but it carries conditions that are easy to break.", before_list=True)
d.new_list()
d.step("Every release is signed. A single unsigned release cannot inherit the reputation the signed "
       "ones earned, and starts again from nothing.")
d.step("Nothing is modified after signing. Editing a file after it has been signed breaks the "
       "signature, so signing is the last step before publication.")
d.step("The signature is timestamped, so that files signed today stay valid after the certificate "
       "itself expires.")
d.step("One identity is used throughout. Changing the signing certificate resets the publisher "
       "signal that the reputation is attached to.")

d.heading("What Signing Does Not Fix")
d.body("Two of the failures already seen in the field are untouched by any certificate. A folder "
       "that Windows will not let the updater write to remains unwritable, because that is a "
       "permission question rather than a trust question. And a school network that intercepts "
       "downloaded programs may continue to do so. Signing removes the trust obstacle; the location "
       "advice and the network advice stand alongside it.")
d.body("It is also worth recording that the only route with no warning at all is the Microsoft "
       "Store, because Store applications are re-signed by Microsoft. Packaging for the Store is a "
       "larger undertaking than buying a certificate, but it is the only option that ends the "
       "question rather than improving it.")

d.heading("The Sequence to Follow")
d.new_list()
d.step("Ask Information Technology Services whether the University subscribes to the InCommon "
       "Certificate Service and whether code-signing certificates are available to departments, at "
       "what cost, and who would hold the hardware token.")
d.step("In the same enquiry, ask whether a paid Azure subscription exists that could carry an "
       "Artifact Signing account, since that decides whether the Microsoft route is open.")
d.step("Choose between the two on one question: whether a person must be present with a token at "
       "each release, or whether signing should happen automatically wherever the release is built.")
d.step("Complete organization identity validation. This is an institutional step requiring someone "
       "authorized to represent the University, and it cannot be hurried.")
d.step("Add the signing step to the build, sign one release, and confirm on a clean machine that "
       "the publisher name appears where \u201cUnknown publisher\u201d appeared before.")
d.body("Only the last of these is technical work, and it is the smallest part. The first four are "
       "institutional, which is the reason to begin them early rather than when the need becomes "
       "urgent.")

print(d.save(DRAFTS, "Securing a Code-Signing Certificate for Windows 11"))
