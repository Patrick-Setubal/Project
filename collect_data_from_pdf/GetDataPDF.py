# Imports
print("Running GetDataPDF")

import fitz
import pandas as pd
import os
import time

# Variables
folders = "./PDFs"
pdf_adress = []
itens = {
    #        X, Y, Comprimento
    "CNPJ": (365, 220, 120),
    "Chave": (355, 125, 220),
    "Nome": (6, 220, 350),
    "DataEmissao": (500, 220, 80),
    "Endereco": (6, 240, 260),
    "Bairro": (280, 240, 118),
    "CEP": (410, 240, 80),
    "DataSaida": (500, 240, 80),
    "Municipio": (6, 260, 260),
    "UF": (280, 260, 15),
    "Fone": (305, 260, 80),
    "PesoLiquido": (490, 380, 97),
}

# Get all the files with '.pdf'
for root, dirs, files in os.walk(folders):
    for filename in files:
        if ".pdf" in filename:
            pdf_adress.append(folders + "/" + filename)

# Number of Pdf's
print(f"Found {len(pdf_adress)} PDFs")

# Create Dataframe
df = pd.DataFrame(columns=itens.keys())

# Open Each PDF and Read
for i, file in enumerate(pdf_adress):
    # Init Doc
    doc = fitz.open(file)
    page = doc[0]

    # For Items Create Rec and Collect Data
    for item in itens:
        # Create Rect
        rect = fitz.Rect(
            itens[item][0],
            itens[item][1],
            itens[item][0] + itens[item][2],
            itens[item][1],
        )
        # Draw Rect
        page.draw_rect(rect, width=1.5, color=(1, 0, 0))
        # Collect Text
        text = page.get_textbox(rect).strip()
        df.loc[i, item] = text


doc.save("View Collected data.pdf")
df.to_excel("data.xlsx", index=False)


print("✅ Data collected from the PDF successfully ✅")
time.sleep(5)
