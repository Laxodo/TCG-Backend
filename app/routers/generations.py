from app.models import GenerationBase, GenerationOut
from app.db.database import GenerationDB, insert_generation, get_generation_by_name, get_generations, get_users
from fastapi import APIRouter, status, HTTPException, Depends
from app.auth.auth import decode_token, oauth2_scheme, TokenData

router = APIRouter(
    prefix = "/generation",
    tags = ["Generation"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_generation(genBase: GenerationBase, token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if data.username not in [u.username for u in get_users()]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    genDB = get_generation_by_name(genBase.name)
    if genDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Generation alredy exists."
        )
    insert_generation(GenerationDB(
        name=genBase.name,
        year=genBase.year
    ))


@router.get("/", response_model=list[GenerationOut], status_code=status.HTTP_200_OK)
async def read_all_generations(token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if data.username not in [u.username for u in get_users()]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
    
    return [GenerationOut(id=gen.id, name=gen.name, year=gen.year) for gen in get_generations()]


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def read_generation_by_name(id: int, token = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if data.username not in [u.username for u in get_users()]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    return [GenerationOut(id=gen.id, name=gen.name, year=gen.year) for gen in get_generations() if gen.id == id]
