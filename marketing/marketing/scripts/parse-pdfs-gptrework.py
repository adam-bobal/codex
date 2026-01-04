import os, sys
from pathlib import Path
import pandas as pd
import pdfplumber
import tabula  # ⇢ pip install tabula‑py
from PyPDF2 import PdfReader

# ---------- 1. HELPER PARSERS ----------
def parse_pypdf2(src: Path, out_txt: Path) -> None:
    text = ""
    for page in PdfReader(src).pages:
        text += (page.extract_text() or "") + "\n" + "-" * 20 + "\n"
    out_txt.write_text(text, encoding="utf‑8")
    print(f"  ✓ PyPDF2  → {out_txt.name}")

def parse_pdfplumber(src: Path, out_xlsx: Path) -> bool:
    """Return True if tables were saved, else False (so we know to fall back on Tabula)."""
    rows = []
    with pdfplumber.open(src) as pdf:
        for p in pdf.pages:
            for tbl in p.extract_tables():
                if tbl:
                    rows.extend(tbl)
    if rows:
        pd.DataFrame(rows).to_excel(out_xlsx, index=False, header=False)
        print(f"  ✓ pdfplumber ({len(rows)} rows) → {out_xlsx.name}")
        return True
    print("  • pdfplumber found no tables")
    return False

def parse_tabula(src: Path, out_xlsx: Path) -> None:
    # Try lattice first (works when grid lines exist), then stream
    for mode in ({"lattice": True}, {"stream": True}):
        try:
            dfs = tabula.read_pdf(str(src), pages="all", multiple_tables=True, **mode)
            if dfs:
                pd.concat(dfs, ignore_index=True).to_excel(out_xlsx, index=False)
                print(f"  ✓ Tabula ({len(dfs)} tbls) → {out_xlsx.name}")
                return
        except Exception as e:
            print(f"    Tabula {mode} failed: {e}")
    print("  ✗ Tabula found no tables")

# ---------- 2. MAIN ----------
PDFS = [
    "close-summary-list-big-time-pie-guys-2025-06-06.pdf",
    "close-summary-list-big-time-pie-guys-2025-06-07.pdf",
    "liabilities-big-time-pie-guys-2025-06-06.pdf",
    "liabilities-big-time-pie-guys-2025-06-07.pdf",
    "pmix-big-time-pie-guys-2025-06-12.pdf",
    "pmix-big-time-pie-guys-2025-06-14.pdf",
    "sales-labor-by-hour-big-time-pie-guys-2025-06-12.pdf",
    "sales-labor-by-hour-big-time-pie-guys-2025-06-13.pdf",
    "weekly-sales-big-time-pie-guys-2025-06-08.pdf",
    "weekly-sales-big-time-pie-guys-2025-06-09.pdf",
]

BASE_DIR   = Path(r"C:\Users\aboba\projects\bookkeeping\attachments")
OUT_PARENT = BASE_DIR / "comparison_output"
OUT_PARENT.mkdir(exist_ok=True)

for pdf_name in PDFS:
    pdf_path = BASE_DIR / pdf_name
    if not pdf_path.exists():
        print(f"⚠️  {pdf_name} not found, skipping")
        continue

    print(f"\nParsing {pdf_name}")
    out_dir = OUT_PARENT / pdf_path.stem
    out_dir.mkdir(exist_ok=True)

    parse_pypdf2(pdf_path, out_dir / "raw.txt")
    got_tables = parse_pdfplumber(pdf_path, out_dir / "plumber.xlsx")
    if not got_tables:
        parse_tabula(pdf_path, out_dir / "tabula.xlsx")
