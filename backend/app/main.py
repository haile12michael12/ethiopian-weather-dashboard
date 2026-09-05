from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.forecast import router as forecast_router

app = FastAPI(
    title=" Weather API",
    description="Serves the SQLite table populated by the web_scrapping Airflow DAG.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your frontend's origin in production
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(forecast_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
