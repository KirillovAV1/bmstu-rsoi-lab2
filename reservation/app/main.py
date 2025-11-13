from fastapi import FastAPI
from .api import router

app = FastAPI(title='Reservation API')
app.include_router(router)
