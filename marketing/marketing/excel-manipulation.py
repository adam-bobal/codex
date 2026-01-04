import pandas as pd
import openpyxl

files = {
    "C:\Users\aboba\Downloads\online-order-report-from-04-01-2025-04-00-to-05-01-2025-03-59.csv",
    "C:\Users\aboba\Downloads\online-order-report-from-03-01-2025-05-00-to-04-01-2025-03-59.csv",
    "C:\Users\aboba\Downloads\online-order-report-from-02-01-2025-05-00-to-03-01-2025-04-59.csv",
    "C:\Users\aboba\Downloads\online-order-report-from-01-01-2025-05-00-to-02-01-2025-04-59.csv",
    "C:\Users\aboba\Downloads\online-order-report-from-05-01-2025-04-00-to-06-01-2025-03-59.csv",
}

df = pd.read_excel("C:\\Users\\aboba\\Downloads\\online-order-report-from-04-01-2025-04-00-to-05-01-2025-03-59.csv", engine="openpyxl")
``` :contentReference[oaicite:1]{index=1} <programming language><command><process>





