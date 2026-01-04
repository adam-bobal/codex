import os
import pandas as pd
from pathlib import Path

# Import parsing libraries
import pdfplumber
import tabula
from PyPDF2 import PdfReader

def parse_with_pdfplumber(pdf_path, output_excel_path):
    """
    Extracts all table rows and saves them to Excel, ignoring headers
    to prevent errors from duplicate column names.
    """
    try:
        all_rows = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        # Collect all rows from all tables, ignoring headers
                        all_rows.extend(table)
        
        if all_rows:
            # Create a single DataFrame from all collected rows
            df = pd.DataFrame(all_rows)
            # Save to Excel without trying to write a header row
            df.to_excel(output_excel_path, index=False, header=False)
            print(f"  - pdfplumber: Saved {len(df)} rows to {output_excel_path.name}")
        else:
            print("  - pdfplumber: No tables found.")
    except Exception as e:
        print(f"  - pdfplumber: FAILED with error: {e}")
        
        if __name__ == '__main__':
    # 1. DEFINE YOUR FOLDERS
    input_dir = Path(r"C:/Users/aboba/projects/bookkeeping/slice/reports")
    main_output_dir = Path("comparison_output")
    main_output_dir.mkdir(exist_ok=True)

    print(f"Searching for PDF files in: {input_dir}/n")
    
    # 2. LOOP THROUGH ALL PDFS
    for pdf_path in input_dir.glob('*.pdf'):
        print(f"Processing '{pdf_path.name}'...")
        
        # Create a dedicated output folder for this PDF
        pdf_output_dir = main_output_dir / pdf_path.stem
        pdf_output_dir.mkdir(exist_ok=True)

        # --- pdfplumber ---
        pdfplumber_out = pdf_output_dir / "output_pdfplumber.xlsx"
        parse_with_pdfplumber(pdf_path, pdfplumber_out)
        

        print("-" * 40)
        
#############
L = r"C:/users/aboba/projects/bookkeeping/slice/reports"
OUTPUT_DIR = r'C:/users/aboba/projects/bookkeeping/slice/parsedreports'
EXCEL_WORKBOOK = r'btpg_finances.xlsx'

for pdf in INPUT_DIR.glob('*.pdf'):
    df = pd.read_excel("{pdf}", )