from app.models import GenerationBase, GenerationOut, ExpansionOut
from app.db.database import GenerationDB, get_user_by_id, insert_generation, get_generation_by_name, get_generation_by_id, get_generations, get_user_by_username, get_session, get_expansion_by_generation
from app.tools.verifiers import verify_generation, verify_generation_exists, verify_generation_exists, verify_user, verify_user_admin
from fastapi import APIRouter, status, HTTPException, Depends
from app.auth.auth import decode_token, oauth2_scheme, TokenData

router = APIRouter(
    prefix = "/generation",
    tags = ["Generation"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_generation(gen_base: GenerationBase, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    user = verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_user_admin(user.is_admin) # Check if the user is admin
    verify_generation_exists(get_generation_by_name(session, gen_base.name)) # Check if the generation exists

    insert_generation(session, GenerationDB(
        name=gen_base.name,
        year=gen_base.year
    ))


@router.get(
        "/", 
        response_model=list[GenerationOut], 
        status_code=status.HTTP_200_OK
)
async def read_all_generations(token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    
    return [GenerationOut(id=gen.id, name=gen.name, year=gen.year) for gen in get_generations(session)]


@router.get(
        "/{id}", 
        response_model=GenerationOut,
        status_code=status.HTTP_200_OK
)
async def read_generation(id: int, token = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_generation(get_generation_by_id(session, id)) # Check if the generation exists

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

    # Verifiers
    verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_generation(get_generation_by_id(session, id)) # Check if the generation exists

    return [ExpansionOut(id=e.id, id_generacion=id, name=e.name, year=e.year) for e in get_expansion_by_generation(session, id)]
