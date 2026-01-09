from app.models import CardBase, ExpansionBase, ExpansionOut
from app.db.database import ExpansionDB, insert_expansion, get_expansion_by_name, get_expansions, get_users
from fastapi import APIRouter, status, HTTPException, Depends
from app.auth.auth import decode_token, oauth2_scheme, TokenData

router = APIRouter(
    prefix = "/expansions",
    tags = ["Expansions"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_expansion(ExpansionBase: ExpansionBase, token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if data.username not in [u.username for u in get_users()]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    expansionDB = get_expansion_by_name(ExpansionBase.name)
    if expansionDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Expansion alredy exists."
        )
    insert_expansion(ExpansionDB(
        id_generation=ExpansionBase.id_generacion,
        name=ExpansionBase.name,
        year=ExpansionBase.year
    ))


@router.get("/", response_model=list[ExpansionOut], status_code=status.HTTP_200_OK)
async def read_all_expansions(token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if data.username not in [u.username for u in get_users()]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
    
    return [ExpansionOut(id=expansion.id, id_generacion=expansion.id_generation, name=expansion.name, year=expansion.year) for expansion in get_expansions()]

@router.get("/{name}", status_code=status.HTTP_200_OK)
async def read_expansion(name: str, token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if data.username not in [u.username for u in get_users()]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
    
    return [ExpansionOut(id=expansion.id, id_generacion=expansion.id_generation, name=expansion.name, year=expansion.year) for expansion in get_expansions() if expansion.name == name]