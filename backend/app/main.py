from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import load_config
from app.database import close_db, get_db, init_db
from app.routers import accounts, admin, auth, dashboard, preferences
from app.services.aggregator import ServerAggregator
from app.services.config_service import ConfigCache
from app.services.scheduler import start_scheduler, stop_scheduler

static_dir = Path(__file__).parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config()
    app.state.config = config
    init_db(config)

    from app.models import Base
    from app.database import engine, async_session_factory
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    config_cache = ConfigCache()
    async with async_session_factory() as db:
        await config_cache.load(db)

    app.state.config_cache = config_cache
    app.state.aggregator = ServerAggregator(config_cache)

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
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        file_path = static_dir / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(
            static_dir / "index.html",
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )
