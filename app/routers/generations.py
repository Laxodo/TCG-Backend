from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix = "/generation",
    tags = ["generation"]
)

class GenerationDB(BaseModel):
    id: int
    name: str
    year: int

class GenerationIn(BaseModel):
    name: str
    year: int

generations: list[GenerationDB] = []

@router.post("/", status_code = status.HTTP_201_CREATED)
async def create_generation(GenerationIn: GenerationIn):
    generations.append(
        GenerationDB(
            id = len(generations) + 1,
            name = GenerationIn.name,
            year = GenerationIn.year
        )
    )

@router.get("/", status_code = status.HTTP_200_OK)
async def get_generations():
    lista = []
    for generation in generations:
        lista.append(
            {
                "id": generation.id,
                "name": generation.name,
                "year": generation.year
            }
        )
    return lista

@router.get("/{id}", status_code = status.HTTP_200_OK)
async def get_generation_by_id(id: int):
    for generation in generations:
        if generation.id == id:
            return {
                "id": generation.id,
                "name": generation.name,
                "year": generation.year
            }
    
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = f"La carta con el id {id} no existe"
    )