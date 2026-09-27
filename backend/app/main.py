from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .database import Base, engine
from .routers import auth as auth_router, tasks, equipment, corridor, recommendations, dashboard
from . import seed as seed_module

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_module.run()
    yield

app = FastAPI(title="Railway Maintenance Optimization API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(tasks.router)
app.include_router(equipment.router)
app.include_router(corridor.router)
app.include_router(recommendations.router)
app.include_router(dashboard.router)

@app.get("/api/health")
def health():
    return {"status": "ok"}

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
