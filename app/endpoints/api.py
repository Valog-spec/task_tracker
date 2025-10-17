from fastapi import APIRouter

from endpoints import auth, tasks, user

routers = APIRouter(prefix="/api")

routers.include_router(tasks.router)
routers.include_router(auth.router)
routers.include_router(user.router)
