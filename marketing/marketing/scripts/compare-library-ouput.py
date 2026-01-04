import os
import pandas as pd
from pathlib import Path

# Import parsing libraries
import pdfplumber
import tabula
from PyPDF2 import PdfReader

def parse_with_pypdf2(pdf_path, output_txt_path):
    """Extracts raw text using PyPDF2."""
    try:
        text = ""
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text() + "/n" + "-"*20 + "/n"
        
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"  - PyPDF2: Saved raw text to {output_txt_path.name}")
    except Exception as e:
        print(f"  - PyPDF2: FAILED with error: {e}")

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

def parse_with_tabula(pdf_path, output_excel_path):
    """Extracts tables using tabula-py."""
    try:
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        if tables:
            combined_df = pd.concat(tables, ignore_index=True)
            combined_df.to_excel(output_excel_path, index=False)
            print(f"  - Tabula: Saved {len(combined_df)} rows to {output_excel_path.name}")
        else:
            print("  - Tabula: No tables found.")
    except Exception as e:
        print(f"  - Tabula: FAILED with error: {e}")


if __name__ == '__main__':
    # 1. DEFINE YOUR FOLDERS
    input_dir = Path(r"C:/Users/aboba/projects/bookkeeping/attachments")
    main_output_dir = Path("comparison_output")
    main_output_dir.mkdir(exist_ok=True)

    print(f"Searching for PDF files in: {input_dir}/n")
    
    # 2. LOOP THROUGH ALL PDFS
    for pdf_path in input_dir.glob('*.pdf'):
        print(f"Processing '{pdf_path.name}'...")
        
        # Create a dedicated output folder for this PDF
        pdf_output_dir = main_output_dir / pdf_path.stem
        pdf_output_dir.mkdir(exist_ok=True)
        
        # 3. RUN EACH LIBRARY
        # --- PyPDF2 ---
        pypdf2_out = pdf_output_dir / "output_pypdf2.txt"
        parse_with_pypdf2(pdf_path, pypdf2_out)
        
        # --- pdfplumber ---
        pdfplumber_out = pdf_output_dir / "output_pdfplumber.xlsx"
        parse_with_pdfplumber(pdf_path, pdfplumber_out)
        
        # --- Tabula ---
        tabula_out = pdf_output_dir / "output_tabula.xlsx"
        parse_with_tabula(pdf_path, tabula_out)
        
        print("-" * 40)