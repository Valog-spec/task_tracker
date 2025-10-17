from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from core.dependencies import async_engine, async_session, shutdown_event, startup_event
from endpoints.api import routers
from models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
        await async_session().close()
        await async_engine.dispose()


def create_application() -> FastAPI:
    """Создание приложения FastAPI."""
    application = FastAPI(lifespan=lifespan)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://task-streamlit.onrender.com",
            "http://localhost:8501",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_event_handler("startup", startup_event)
    application.add_event_handler("shutdown", shutdown_event)
    application.include_router(routers)

    return application


app = create_application()
