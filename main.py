from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
import subprocess
import json
import os

app = FastAPI()

@app.post("/generate")
async def generate_plan(request: Request):
    try:
        data = await request.json()

        # Enregistrement du fichier d'entrée
        with open("/tmp/input.json", "w") as f:
            json.dump(data, f)

        # Appel du script FreeCAD via subprocess
       process = subprocess.run(
    [
        "C:\\Program Files\\FreeCAD 1.0\\bin\\FreeCADCmd.exe",
        "generate_structure_fc.py"
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)


        if process.returncode != 0:
            return JSONResponse(
                status_code=500,
                content={"error": "FreeCAD execution failed", "stderr": process.stderr}
            )

        pdf_path = "/tmp/plan_structure.pdf"
        if not os.path.exists(pdf_path):
            return JSONResponse(status_code=500, content={"error": "Le PDF n'a pas été généré"})

        return FileResponse(pdf_path, media_type="application/pdf", filename="plan_structure.pdf")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
