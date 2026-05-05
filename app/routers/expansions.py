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
    
    return [ExpansionOut(id=expansion.id, id_generacion=expansion.id_generation, name=expansion.name, year=expansion.year) for expansion in get_expansions(session)]

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
            year=expansion_target.year
        )


@router.get(
        "/{id}/open-boosted", 
        response_model=list[CardOut],
        status_code=status.HTTP_200_OK
)
async def open_boosted_pack(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    
    user = get_user_by_id(session, data.id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    #TODO: Cantidad temporal hasta que se remplace por el precio del sobre seleccionado o poner precio estatico por sobre.
    if user.money <  5:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Saldo insuficiente."
        )

    if not get_expansion_by_id(session, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expansion not found."
        )


    booster = choices(get_cards_by_expansion_and_rarity(session, id, Rarity.common), k=5)
    booster += choices(get_cards_by_expansion_and_rarity(session, id, Rarity.uncommon), k=3)
    booster += choices(get_cards_by_expansion_and_rarity(session, id, Rarity.rare), k=1)
    card_rarity: Rarity = choices(rarity_variable, weights=probabilities, k=1)[0]
    booster += choices(get_cards_by_expansion_and_rarity(session, id, card_rarity), k=1)

    [create_user_card(session, UserCardDB(id_card=c.id ,id_user=data.id, price=c.price, psa=None, sold=False)) for c in booster]

    return [CardOut(id=card.id, id_expansion=card.id_expansion, name=card.name, rarity=card.rarity, price=card.price, card_number=card.card_number, frontcard=card.frontcard, backcard=card.backcard) for card in booster]

@router.get(
        "{id}/collection",
        response_model=list[CollectionCardOut],
        status_code=status.HTTP_200_OK
)
async def read_collection(id: int, expansion: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    if not get_user_by_id(session, data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    if not get_expansion_by_id(session, expansion):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expansion not found."
        )
     
    collection_card_list: list[CollectionCardOut] = []

    for card_list in get_formated_user_card(session, id, expansion, -1, -1):
        collection_card_list.append(
                CollectionCardOut(
                        id_card=card_list.card.id,
                        card_number=card_list.card.card_number,
                        card_name=card_list.card.name,
                        quantity=len(card_list.user_cards),
                        frontcard=card_list.card.frontcard,
                    )
            )

    return collection_card_list
