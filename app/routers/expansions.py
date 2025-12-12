from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix = "/expansions",
    tags = ["/expansions"]
)

class ExpansionDB(BaseModel):
    id: int
    name: str
    year: int

class ExpansionIn(BaseModel):
    name: str
    year: int

expansions: list[ExpansionDB] = []

@router.post("/", status_code = status.HTTP_201_CREATED)
async def create_expansion(ExpansionIn: ExpansionIn):
    expansions.append(
        ExpansionDB(
            id = len(expansions) + 1,
            name = ExpansionIn.name,
            year = ExpansionIn.year
        )
    )

@router.get("/", status_code = status.HTTP_200_OK)
async def get_expansins():
    pass