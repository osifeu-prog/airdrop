from fastapi import FastAPI
from backend.app.api.v1 import public

app = FastAPI()
app.include_router(public.router, prefix="/public")
