from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
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

def draw_forme(code, ax, x, y, w=0.5, h=0.3):
    if code == "00":
        ax.plot([x, x + w], [y + h / 2, y + h / 2], 'k-', lw=2)
    elif code == "31":
        ax.plot([x, x, x + w, x + w, x], [y, y + h, y + h, y, y], 'k-', lw=2)
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

        fig, ax = plt.subplots(figsize=(11.7, 8.3))  # A4 paysage
        ax.set_xlim(-1, 11)
        ax.set_ylim(-1, 9)
        ax.axis('off')

        bar_radius = 0.04
        rep1_color = 'darkred'
        rep2_color = 'blue'
        # === VUE EN PLAN (développement vertical du poteau) ===
        vp_x, vp_y = 1, 1.2
        ax.plot([vp_x, vp_x + length, vp_x + length, vp_x, vp_x],
                [vp_y, vp_y, vp_y + height, vp_y + height, vp_y], 'k-', lw=2)

        for i in range(int(height / 0.15)):
            y = vp_y + i * 0.15
            ax.plot([vp_x + 0.05, vp_x + length - 0.05], [y, y], color=rep2_color, linestyle='--', lw=0.8)

        ax.add_patch(Circle((vp_x + 0.05, vp_y + 0.05), bar_radius, color=rep1_color))
        ax.add_patch(Circle((vp_x + length - 0.05, vp_y + height - 0.05), bar_radius, color=rep1_color))

        ax.text(vp_x + length / 2 - 0.1, vp_y + height + 0.3, "Vue en Plan", fontsize=11, weight="bold")
        ax.annotate("A", xy=(vp_x - 0.3, vp_y + height / 2 + 0.05), fontsize=12, weight='bold')
        ax.annotate("A", xy=(vp_x + length + 0.15, vp_y + height / 2 + 0.05), fontsize=12, weight='bold')
        ax.annotate("↓", xy=(vp_x - 0.3, vp_y + height / 2 - 0.05), fontsize=14)
        ax.annotate("↓", xy=(vp_x + length + 0.15, vp_y + height / 2 - 0.05), fontsize=14)
        ax.annotate(f"{height:.2f} m", xy=(vp_x + length + 0.1, vp_y + height / 2), fontsize=9, rotation=90)

        # Repère longitudinal
        ax.annotate("①", xy=(vp_x + length / 2 - 0.03, vp_y + height / 2 - 0.02), fontsize=12, weight="bold")

        # === COUPE A-A (carré 30x30 cm) ===
        cp_x, cp_y = 4.5, 4.2
        ax.plot([cp_x, cp_x + length, cp_x + length, cp_x, cp_x],
                [cp_y, cp_y, cp_y + width, cp_y + width, cp_y], 'k-', lw=2)

        # carré intérieur (coulis/coffrage)
        margin = 0.03
        ax.plot([cp_x + margin, cp_x + length - margin, cp_x + length - margin, cp_x + margin, cp_x + margin],
                [cp_y + margin, cp_y + margin, cp_y + width - margin, cp_y + width - margin, cp_y + margin],
                'gray', lw=1.5, linestyle='--')

        for x in [cp_x + margin, cp_x + length - margin]:
            for y in [cp_y + margin, cp_y + width - margin]:
                ax.add_patch(Circle((x, y), bar_radius, color=rep1_color))

        ax.text(cp_x + length / 2 - 0.1, cp_y + width + 0.3, "Coupe A-A", fontsize=11, weight="bold")
        ax.annotate(f"{length:.2f} m", xy=(cp_x + length / 2 - 0.05, cp_y - 0.25), fontsize=9)
        ax.annotate(f"{width:.2f} m", xy=(cp_x + length + 0.1, cp_y + width / 2 - 0.05), fontsize=9, rotation=90)

        # Repère transversal
        ax.annotate("②", xy=(cp_x + length / 2 - 0.03, cp_y + width / 2 - 0.02), fontsize=12, weight="bold")
        # === NOMENCLATURE ===
        table_x = 7.0
        table_y = 6.5
        row_h = 0.5
        col_w = [0.5, 1.8, 1.0, 1.2, 1.0]  # Qté élargie
        headers = ["Pos", "Désignation", "Forme", "Code", "Qté"]
        values = [
            ["①", "4x⌀16", "00", f"L={height:.2f}m", "4"],
            ["②", f"Etriers ⌀6 / {esp}", "31", f"H={height:.2f}m", f"{round(height / 0.15):.0f}"]
        ]
        for i, h in enumerate(headers):
            x = table_x + sum(col_w[:i])
            y = table_y
            ax.add_patch(Rectangle((x, y), col_w[i], row_h, fill=False))
            ax.text(x + 0.05, y + row_h / 2 - 0.1, h, fontsize=8, weight="bold")

        for j, row in enumerate(values):
            for i, val in enumerate(row):
                x = table_x + sum(col_w[:i])
                y = table_y - (j + 1) * row_h
                ax.add_patch(Rectangle((x, y), col_w[i], row_h, fill=False))
                if i == 2:
                    draw_forme(val, ax, x + 0.05, y + 0.1)
                else:
                    ax.text(x + 0.05, y + row_h / 2 - 0.1, val, fontsize=8, ha='left')

        # === LÉGENDE GRAPHIQUE ===
        lg_x, lg_y = 7.0, 2.2
        ax.text(lg_x, lg_y + 1.0, "LÉGENDE", fontsize=10, weight="bold")
        ax.plot([lg_x, lg_x + 0.4], [lg_y + 0.8, lg_y + 0.8], 'k-', lw=2)
        ax.text(lg_x + 0.5, lg_y + 0.75, "Contour béton", fontsize=8)
        ax.add_patch(Circle((lg_x + 0.2, lg_y + 0.55), bar_radius, color=rep1_color))
        ax.text(lg_x + 0.5, lg_y + 0.5, "Armature longitudinale", fontsize=8)
        ax.plot([lg_x, lg_x + 0.4], [lg_y + 0.3, lg_y + 0.3], color=rep2_color, linestyle='--', lw=1)
        ax.text(lg_x + 0.5, lg_y + 0.25, "Étriers (transversaux)", fontsize=8)

        # === CARTOUCHE ===
        ct_x, ct_y = 1.0, 0.3
        ax.text(ct_x, ct_y + 0.5, "Projet : BE.ON", fontsize=10)
        ax.text(ct_x + 3.0, ct_y + 0.5, f"Dimensions : {length:.2f} x {width:.2f} x {height:.2f} m", fontsize=10)
        ax.text(ct_x, ct_y + 0.2, f"Armatures : {longi} / {transv}", fontsize=10)

        # === SAUVEGARDE DE L'IMAGE ===
        plt.savefig(img_path, dpi=150)
        plt.close()

        # === PDF UNICODE AVEC FPDF2 + NOTOSANS ===
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.add_font("NotoSans", "", "./NotoSans-Regular.ttf", uni=True)
        pdf.set_font("NotoSans", size=11)
        pdf.cell(0, 10, txt="Rapport de Ferraillage – BE.ON ⌀ φ ✔️", ln=True)
        pdf.image(img_path, x=10, y=20, w=270)
        pdf.output(pdf_path)

        return FileResponse(pdf_path, media_type="application/pdf", filename="rapport_ferraillage.pdf")

    except Exception as e:
        import traceback
        return JSONResponse(status_code=500, content={"error": str(e), "trace": traceback.format_exc()})
