from fastapi import FastAPI, status, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.routers import users, card, expansions, generations, media
from app.db.database import create_database_and_tables, create_admin_user
from app.auth.auth import get_hash_password 

app = FastAPI(debug=True)
app.include_router(users.router)
app.include_router(card.router)
app.include_router(expansions.router)
app.include_router(generations.router)
app.include_router(media.router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
async def on_startup():
    create_database_and_tables()
    create_admin_user(get_hash_password("adm1029"))

@app.get("/")
async def root():
    return {"message": "Welcome to my api made with fastAPI"}


