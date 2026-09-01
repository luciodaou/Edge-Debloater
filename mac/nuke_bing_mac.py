"""Remove the Bing search engine from every Microsoft Edge profile on macOS.

Backs up each profile's "Web Data" SQLite database (SQLite online backup API,
consistent even while Edge runs), then deletes the Bing entries.

Exit code: 0 on success, 1 on failure.
"""

import os
import sys

# Make the repository-root library importable regardless of the current
# working directory (e.g. when double-clicked from Finder).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nuke_bing_lib  # noqa: E402

LOCK_HINT = (
    "DATABASE LOCKED: Microsoft Edge is still running in the background.",
    "Please completely quit Edge (Cmd+Q) or kill the 'Microsoft Edge' process, then rerun this script.",
)


def nuke_bing_from_edge():
    # 1. Locate every Edge profile database
    user_data_dir = os.path.join(
        os.path.expanduser("~"), "Library", "Application Support", "Microsoft Edge"
    )
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
        ok, deleted = nuke_bing_lib.nuke_profile(db_path, LOCK_HINT, LOCK_HINT)
        total_deleted += deleted
        if not ok:
            failures += 1

    summary = f"[+] Summary: {len(db_paths)} profile(s) processed, {total_deleted} Bing entry/entries deleted"
    if failures:
        summary += f", {failures} profile(s) failed"
    print(summary + ".")
    return failures == 0


if __name__ == "__main__":
    print("--- Edge Bing Removal Tool (macOS) ---")
    success = nuke_bing_from_edge()
    print("--------------------------------------")
    sys.exit(0 if success else 1)
