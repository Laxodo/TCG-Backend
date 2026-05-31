from app.models import ExpansionBase, ExpansionOut, CardOut
from app.tools.verifiers import verify_expansion, verify_expansion_exists, verify_user, verify_user_admin
from fastapi import APIRouter, status, Depends
from app.auth.auth import decode_token, oauth2_scheme, TokenData
from app.db.database import (
    ExpansionDB,
    insert_expansion, 
    get_session,
    get_expansion_by_name, 
    get_expansion_by_id, 
    get_expansions, 
    get_user_by_id,
    get_cards_by_expansion
)

router = APIRouter(
    prefix = "/expansions",
    tags = ["Expansions"]
)

@router.post(
        "/", 
        status_code=status.HTTP_201_CREATED
)
async def create_expansion(expansionBase: ExpansionBase, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    user = verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_user_admin(user.is_admin) # Check if the user is admin
    verify_expansion_exists(get_expansion_by_name(session, expansionBase.name))
    
    insert_expansion(session, ExpansionDB(
        id_generation=expansionBase.id_generacion,
        name=expansionBase.name,
        price=int(expansionBase.price*100),
        year=expansionBase.year
    ))


@router.get(
        "/", 
        response_model=list[ExpansionOut], 
        status_code=status.HTTP_200_OK
)
async def read_all_expansions(token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    
    return [ExpansionOut(id=expansion.id, id_generacion=expansion.id_generation, name=expansion.name, price=expansion.price/100, year=expansion.year) for expansion in get_expansions(session)]

@router.get(
        "/{id}",
        response_model=ExpansionOut,
        status_code=status.HTTP_200_OK
)
async def read_expansion(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    expansion_target = verify_expansion(get_expansion_by_id(session, id)) # Check if the expansion exists

    return ExpansionOut(
            id=expansion_target.id, 
            id_generacion=expansion_target.id_generation, 
            name=expansion_target.name,
            price=expansion_target.price/100,
            year=expansion_target.year
        )


@router.get(
        "/{id}/cards",
        response_model=list[CardOut],
        status_code=status.HTTP_200_OK
)
async def read_expansion_cards(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_expansion(get_expansion_by_id(session, id)) # Check if the expansion exists

    return [CardOut(id=c.id, id_expansion=id, name=c.name, rarity=c.rarity, price=c.price/100, card_number=c.card_number, frontcard=c.frontcard, backcard=c.backcard) for c in get_cards_by_expansion(session, id)]



