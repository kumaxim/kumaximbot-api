import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from .config import config
from .api.routers import posts, contacts, default, webhook


logging.getLogger().setLevel(logging.DEBUG)

app = FastAPI(debug=config.dev_mode)
app.add_middleware(
    CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

for module in [posts, contacts, webhook, default]:
    app.include_router(module.router)


handler = Mangum(app)
