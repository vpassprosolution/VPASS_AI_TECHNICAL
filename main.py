import uvicorn
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles  # ✅ Import StaticFiles
from chart_generator import generate_chart

app = FastAPI()

# ✅ Mount the "static/" directory so images can be served correctly
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"message": "VPASS AI TECHNICAL API is running!"}

@app.get("/chart/")
def get_chart(instrument: str, timeframe: str):
    chart_path = generate_chart(instrument, timeframe)
    if chart_path and os.path.exists(chart_path):
        return {"chart_url": f"https://vpassaitechnical-production.up.railway.app/static/{os.path.basename(chart_path)}"}
    return {"error": "Invalid instrument or timeframe"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Make sure Railway uses this!
    uvicorn.run(app, host="0.0.0.0", port=port)
