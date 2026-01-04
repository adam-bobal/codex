from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class TickerRequest(BaseModel):
    ticker: str

@app.post("/analyze")
async def analyze(request: TickerRequest):
    # This is where your Gemini/Perplexity/Brave logic lives
    # ticker = request.ticker
    # result = await run_automated_research(ticker)
    return {"analysis": f"Completed graduate-level valuation for {request.ticker}."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)