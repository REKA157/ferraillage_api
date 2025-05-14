from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

app = FastAPI()

@app.post("/generate")
async def generate(request: Request):
    data = await request.json()

    # Récupération des données
    length = float(data.get("length", 0.4))
    width = float(data.get("width", 0.4))
    armatures = data.get("Armatures", {})
    longi = armatures.get("Longitudinales", "4x12mm")
    transv = armatures.get("Transversales", "⌀6mm @20cm")
    esp = armatures.get("Espacement", "20cm")

    # Fichier temporaire image
    img_path = "/tmp/plan.png"
    pdf_path = "/tmp/rapport.pdf"

    # 🔧 1. GÉNÉRATION DU PLAN AVEC MATPLOTLIB
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_title("Plan de Ferraillage (vue de dessus)", fontsize=10)
    ax.set_xlim(0, length)
    ax.set_ylim(0, width)

    # Barres longitudinales (cercles aux coins)
    ax.plot([0.05, length-0.05], [0.05, 0.05], 'ko', label='Longitudinales')
    ax.plot([0.05, length-0.05], [width-0.05, width-0.05], 'ko')

    # Cadre (étrier)
    ax.plot([0.05, length-0.05, length-0.05, 0.05, 0.05],
            [0.05, 0.05, width-0.05, width-0.05, 0.05], 'r--', label='Transversales')

    ax.legend(loc='lower right')
    ax.axis('off')
    plt.savefig(img_path, bbox_inches='tight')
    plt.close()

    # 🔧 2. GÉNÉRATION DU PDF AVEC L’IMAGE INTÉGRÉE
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="Rapport de Ferraillage BE.ON", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Longueur : {length} m", ln=True)
    pdf.cell(200, 10, txt=f"Largeur : {width} m", ln=True)
    pdf.cell(200, 10, txt=f"Armatures Longitudinales : {longi}", ln=True)
    pdf.cell(200, 10, txt=f"Armatures Transversales : {transv}", ln=True)
    pdf.cell(200, 10, txt=f"Espacement : {esp}", ln=True)
    pdf.ln(10)
    pdf.image(img_path, x=10, w=180)

    pdf.output(pdf_path)

    # 🔁 3. RETOUR DU FICHIER PDF DIRECTEMENT
    return FileResponse(pdf_path, media_type='application/pdf', filename="ferraillage.pdf")
