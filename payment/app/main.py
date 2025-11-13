from fastapi import FastAPI
from .api import router

app = FastAPI(title='Payment API')
app.include_router(router)
