"""Shared logic for the Edge Bing-removal scripts (mac/ and windows/).

Both wrapper scripts import this module, so keep it in the repository root.
Uses only the Python standard library (3.7+).
"""

import os
import sqlite3
import time

# Matches Bing search-engine rows in Edge's `keywords` table.
BING_CONDITION = "url LIKE '%bing.com%' OR keyword LIKE '%bing%'"
# Seconds to wait on a SQLite lock before giving up.
SQLITE_TIMEOUT = 3.0
# Profile directory names that hold a real user profile.
PROFILE_NAMES = ("Default",)
PROFILE_PREFIX = "Profile "


def is_locked_error(error):
    """True when a sqlite3.Error looks like file locking by a running Edge."""
    message = str(error).lower()
    return "locked" in message or "unable to open" in message


def report_sqlite_error(error, locked_hint_lines):
    """Print a user-facing message for a sqlite3.Error.

    locked_hint_lines: lines shown when the failure looks like a lock.
    """
    if is_locked_error(error):
        for line in locked_hint_lines:
            print(f"[-] {line}")
    else:
        print(f"[-] SQLite Error: {error}")


def find_web_data_files(user_data_dir):
    """Return the Web Data path of every Edge profile under user_data_dir.

    Covers the default profile plus every numbered one (Profile 1, 2, ...).
    """
    if not os.path.isdir(user_data_dir):
        return []
    paths = []
    for name in sorted(os.listdir(user_data_dir)):
        if name not in PROFILE_NAMES and not name.startswith(PROFILE_PREFIX):
            continue
        candidate = os.path.join(user_data_dir, name, "Web Data")
        if os.path.isfile(candidate):
            paths.append(candidate)
    return paths


def back_up_database(db_path):
    """Snapshot db_path to a timestamped file via SQLite's online backup API.

    Unlike a byte-wise file copy this yields a consistent database even if
    another process holds the file open. Raises sqlite3.Error on failure; a
    partially created backup is removed.
    """
    backup_path = f"{db_path}.backup_{int(time.time())}"
    source = sqlite3.connect(db_path, timeout=SQLITE_TIMEOUT)
    target = None
    try:
        target = sqlite3.connect(backup_path)
        source.backup(target)
    except Exception:
        if os.path.exists(backup_path):
            os.unlink(backup_path)
        raise
    finally:
        if target is not None:
            target.close()
        source.close()
    return backup_path


def remove_bing_entries(db_path):
    """Delete Bing rows from the keywords table; returns the deleted count.

    Raises sqlite3.Error on failure.
    """
    conn = sqlite3.connect(db_path, timeout=SQLITE_TIMEOUT)
    try:
        count = conn.execute(
            f"SELECT COUNT(*) FROM keywords WHERE {BING_CONDITION}"
        ).fetchone()[0]
        if count:
            conn.execute(f"DELETE FROM keywords WHERE {BING_CONDITION}")
            conn.commit()
        return count
    finally:
        conn.close()


def nuke_profile(db_path, backup_lock_hint, delete_lock_hint):
    """Back up one profile's Web Data, then delete its Bing entries.

    Returns (ok, deleted_count). Prints progress with [+]/[!]/[-] markers.
    """
    try:
        backup_path = back_up_database(db_path)
    except sqlite3.Error as e:
        report_sqlite_error(e, backup_lock_hint)
        return False, 0
    print(f"[+] Backup successfully created at: {backup_path}")

    try:
        count = remove_bing_entries(db_path)
    except sqlite3.Error as e:
        report_sqlite_error(e, delete_lock_hint)
        return False, 0

    if count == 0:
        print("[!] No Bing search engines found in the database. It might already be deleted.")
    else:
        print(f"[+] Success! Deleted {count} Bing-related entry/entries from the Edge database.")
    return True, count
