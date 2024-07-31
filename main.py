from fastapi import FastAPI
from routes import CVI, fear_greed, economic_calendar#, on_gain_data, sentiment_analysis

app = FastAPI(
    title="Passive Income Node",
    description="API for passive income project",
    version="0.1",
    contact={
        "name": "Pau Mateu",
        "email": "paumat17@gmail.com",
    }
)

"""Call each route"""
app.include_router(CVI.router, prefix="")
app.include_router(fear_greed.router, prefix="")
app.include_router(economic_calendar.router, prefix="")
# app.include_router(on_gain_data.router, prefix="/on-gain-data")
# app.include_router(sentiment_analysis.router, prefix="/sentiment-analysis")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
