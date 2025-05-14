from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from fpdf import FPDF
import os

app = FastAPI()

@app.post("/generate")
async def generate_pdf(request: Request):
    try:
        data = await request.json()
        length = float(data.get("length", 0.3))  # en mètres
        width = float(data.get("width", 0.3))
        height = float(data.get("height", 3.0))
        armatures = data.get("Armatures", {})
        longi = armatures.get("Longitudinales", "4x16mm")
        transv = armatures.get("Transversales", "phi6mm à 15cm")
        esp = armatures.get("Espacement", "15cm")

        def clean(text):
            return (
                text.replace("⌀", "phi")
                    .replace("@", " à ")
                    .replace("ø", "phi")
                    .encode("ascii", "ignore")
                    .decode("ascii")
            )

        longi = clean(longi)
        transv = clean(transv)
        esp = clean(esp)

        img_path = "/tmp/plan.png"
        pdf_path = "/tmp/ferraillage_visible.pdf"

        # === Génération du schéma ===
        fig, ax = plt.subplots(figsize=(9, 13))
        ax.set_xlim(-0.5, max(length, width) + 4)
        ax.set_ylim(-0.5, height + width + 3)
        ax.set_aspect('equal')
        ax.axis('off')

        bar_radius = 0.02
        line_thick = 2

        # --- Vue en Plan ---
        ax.text(length / 2 - 0.2, -0.2, "Vue en Plan", fontsize=12, weight='bold')
        ax.plot([0, length, length, 0, 0], [0, 0, width, width, 0], color="black", linewidth=line_thick)

        for x in [0.05, length - 0.05]:
            for y in [0.05, width - 0.05]:
                ax.add_patch(plt.Circle((x, y), bar_radius, color='darkred'))

        ax.annotate(f"{length:.2f} m", xy=(length / 2 - 0.15, width + 0.05), fontsize=10)
        ax.annotate(f"{width:.2f} m", xy=(length + 0.05, width / 2 - 0.05), fontsize=10, rotation=90)

        ax.annotate("A", xy=(-0.2, width / 2), fontsize=12, weight='bold')
        ax.annotate("A", xy=(length + 0.1, width / 2), fontsize=12, weight='bold')
        ax.annotate("⟵", xy=(-0.25, width / 2), fontsize=14)
        ax.annotate("⟶", xy=(length + 0.05, width / 2), fontsize=14)

        # --- Coupe A-A ---
        y0 = width + 0.5
        ax.text(length / 2 - 0.2, y0 + height + 0.2, "Coupe A-A", fontsize=12, weight='bold')

        ax.plot([0, 0], [y0, y0 + height], 'black', linewidth=line_thick)
        ax.plot([length, length], [y0, y0 + height], 'black', linewidth=line_thick)
        ax.plot([0, length], [y0, y0], 'black', linewidth=line_thick)
        ax.plot([0, length], [y0 + height, y0 + height], 'black', linewidth=line_thick)  # <-- Correction ici

        ax.annotate(f"{height:.2f} m", xy=(length + 0.05, y0 + height / 2 - 0.05), fontsize=10, rotation=90)

        for i in range(int(height / 0.15)):
            y = y0 + i * 0.15
            ax.plot([0.05, length - 0.05], [y, y], 'blue', linestyle='--', linewidth=0.7)

        ax.add_patch(plt.Circle((0.05, y0 + 0.05), bar_radius, color='darkred'))
        ax.add_patch(plt.Circle((length - 0.05, y0 + 0.05), bar_radius, color='darkred'))
        ax.add_patch(plt.Circle((0.05, y0 + height - 0.05), bar_radius, color='darkred'))
        ax.add_patch(plt.Circle((length - 0.05, y0 + height - 0.05), bar_radius, color='darkred'))

        # --- Légende graphique ---
        legend_y = y0 + height + 0.7
        ax.text(0, legend_y, "LÉGENDE :", fontsize=12, weight="bold")
        ax.plot([0.1, 0.5], [legend_y - 0.1, legend_y - 0.1], color='black', linewidth=2)
        ax.text(0.6, legend_y - 0.15, "Contour béton", fontsize=10)
        ax.add_patch(plt.Circle((0.3, legend_y - 0.4), bar_radius, color='darkred'))
        ax.text(0.6, legend_y - 0.45, "Armature longitudinale", fontsize=10)
        ax.plot([0.1, 0.5], [legend_y - 0.7, legend_y - 0.7], 'blue', linestyle='--', linewidth=1)
        ax.text(0.6, legend_y - 0.75, "Étriers (transversaux)", fontsize=10)

        # --- Cartouche ---
        cart_x = length + 0.5
        cart_y = -0.5
        ax.add_patch(Rectangle((cart_x, cart_y), 3.5, 2.5, fill=False, edgecolor='black', linewidth=1))
        ax.text(cart_x + 0.1, cart_y + 2.2, "BE.ON - Rapport Ferraillage", fontsize=10, weight='bold')
        ax.text(cart_x + 0.1, cart_y + 1.8, f"L : {length} m")
        ax.text(cart_x + 0.1, cart_y + 1.5, f"l : {width} m")
        ax.text(cart_x + 0.1, cart_y + 1.2, f"H : {height} m")
        ax.text(cart_x + 0.1, cart_y + 0.9, f"Longitudinales : {longi}")
        ax.text(cart_x + 0.1, cart_y + 0.6, f"Transversales : {transv}")
        ax.text(cart_x + 0.1, cart_y + 0.3, f"Espacement : {esp}")

        plt.savefig(img_path, dpi=150)
        plt.close()

        if not os.path.exists(img_path):
            return JSONResponse(status_code=500, content={"error": "plan.png non généré"})

        # === PDF final ===
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(200, 10, txt="Rapport de Ferraillage BE.ON", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Dimensions : {length}m x {width}m x {height}m", ln=True)
        pdf.cell(200, 10, txt=f"Armatures Longitudinales : {longi}", ln=True)
        pdf.cell(200, 10, txt=f"Armatures Transversales : {transv}", ln=True)
        pdf.cell(200, 10, txt=f"Espacement : {esp}", ln=True)
        pdf.ln(10)
        pdf.image(img_path, x=5, w=200)
        pdf.output(pdf_path)

        return FileResponse(pdf_path, media_type="application/pdf", filename="rapport_ferraillage.pdf")

    except Exception as e:
        import traceback
        return JSONResponse(status_code=500, content={"error": str(e), "trace": traceback.format_exc()})
