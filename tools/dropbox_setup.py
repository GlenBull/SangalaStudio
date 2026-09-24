"""One-time setup: connect GitHub's release workflow to the Dropbox Sangala Tools folder.

Run it once, on any computer, by someone whose Dropbox account can open the Sangala Tools folder:

    python -m pip install dropbox
    python dropbox_setup.py

It asks for the App key and App secret of a Dropbox app (created at
https://dropbox.com/developers/apps with "Full Dropbox" access and the permissions files.metadata.read,
files.content.read, files.content.write and account_info.read), opens a Dropbox sign-in page, and
prints the four values to store in GitHub. Before printing them it checks that the Sangala Tools path
it was given really is a folder the token can see, so a mistyped path is caught here and not on the
first release.
"""
import sys

import dropbox
from dropbox import common, files

SCOPES = ["files.metadata.read", "files.content.read", "files.content.write", "account_info.read"]

key = input("Dropbox App key: ").strip()
secret = input("Dropbox App secret: ").strip()
flow = dropbox.DropboxOAuth2FlowNoRedirect(key, consumer_secret=secret,
                                           token_access_type="offline", scope=SCOPES)
print("\n1. Open this address and sign in to Dropbox:\n   " + flow.start())
print('2. Click "Allow", then copy the code Dropbox shows.')
result = flow.finish(input("Paste the code here: ").strip())

dbx = dropbox.Dropbox(oauth2_refresh_token=result.refresh_token, app_key=key, app_secret=secret)
# The release workflow counts paths from the top of the team's Dropbox; so does this check.
root = dbx.users_get_current_account().root_info.root_namespace_id
dbx = dbx.with_path_root(common.PathRoot.root(root))

print("\nFolders at the top of this Dropbox:")
for e in dbx.files_list_folder("").entries:
    if isinstance(e, files.FolderMetadata):
        print("   /" + e.name)
while True:
    base = input("\nPath of the Sangala Tools folder, from that top level\n"
                 "(for example /AI Sandbox/Design through Making/Sangala Tools): ").strip()
    base = "/" + base.strip("/")
    try:
        names = [e.name for e in dbx.files_list_folder(base).entries]
    except dropbox.exceptions.ApiError:
        print("No folder at " + base + " - try again.")
        continue
    if "Sangala Studio Files" in names:
        break
    print("That folder exists but holds no 'Sangala Studio Files' folder - try again.")

print("\nStore these in GitHub: organization maketolearn > Settings > Secrets and variables > Actions.")
print("Secrets:")
print("   DROPBOX_APP_KEY        " + key)
print("   DROPBOX_APP_SECRET     " + secret)
print("   DROPBOX_REFRESH_TOKEN  " + result.refresh_token)
print("Variable:")
print("   DROPBOX_BASE           " + base)
sys.exit(0)
