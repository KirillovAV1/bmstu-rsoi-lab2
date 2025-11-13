from fastapi import FastAPI
from .api import router

app = FastAPI(title="Gateway API")
app.include_router(router)
