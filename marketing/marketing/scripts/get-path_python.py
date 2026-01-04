from pathlib import Path

# filelist.txt has one full path per line
with open("filelist.txt") as f:
    for line in f:
        p = Path(line.strip())
        print(f"{p} | {'FOUND' if p.exists() else 'MISSING'}")

root = Path("E:/")                         # folder to search
index = {f.name: f for f in root.rglob("*") if f.is_file()}
for name in Path("names.txt").read_text().splitlines():
    print(index.get(name, f"MISSING: {name}"))
