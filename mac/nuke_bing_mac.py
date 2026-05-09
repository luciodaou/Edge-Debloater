import os
import sqlite3
import shutil
import time

def nuke_bing_from_edge():
    # 1. Locate the Web Data database
    home_dir = os.path.expanduser("~")
    db_path = os.path.join(home_dir, "Library", "Application Support", "Microsoft Edge", "Default", "Web Data")

    if not os.path.exists(db_path):
        print(f"[-] Error: Could not find Edge Web Data file at:\n{db_path}")
        return

    print(f"[+] Found Edge database: {db_path}")

    # 2. Create a safety backup before touching anything
    backup_path = f"{db_path}.backup_{int(time.time())}"
    try:
        shutil.copy2(db_path, backup_path)
        print(f"[+] Backup successfully created at: {backup_path}")
    except PermissionError:
        print("[-] PERMISSION DENIED: Microsoft Edge might be currently running.")
        print("[-] Please completely quit Edge (Cmd+Q) and try again.")
        return

    # 3. Connect to the database and delete Bing
    try:
        # We use a slight timeout in case the file is momentarily locked
        conn = sqlite3.connect(db_path, timeout=3.0)
        cursor = conn.cursor()

        # Check how many Bing entries exist
        cursor.execute("SELECT COUNT(*) FROM keywords WHERE url LIKE '%bing.com%' OR keyword LIKE '%bing%'")
        count = cursor.fetchone()[0]

        if count == 0:
            print("[!] No Bing search engines found in the database. It might already be deleted.")
        else:
            # Execute the deletion
            cursor.execute("DELETE FROM keywords WHERE url LIKE '%bing.com%' OR keyword LIKE '%bing%'")
            conn.commit()
            print(f"[+] Success! Deleted {count} Bing-related entry/entries from the Edge database.")

    except sqlite3.OperationalError as e:
        if "locked" in str(e).lower():
            print("[-] DATABASE LOCKED: Microsoft Edge is still running in the background.")
            print("[-] Please completely quit Edge (Cmd+Q) or kill the 'Microsoft Edge' process, then rerun this script.")
        else:
            print(f"[-] SQLite Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("--- Edge Bing Removal Tool (macOS) ---")
    nuke_bing_from_edge()
    print("--------------------------------------")
