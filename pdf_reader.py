from PyPDF2 import PdfReader
import pandas as pd
from datetime import datetime
import re

def read_pdf(pdf_path):
    invoice_date = get_date(pdf_path)
    details = get_details(pdf_path)
    return invoice_date, details


def get_date(path):
    pdf = PdfReader(path)
    text = pdf.pages[0].extract_text()

    # Extract only the invoice section that contains the date
    start, end = "Fecha emisión factura", "Periodo de facturación"
    text_section = text[text.find(start):text.find(end)]

    # Clean text before regex search
    cleaned_text = text_section.replace(" ", "").replace("\n", "")

    # Pattern for dd/mm/yyyy
    pattern = r"\b\d{1,2}/\d{1,2}/\d{4}\b"
    match = re.search(pattern, cleaned_text)

    return datetime.strptime(match.group(), "%d/%m/%Y").date()


def get_details(path):
    pdf = PdfReader(path)
    text = pdf.pages[1].extract_text()

    # Extract only the section we need
    start, end = "DETALLE DE LA FACTURA", "Incluido en el"
    text_section = text[text.find(start):text.find(end)]

    # Normalize text
    cleaned_text = (
        text_section.replace(".", "")
                    .replace(" €", "")
                    .replace(",", ".")
    )
    lines = [line for line in cleaned_text.split("\n") if line]

    # Separate into two lists (items and costs)
    items = [line for i, line in enumerate(lines) if i % 2 == 1]
    costs = [line for i, line in enumerate(lines) if i % 2 == 0 and i > 0]

    # Create DataFrame
    df = pd.DataFrame({
        "Item": items,
        "Cost": pd.to_numeric(costs, errors="coerce")
    })

    return df


def save_to_csv(df):
    output_file = f"salida_endesa.csv"
    df.to_csv(output_file, index=False)
