from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
import os
from chart_generator import generate_chart

app = FastAPI()

# Define API endpoint to generate chart
@app.get("/chart/")
def get_chart(instrument: str = Query(...), timeframe: str = Query(...)):
    chart_path = generate_chart(instrument, timeframe)
    if chart_path and os.path.exists(chart_path):
        return FileResponse(chart_path, media_type="image/png")
    return {"error": "Invalid instrument or timeframe"}

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
