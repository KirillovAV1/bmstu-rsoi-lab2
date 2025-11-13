from fastapi import FastAPI
from .api import router

app = FastAPI(title='Loyalty API')
app.include_router(router)
