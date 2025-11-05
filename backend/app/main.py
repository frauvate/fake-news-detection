from fastapi import FastAPI
from app.routers import auth, search
from app.core.database import init_models

app = FastAPI(
    title="Veerify API",
    description="Sahte haber tespiti projesi",
    version="0.1.0"
)

app.include_router(auth.router)
app.include_router(search.router)

@app.on_event("startup")
async def on_startup():
    await init_models()

@app.get("/")
async def read_root():
    return {"Proje": "Veerify API", "Durum": "Çalışıyor"}
