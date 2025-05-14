from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

app = FastAPI()

@app.post("/generate")
async def generate(request: Request):
    try:
        data = await request.json()

        length = float(data.get("length", 0.4))
        width = float(data.get("width", 0.4))
        armatures = data.get("Armatures", {})
        longi = armatures.get("Longitudinales", "4x12mm")
        transv = armatures.get("Transversales", "⌀6mm @20cm")
        esp = armatures.get("Espacement", "20cm")

        # Nettoyer tous les caractères illégaux
        def clean(text):
            return (
                text.replace("⌀", "phi")
                    .replace("ø", "phi")
                    .replace("@", " à ")
                    .encode("ascii", "ignore")
                    .decode("ascii")
            )

        longi = clean(longi)
        transv = clean(transv)
        esp = clean(esp)

        img_path = "/tmp/plan.png"
        pdf_path = "/tmp/rapport.pdf"

        # PLAN EN IMAGE
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.set_title("Plan de Ferraillage (vue de dessus)", fontsize=10)
        ax.set_xlim(0, length)
        ax.set_ylim(0, width)

        ax.plot([0.05, length - 0.05], [0.05, 0.05], 'ko')
        ax.plot([0.05, length - 0.05], [width - 0.05, width - 0.05], 'ko')
        ax.plot([0.05, length - 0.05, length - 0.05, 0.05, 0.05],
                [0.05, 0.05, width - 0.05, width - 0.05, 0.05], 'r--')
        ax.axis('off')
        plt.savefig(img_path, bbox_inches='tight')
        plt.close()

        # PDF
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

        return FileResponse(pdf_path, media_type='application/pdf', filename="ferraillage.pdf")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
