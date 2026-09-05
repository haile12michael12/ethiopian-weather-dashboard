from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.forecast import router as forecast_router
from .routes.notifications import router as notifications_router

app = FastAPI(
    title="Ethiopian Weather API",
    description="Serves the resilient multi-source weather pipeline with Telegram Bot and Web Push alert notifications.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your frontend's origin in production
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(forecast_router)
app.include_router(notifications_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
