from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from fpdf import FPDF
import os

app = FastAPI()

def clean(text):
    return (
        text.replace("⌀", "phi")
            .replace("@", " à ")
            .replace("ø", "phi")
            .encode("ascii", "ignore")
            .decode("ascii")
    )

def draw_forme(code, ax, x, y, w=0.4, h=0.2):
    if code == "00":
        ax.plot([x, x + w], [y + h / 2, y + h / 2], 'k-', lw=2)
    elif code == "31":
        ax.plot([x, x, x + w, x + w], [y, y + h, y + h, y], 'k-', lw=2)
    else:
        ax.text(x, y + h / 2, code, fontsize=8)
@app.post("/generate")
async def generate_pdf(request: Request):
    try:
        data = await request.json()
        length = float(data.get("length", 0.3))
        width = float(data.get("width", 0.3))
        height = float(data.get("height", 3.0))
        armatures = data.get("Armatures", {})
        longi = clean(armatures.get("Longitudinales", "4x16mm"))
        transv = clean(armatures.get("Transversales", "phi6mm à 15cm"))
        esp = clean(armatures.get("Espacement", "15cm"))

        img_path = "/tmp/plan.png"
        pdf_path = "/tmp/ferraillage_visible.pdf"

        fig, ax = plt.subplots(figsize=(11.7, 8.3))  # A4 horizontal
        ax.set_xlim(-0.5, 8)
        ax.set_ylim(-0.5, 6)
        ax.axis('off')

        bar_radius = 0.03
        plan_x, plan_y = 0.5, 3.5
        sec_x, sec_y = 0.5, 1.0

        # Vue en plan
        ax.text(plan_x + length / 2, plan_y + width + 0.2, "Vue en Plan", fontsize=12, weight="bold")
        ax.plot([plan_x, plan_x + length, plan_x + length, plan_x, plan_x],
                [plan_y, plan_y, plan_y + width, plan_y + width, plan_y], 'k-', lw=2)

        ax.add_patch(plt.Circle((plan_x + 0.05, plan_y + 0.05), bar_radius, color="darkred"))
        ax.add_patch(plt.Circle((plan_x + length - 0.05, plan_y + width - 0.05), bar_radius, color="darkred"))

        # Coupe A-A
        ax.text(sec_x + length / 2, sec_y + height + 0.3, "Coupe A-A", fontsize=12, weight="bold")
        ax.plot([sec_x, sec_x + length, sec_x + length, sec_x, sec_x],
                [sec_y, sec_y, sec_y + height, sec_y + height, sec_y], 'k-', lw=2)

        for i in range(int(height / 0.15)):
            y = sec_y + i * 0.15
            ax.plot([sec_x + 0.05, sec_x + length - 0.05], [y, y], 'b--', lw=0.6)

        ax.add_patch(plt.Circle((sec_x + 0.05, sec_y + 0.05), bar_radius, color="darkred"))
        ax.add_patch(plt.Circle((sec_x + length - 0.05, sec_y + height - 0.05), bar_radius, color="darkred"))

        # Repères armatures
        ax.text(plan_x + length / 2, plan_y + width / 2, "①", fontsize=14, color='black')
        ax.text(sec_x + length / 2, sec_y + height / 2, "②", fontsize=14, color='black')
        # Nomenclature
        table_x = 5.5
        table_y = 3.8
        row_h = 0.4
        col_w = [0.4, 1.5, 0.6, 1.0, 0.6]

        headers = ["Pos", "Désignation", "Forme", "Code", "Quantité"]
        values = [
            ["①", "4 x ⌀16", "00", "L=3.00m", "4"],
            ["②", "Etriers ⌀6 / 15cm", "31", "H=3.00m", f"{int(height / 0.15)}"]
        ]

        for i, label in enumerate(headers):
            ax.add_patch(Rectangle((table_x + sum(col_w[:i]), table_y), col_w[i], row_h, fill=False))
            ax.text(table_x + sum(col_w[:i]) + 0.05, table_y + row_h / 2 - 0.1, label, fontsize=8, weight='bold')

        for row, val in enumerate(values):
            for i, v in enumerate(val):
                x = table_x + sum(col_w[:i])
                y = table_y - (row + 1) * row_h
                ax.add_patch(Rectangle((x, y), col_w[i], row_h, fill=False))
                if i == 2:
                    draw_forme(v, ax, x + 0.05, y + 0.1, w=0.5, h=0.2)
                else:
                    ax.text(x + 0.05, y + row_h / 2 - 0.1, v, fontsize=8)

        # Légende graphique
        leg_x, leg_y = 5.5, 1.5
        ax.text(leg_x, leg_y + 0.9, "LÉGENDE", fontsize=10, weight="bold")
        ax.plot([leg_x, leg_x + 0.4], [leg_y + 0.7, leg_y + 0.7], 'k-', lw=2)
        ax.text(leg_x + 0.5, leg_y + 0.65, "Béton (contour)", fontsize=8)
        ax.add_patch(plt.Circle((leg_x + 0.2, leg_y + 0.45), 0.03, color="darkred"))
        ax.text(leg_x + 0.5, leg_y + 0.4, "Armature longitudinale", fontsize=8)
        ax.plot([leg_x, leg_x + 0.4], [leg_y + 0.2, leg_y + 0.2], 'b--', lw=1)
        ax.text(leg_x + 0.5, leg_y + 0.15, "Etriers / cadres", fontsize=8)

        # Cartouche
        cart_x, cart_y = 0.5, 0.1
        ax.text(cart_x, cart_y + 0.5, "Projet : BE.ON", fontsize=10)
        ax.text(cart_x + 2.5, cart_y + 0.5, f"Dimensions : {length:.2f} x {width:.2f} x {height:.2f} m", fontsize=10)
        ax.text(cart_x, cart_y + 0.2, f"Armatures : {longi} / {transv}", fontsize=10)

        # Sauvegarde image
        plt.savefig(img_path, dpi=150)
        plt.close()

        # Génération PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(200, 10, txt="Rapport de Ferraillage - BE.ON", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.ln(5)
        pdf.image(img_path, x=5, w=200)
        pdf.output(pdf_path)

        return FileResponse(pdf_path, media_type="application/pdf", filename="rapport_ferraillage.pdf")

    except Exception as e:
        import traceback
        return JSONResponse(status_code=500, content={"error": str(e), "trace": traceback.format_exc()})
