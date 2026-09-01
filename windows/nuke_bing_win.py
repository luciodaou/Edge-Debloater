"""Remove the Bing search engine from every Microsoft Edge profile on Windows.

Backs up each profile's "Web Data" SQLite database (SQLite online backup API,
consistent even while Edge runs), then deletes the Bing entries.

Exit code: 0 on success, 1 on failure.
"""

import os
import sys

# Make the repository-root library importable regardless of the current
# working directory (e.g. when double-clicked from Explorer).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nuke_bing_lib  # noqa: E402

LOCK_HINT_BACKUP = (
    "DATABASE LOCKED: Microsoft Edge is currently running.",
    "Please close Edge completely (check Task Manager for 'msedge.exe') and try again.",
)
LOCK_HINT_DELETE = (
    "DATABASE LOCKED: Microsoft Edge is still running in the background.",
    "Open Task Manager, end all 'msedge.exe' processes, and rerun this script.",
)


def nuke_bing_from_edge():
    # 1. Locate every Edge profile database
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        print("[-] Error: LOCALAPPDATA environment variable not found.")
        return False

    user_data_dir = os.path.join(local_app_data, r"Microsoft\Edge\User Data")
    db_paths = nuke_bing_lib.find_web_data_files(user_data_dir)
    if not db_paths:
        print(f"[-] Error: Could not find any Edge profile database under:\n{user_data_dir}")
        return False

    # 2. Back up + clean each profile
    failures = 0
    total_deleted = 0
    for db_path in db_paths:
        profile = os.path.basename(os.path.dirname(db_path))
        print(f"[+] Processing profile: {profile}")
        ok, deleted = nuke_bing_lib.nuke_profile(db_path, LOCK_HINT_BACKUP, LOCK_HINT_DELETE)
        total_deleted += deleted
        if not ok:
            failures += 1

    summary = f"[+] Summary: {len(db_paths)} profile(s) processed, {total_deleted} Bing entry/entries deleted"
    if failures:
        summary += f", {failures} profile(s) failed"
    print(summary + ".")
    return failures == 0


if __name__ == "__main__":
    print("--- Edge Bing Removal Tool ---")
    success = nuke_bing_from_edge()
    print("------------------------------")
    input("Press Enter to exit...")
    sys.exit(0 if success else 1)
