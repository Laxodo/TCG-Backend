from fastapi import FastAPI, status, Depends
from pydantic import BaseModel
from app.routers import users, card, expansions, generations
from app.db.database import create_database_and_tables, get_session
from app.auth.auth import get_hash_password 

app = FastAPI(debug=True)
app.include_router(users.router)
app.include_router(card.router)
app.include_router(expansions.router)
app.include_router(generations.router)

@app.on_event("startup")
async def on_startup(session = Depends(get_session)):
    create_database_and_tables(session, get_hash_password("adm1029"))

@app.get("/")
async def root():
    return {"message": "Welcome to my api made with fastAPI"}


