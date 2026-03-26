import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import load_config
from app.database import close_db, init_db
from app.routers import accounts, auth, dashboard, preferences
from app.services.aggregator import ServerAggregator
from app.services.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config()
    app.state.config = config
    app.state.aggregator = ServerAggregator(config.relay_servers)
    init_db(config)

    from app.models import Base
    from app.database import engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    start_scheduler(app)
    yield
    stop_scheduler()
    await close_db()


app = FastAPI(title="OMR Portal", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(preferences.router, prefix="/api/preferences", tags=["preferences"])

static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
