from fastapi import FastAPI
from src.app.core.config import settings
from src.app.api import auth, reports, tenants, health

app = FastAPI(title="TallyAI API", version="1.0")

app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(tenants.router)
app.include_router(health.router)

@app.get("/")
def root():
    return {"message": "Welcome to TallyAI API"}
