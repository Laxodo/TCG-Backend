from app.db.database import get_session
from app.db.expansion import get_expansion_by_generation
from app.db.generation import GenerationDB, get_generation_by_id, get_generation_by_name, get_generations, insert_generation
from app.db.user import get_user_by_id
from app.models import ExpansionListOut, GenerationBase, GenerationListOut, GenerationOut, ExpansionOut
from app.tools.verifiers import verify_generation, verify_generation_exists, verify_generation_exists, verify_user, verify_user_admin
from fastapi import APIRouter, status, Depends
from app.auth.auth import decode_token, oauth2_scheme, TokenData

router = APIRouter(
    prefix = "/generations",
    tags = ["Generations"]
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
        response_model=GenerationListOut, 
        status_code=status.HTTP_200_OK
)
async def read_all_generations(token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    
    return GenerationListOut(generations=[GenerationOut(id=gen.id, name=gen.name, year=gen.year) for gen in get_generations(session)])


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
    response_model=ExpansionListOut,
    status_code=status.HTTP_200_OK
)
async def read_generation_expansions(id: int, token = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_generation(get_generation_by_id(session, id)) # Check if the generation exists

    return ExpansionListOut(expansions=[ExpansionOut(id=e.id, id_generacion=id, price=e.price, name=e.name, year=e.year) for e in get_expansion_by_generation(session, id)])
