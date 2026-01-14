from fastapi import FastAPI, status
from pydantic import BaseModel
from app.routers import users, card
from app.db.database import create_database_and_tables

app = FastAPI(debug=True)
app.include_router(users.router)
app.include_router(card.router)
app.include_router(expansions.router)
app.include_router(generations.router)

@app.on_event("startup")
async def on_startup():
    create_database_and_tables()

@app.get("/")
async def root():
    return {"message": "Welcome to my api made with fastAPI"}


