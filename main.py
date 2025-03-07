import uvicorn
import os
from fastapi import FastAPI
from chart_generator import generate_chart

app = FastAPI()

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
    port = int(os.getenv("PORT", 8000))  # Railway uses PORT from environment variables
    uvicorn.run(app, host="0.0.0.0", port=port)
