from app.models import GenerationBase, GenerationOut, ExpansionOut
from app.db.database import GenerationDB, insert_generation, get_generation_by_name, get_generation_by_id, get_generations, get_user_by_username, get_session, get_expansion_by_generation
from fastapi import APIRouter, status, HTTPException, Depends
from app.auth.auth import decode_token, oauth2_scheme, TokenData

router = APIRouter(
    prefix = "/generation",
    tags = ["Generation"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_generation(genBase: GenerationBase, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    if not get_user_by_username(session, data.username) or not data.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    genDB = get_generation_by_name(session, genBase.name)
    if genDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Generation alredy exists."
        )
    insert_generation(session, GenerationDB(
        name=genBase.name,
        year=genBase.year
    ))


@router.get(
        "/", 
        response_model=list[GenerationOut], 
        status_code=status.HTTP_200_OK
)
async def read_all_generations(token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    if not get_user_by_username(session, data.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
    
    return [GenerationOut(id=gen.id, name=gen.name, year=gen.year) for gen in get_generations(session)]


@router.get(
        "/{id}", 
        response_model=GenerationOut,
        status_code=status.HTTP_200_OK
)
async def read_generation(id: int, token = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    if not get_user_by_username(session, data.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    gen_target = get_generation_by_id(session, id)

    return GenerationOut(
            id=gen_target.id, 
            name=gen_target.name, 
            year=gen_target.year
        )

@router.get(
    "/{id}/expansions",
    response_model=list[ExpansionOut],
    status_code=status.HTTP_200_OK
)
async def read_generation_expansions(id: int, token = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    if not get_user_by_username(session, data.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    if not get_generation_by_id(session, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found"
        )

    return [ExpansionOut(id=e.id, id_generacion=id, name=e.name, year=e.year) for e in get_expansion_by_generation(session, id)]
