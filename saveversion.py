"""
Version Snapshot
================
Run this before making any changes to your agent.
It saves a timestamped copy so you can always roll back.

Usage:
    python save_version.py "v1 - basic greedy"
    python save_version.py "v2 - added production priority"
    python save_version.py   (no message = uses timestamp only)
"""

import shutil
import os
import sys
from datetime import datetime

AGENT_FILE   = os.path.join(os.path.dirname(__file__), "agent", "main.py")
VERSIONS_DIR = os.path.join(os.path.dirname(__file__), "versions")

os.makedirs(VERSIONS_DIR, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M")
label     = sys.argv[1] if len(sys.argv) > 1 else ""
safe_label = label.replace(" ", "_").replace("/", "-")[:40]
filename  = f"{timestamp}_{safe_label}.py" if safe_label else f"{timestamp}.py"
dest      = os.path.join(VERSIONS_DIR, filename)

shutil.copy2(AGENT_FILE, dest)
print(f"Saved → versions/{filename}")

# List all versions
print("\nAll saved versions:")
for f in sorted(os.listdir(VERSIONS_DIR)):
    size = os.path.getsize(os.path.join(VERSIONS_DIR, f))
    print(f"  {f}  ({size} bytes)")