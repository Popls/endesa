import os
import pandas as pd
from pdf_reader import read_pdf, save_to_csv

invoices_dir = "facturas"

def claim(df):
    # Validate operation: Energy consumed + Compensation = Virtual Battery balance
    consumed_energy = df.loc[df["Item"] == "Energía consumida de la red", "Cost"].iloc[0]
    compensation = df.loc[df["Item"].str.startswith("Compensación excedente"), "Cost"].iloc[0]
    used = df.loc[df["Item"].str.startswith("BATERÍA VIRTUAL"), "Cost"]
    used = used.iloc[0] if not used.empty else 0

    operation = round((consumed_energy + compensation) * -1, 2)

    battery_balance = df.loc[df["Item"] == "Saldo destinado a Batería Virtual", "Cost"]

    if operation > 0:
        if battery_balance.empty:
            print(f"---- RECLAMAR {operation}€ --- No se ha guardado en la Batería Virtual")
        elif battery_balance.iloc[0] != operation:
            print(f"---- RECLAMAR {operation}€ --- Energía consumida + Compensación excedente ≠ Saldo Batería Virtual. Resultado esperado: {operation}")
        return operation + used
    return used

# Collect all files in the invoices directory
files = [
    os.path.join(invoices_dir, f)
    for f in os.listdir(invoices_dir)
    if os.path.isfile(os.path.join(invoices_dir, f))
]

results = []
for file in files:
    date, details = read_pdf(file)
    results.append((date, details, file))

# Sort by date
results.sort(key=lambda x: x[0])

virtual_balance = 0
all_details = []
# Process in order
for date, details, files in results:
    virtual_balance = virtual_balance + claim(details)
    df_copy = details.copy()
    df_copy.insert(0, "Date", date)
    all_details.append(df_copy)

    if virtual_balance > 0:
        print(f"{date} - Saldo esperado de Bateria virtual: {virtual_balance}")
        print("----------------------------------------------------------------------------------------")
save_to_csv(pd.concat(all_details, ignore_index=True))
