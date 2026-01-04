import subprocess
import os
from concurrent.futures import ThreadPoolExecutor

# 1️⃣ Get mounted drives (excluding C:) via PowerShell
ps_command = r'''
Get-PSDrive -PSProvider FileSystem |
  Where-Object { $_.Name -ne 'C' -and Test-Path $_.Root } |
  Select-Object -ExpandProperty Root
'''
get_vids = r'''
    get-childitem . -recurse -include "*.mp4", "*.wmv", "*.mpeg", "*.wmv", "*.flv", "*.avi", "*.mov" |
        Select-Object -property name |
        sort-object -property name
}
'''
result = subprocess.run(
    ["powershell", "-NoProfile", "-Command", ps_command],
    capture_output=True,
    text=True
)
drives = [d.strip() for d in result.stdout.splitlines() if d.strip()]

print("Drives to scan:", drives)

def getvideos(drives):
    for d in drives:
        subprocess.run(["powershell", "-noprofile, "-command", get_vids], capture_output=True, text=True)
        
# 2️⃣ Load your OneDrive filenames
#    (Assumes one filename per line in 'onedrive_files.txt')
with open("onedrive_files.txt", "r", encoding="utf-8") as f:
    onedrive_files = {line.strip() for line in f if line.strip()}

print(f"Total OneDrive files to verify: {len(onedrive_files)}")


# 3️⃣ Define per-drive scanner
def scan_drive(drive_root):
    """Return the set of onedrive_files found under this drive."""
    found = set()
    for root, _, files in os.walk(drive_root):
        for fname in files:
            if fname in onedrive_files:
                found.add(fname)
    return found

# 4️⃣ Run scans in parallel
found_files = set()
with ThreadPoolExecutor(max_workers=min(len(drives), 8)) as pool:
    for drive_matches in pool.map(scan_drive, drives):
        found_files.update(drive_matches)

# 5️⃣ Compare and report
missing = sorted(onedrive_files - found_files)
present = sorted(onedrive_files & found_files)

print(f"\n✔ Present on local drives ({len(present)}):")
for fname in present:
    print(" ", fname)

print(f"\n❌ Missing from local drives ({len(missing)}):")
for fname in missing:
    print(" ", fname)
