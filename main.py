from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import base64
from fpdf import FPDF
import os

app = FastAPI()

@app.post("/generate")
async def generate_pdf(request: Request):
    data = await request.json()

    length = float(data.get("length", 0.4))
    width = float(data.get("width", 0.4))

    armatures = data.get("Armatures", {})
    longitudinal = armatures.get("Longitudinales", "H12")
    transversal = armatures.get("Transversales", "H8")
    espacement = armatures.get("Espacement", "20cm")

    # Nettoyage caractères spéciaux pour éviter l’erreur latin-1
    def sanitize(text):
        return (
            text.replace("⌀", "phi")
                .replace("ø", "phi")
                .replace("@", " à ")
                .encode("ascii", "ignore")  # supprime tout caractère illégal
                .decode("ascii")
        )

    longitudinal = sanitize(longitudinal)
    transversal = sanitize(transversal)
    espacement = sanitize(espacement)

    # Génération PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="Rapport de Ferraillage BE.ON", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Longueur : {length} m", ln=True)
    pdf.cell(200, 10, txt=f"Largeur : {width} m", ln=True)
    pdf.cell(200, 10, txt=f"Armatures Longitudinales : {longitudinal}", ln=True)
    pdf.cell(200, 10, txt=f"Armatures Transversales : {transversal}", ln=True)
    pdf.cell(200, 10, txt=f"Espacement : {espacement}", ln=True)

    file_path = "/tmp/rapport.pdf"
    try:
        pdf.output(file_path)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Erreur PDF", "details": str(e)}
        )

    # Encoder PDF en base64
    with open(file_path, "rb") as f:
        encoded_pdf = base64.b64encode(f.read()).decode("utf-8")

    return JSONResponse(content={
        "report_pdf": f"data:application/pdf;base64,{encoded_pdf}"
    })
