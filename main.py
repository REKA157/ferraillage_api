from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

app = FastAPI()

@app.post("/generate")
async def generate_pdf(request: Request):
    try:
        data = await request.json()
        length = float(data.get("length", 0.3))
        width = float(data.get("width", 0.3))
        height = float(data.get("height", 3.0))
        armatures = data.get("Armatures", {})
        longi = armatures.get("Longitudinales", "4x16mm")
        transv = armatures.get("Transversales", "⌀6mm @15cm")
        esp = armatures.get("Espacement", "15cm")

        def clean(text):
            return text.replace("⌀", "phi").replace("@", " à ").replace("ø", "phi").encode("ascii", "ignore").decode("ascii")

        longi = clean(longi)
        transv = clean(transv)
        esp = clean(esp)

        img_path = "/tmp/plan.png"
        pdf_path = "/tmp/ferraillage_visible.pdf"

        # 🖼 Génération de l'image avec cadre de visualisation fixe
        fig, ax = plt.subplots(figsize=(8, 10))
        ax.set_xlim(-0.1, 1)
        ax.set_ylim(-0.1, 4)
        ax.set_aspect('equal')
        ax.axis('off')

        # Vue en plan
        ax.plot([0, length, length, 0, 0], [0, 0, width, width, 0], 'k-', linewidth=2)
        ax.plot([0.03, length-0.03, length-0.03, 0.03, 0.03], [0.03, 0.03, width-0.03, width-0.03, 0.03], 'r--')
        ax.plot([0.03], [0.03], 'ko')
        ax.plot([length-0.03], [0.03], 'ko')
        ax.plot([length-0.03], [width-0.03], 'ko')
        ax.plot([0.03], [width-0.03], 'ko')
        ax.text(length/2 - 0.05, -0.06, "Vue en Plan", fontsize=10, weight="bold")

        # Coupe A-A
        base_x = 0
        base_y = height + 0.1
        ax.plot([base_x, base_x], [base_y, base_y + height], 'k-')
        ax.plot([base_x + length, base_x + length], [base_y, base_y + height], 'k-')
        ax.plot([base_x, base_x + length], [base_y + height, base_y + height], 'k-')
        ax.plot([base_x, base_x + length], [base_y, base_y], 'k-')

        for i in range(int(height / 0.15)):
            y = base_y + i * 0.15
            ax.plot([base_x + 0.03, base_x + length - 0.03], [y, y], 'r--', linewidth=0.5)

        ax.plot([base_x + 0.03, base_x + 0.03], [base_y, base_y + height], 'k-')
        ax.plot([base_x + length - 0.03, base_x + length - 0.03], [base_y, base_y + height], 'k-')
        ax.text(base_x + length/2 - 0.05, base_y + height + 0.1, "Coupe A-A", fontsize=10, weight="bold")

        plt.savefig(img_path, dpi=300)
        plt.close()

        # 📄 Génération du PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(200, 10, txt="Rapport de Ferraillage BE.ON", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Longueur : {length} m", ln=True)
        pdf.cell(200, 10, txt=f"Largeur : {width} m", ln=True)
        pdf.cell(200, 10, txt=f"Hauteur : {height} m", ln=True)
        pdf.cell(200, 10, txt=f"Armatures Longitudinales : {longi}", ln=True)
        pdf.cell(200, 10, txt=f"Armatures Transversales : {transv}", ln=True)
        pdf.cell(200, 10, txt=f"Espacement : {esp}", ln=True)
        pdf.ln(10)
        pdf.image(img_path, x=10, w=190)
        pdf.output(pdf_path)

        return FileResponse(pdf_path, media_type="application/pdf", filename="rapport_ferraillage.pdf")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

