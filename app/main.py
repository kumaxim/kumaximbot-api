from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from .config import config
from .api.routers import posts, contacts, default, webhook, users
from .tgbot.bot import dp as dispatcher, bot


@asynccontextmanager
async def startup(application: FastAPI):
    workflow_data = {
        "app": application,
        "dispatcher": dispatcher,
        "bot": bot,
        **dispatcher.workflow_data,
    }

    await dispatcher.emit_startup(**workflow_data)
    yield
    await dispatcher.emit_shutdown(**workflow_data)

app = FastAPI(lifespan=startup, debug=config.dev_mode)
app.add_middleware(
    CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

for module in [posts, contacts, users, webhook, default]:
    if hasattr(module, 'protected'):
        module.router.include_router(module.protected)

    app.include_router(module.router)


handler = Mangum(app, lifespan="on")
