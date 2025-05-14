from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
import ezdxf
import os

app = FastAPI()

@app.post("/generate")
async def generate_dxf(request: Request):
    try:
        data = await request.json()
        length = float(data.get("length", 0.3)) * 1000  # m to mm
        width = float(data.get("width", 0.3)) * 1000
        height = float(data.get("height", 3.0)) * 1000

        armatures = data.get("Armatures", {})
        longi = armatures.get("Longitudinales", "4x16mm")
        transv = armatures.get("Transversales", "HA10 ⌀ @15cm")

        def clean(text):
            return text.replace("⌀", "phi").replace("@", "à").replace("ø", "phi")

        longi = clean(longi)
        transv = clean(transv)

        doc = ezdxf.new(dxfversion="R2010")
        msp = doc.modelspace()
        cover = 25
        radius = 8

        # === VUE EN PLAN (en bas à gauche) ===
        origin_x = 0
        origin_y = 0
        msp.add_lwpolyline([
            (origin_x, origin_y),
            (origin_x + length, origin_y),
            (origin_x + length, origin_y + width),
            (origin_x, origin_y + width),
            (origin_x, origin_y)
        ], close=True)

        # barres aux coins
        msp.add_circle((origin_x + cover, origin_y + cover), radius)
        msp.add_circle((origin_x + length - cover, origin_y + cover), radius)
        msp.add_circle((origin_x + length - cover, origin_y + width - cover), radius)
        msp.add_circle((origin_x + cover, origin_y + width - cover), radius)

        # annotation
        msp.add_text("A-A", dxfattribs={"height": 100}).set_pos((origin_x + length/2 - 20, origin_y - 150))

        # === VUE EN COUPE A-A (à droite) ===
        cx = origin_x + 600
        cy = origin_y

        # contour
        msp.add_lwpolyline([
            (cx, cy),
            (cx, cy + height),
            (cx + length, cy + height),
            (cx + length, cy),
            (cx, cy)
        ], close=True)

        # étriers espacés (tous les 150mm)
        etrier_step = 150
        num_etriers = int(height / etrier_step)
        for i in range(num_etriers):
            y = cy + i * etrier_step
            msp.add_lwpolyline([
                (cx + cover, y + cover),
                (cx + length - cover, y + cover),
                (cx + length - cover, y + length - cover),
                (cx + cover, y + length - cover),
                (cx + cover, y + cover)
            ], dxfattribs={"color": 1})

        # barres longitudinales
        msp.add_line((cx + cover, cy), (cx + cover, cy + height))
        msp.add_line((cx + length - cover, cy), (cx + length - cover, cy + height))

        # annotation
        msp.add_text("Coupe A-A", dxfattribs={"height": 100}).set_pos((cx, cy - 150))

        # === TABLEAU ARMATURES (en haut à droite) ===
        tx = origin_x + 1300
        ty = origin_y + height

        msp.add_text("TABLEAU ARMATURES", dxfattribs={"height": 100}).set_pos((tx, ty + 100))
        msp.add_text("1 - Longi: " + longi, dxfattribs={"height": 80}).set_pos((tx, ty))
        msp.add_text("2 - Transv: " + transv, dxfattribs={"height": 80}).set_pos((tx, ty - 120))

        file_path = "/tmp/plan_ferraillage_complet.dxf"
        doc.saveas(file_path)

        return FileResponse(file_path, media_type="application/dxf", filename="plan_ferraillage_complet.dxf")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
