from app.models import CardBase, ExpansionBase, ExpansionOut, CollectionCardOut, CardOut
from fastapi import APIRouter, status, HTTPException, Depends
from app.auth.auth import decode_token, oauth2_scheme, TokenData
from random import choices
from app.tools.tools import get_formated_user_card
from app.db.database import (
    ExpansionDB,
    CardDB,
    UserCardDB,
    Rarity,
    rarity_variable,
    probabilities,
    insert_expansion, 
    get_session,
    get_expansion_by_name, 
    get_expansion_by_id, 
    get_expansions, 
    get_user_by_id,
    update_user,
    get_cards_by_expansion, 
    get_cards_by_expansion_and_rarity,
    create_user_card
)

router = APIRouter(
    prefix = "/expansions",
    tags = ["Expansions"]
)

@router.post(
        "/", 
        status_code=status.HTTP_201_CREATED
)
async def create_expansion(ExpansionBase: ExpansionBase, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    if not get_user_by_id(session, data.id) or not data.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    expansionDB = get_expansion_by_name(session, ExpansionBase.name)
    if expansionDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Expansion alredy exists."
        )
    insert_expansion(session, ExpansionDB(
        id_generation=ExpansionBase.id_generacion,
        name=ExpansionBase.name,
        price=int(ExpansionBase.price*100),
        year=ExpansionBase.year
    ))


@router.get(
        "/", 
        response_model=list[ExpansionOut], 
        status_code=status.HTTP_200_OK
)
async def read_all_expansions(token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    if not get_user_by_id(session, data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
    
    return [ExpansionOut(id=expansion.id, id_generacion=expansion.id_generation, name=expansion.name, price=expansion.price/100, year=expansion.year) for expansion in get_expansions(session)]

@router.get(
        "/{id}",
        response_model=ExpansionOut,
        status_code=status.HTTP_200_OK
)
async def read_expansion(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    if not get_user_by_id(session, data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    expansion_target = get_expansion_by_id(session, id)

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

    if not get_user_by_id(session, data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    if not get_expansion_by_id(session, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expansion not found."
        )

    return [CardOut(id=c.id, id_expansion=id, name=c.name, rarity=c.rarity, price=c.price/100, card_number=c.card_number, frontcard=c.frontcard, backcard=c.backcard) for c in get_cards_by_expansion(session, id)]



