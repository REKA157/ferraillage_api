from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
import ezdxf
import os

app = FastAPI()

@app.post("/generate")
async def generate_dxf(request: Request):
    try:
        data = await request.json()
        length = float(data.get("length", 0.4)) * 1000  # convert m to mm
        width = float(data.get("width", 0.4)) * 1000

        armatures = data.get("Armatures", {})
        longi = armatures.get("Longitudinales", "4x12mm")
        transv = armatures.get("Transversales", "⌀6mm @20cm")

        def clean(text):
            return text.replace("⌀", "phi").replace("@", " à ").replace("ø", "phi")

        longi = clean(longi)
        transv = clean(transv)

        doc = ezdxf.new(dxfversion="R2010")
        msp = doc.modelspace()

        # rectangle (section poteau)
        msp.add_lwpolyline([(0, 0), (length, 0), (length, width), (0, width)], close=True)

        # barres longitudinales (coins)
        cover = 40
        radius = 8
        msp.add_circle((cover, cover), radius)
        msp.add_circle((length - cover, cover), radius)
        msp.add_circle((length - cover, width - cover), radius)
        msp.add_circle((cover, width - cover), radius)

        # étrier intérieur
        msp.add_lwpolyline([
            (cover, cover),
            (length - cover, cover),
            (length - cover, width - cover),
            (cover, width - cover),
            (cover, cover)
        ], dxfattribs={"color": 1})

        # annotations
        msp.add_text(f"Longi: {longi}", dxfattribs={"height": 150, "insert": (0, width + 100)})
        msp.add_text(f"Transv: {transv}", dxfattribs={"height": 150, "insert": (0, width + 300)})

        file_path = "/tmp/plan_ferraillage.dxf"
        doc.saveas(file_path)

        return FileResponse(file_path, media_type="application/dxf", filename="plan_ferraillage.dxf")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
