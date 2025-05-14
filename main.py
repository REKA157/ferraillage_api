from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import base64
from fpdf import FPDF
import ezdxf
import io
import os

app = FastAPI()

@app.post("/generate")
async def generate_pdf(request: Request):
    data = await request.json()
    length = float(data.get("length", 0.4))
    width = float(data.get("width", 0.4))
    longitudinal = data["Armatures"].get("Longitudinales", "H12")
    transversal = data["Armatures"].get("Transversales", "H8")
    espacement = data["Armatures"].get("Espacement", "20cm")

    # Création du PDF
    pdf = FPDF()
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
    pdf.output(file_path)

    with open(file_path, "rb") as f:
        encoded_pdf = base64.b64encode(f.read()).decode("utf-8")

    return JSONResponse(content={
        "report_pdf": f"data:application/pdf;base64,{encoded_pdf}"
    })