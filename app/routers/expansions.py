from app.models import CardBase, ExpansionBase, ExpansionOut, CollectionCardOut, CardOut
from fastapi import APIRouter, status, HTTPException, Depends
from app.auth.auth import decode_token, oauth2_scheme, TokenData
from random import choices
from app.db.database import (
    ExpansionDB,
    CardDB,
    UserCardDB,
    Rarity,
    rarity_variable,
    probabilities,
    insert_expansion, 
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
async def create_expansion(ExpansionBase: ExpansionBase, token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if not get_user_by_id(data.id) or not data.is_admin:
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


@router.get(
        "/", 
        response_model=list[ExpansionOut], 
        status_code=status.HTTP_200_OK
)
async def read_all_expansions(token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if not get_user_by_id(data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
    
    return [ExpansionOut(id=expansion.id, id_generacion=expansion.id_generation, name=expansion.name, year=expansion.year) for expansion in get_expansions()]

@router.get(
        "/{id}",
        response_model=ExpansionOut,
        status_code=status.HTTP_200_OK
)
async def read_expansion(id: int, token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if not get_user_by_id(data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    expansion_target = get_expansion_by_id(id)

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
async def open_boosted_pack(id: int, token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)
    
    user = get_user_by_id(data.id)

    #TODO: Comprobar que el usuario tenga saldo suficiente y añadir precio a las expansiones.
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    if not get_expansion_by_id(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expansion not found."
        )


    booster = choices(get_cards_by_expansion_and_rarity(id, Rarity.common), k=5)
    booster += choices(get_cards_by_expansion_and_rarity(id, Rarity.uncommon), k=3)
    booster += choices(get_cards_by_expansion_and_rarity(id, Rarity.rare), k=1)
    card_rarity: Rarity = choices(rarity_variable, weights=probabilities, k=1)[0]
    booster += choices(get_cards_by_expansion_and_rarity(id, card_rarity), k=1)

    [create_user_card(UserCardDB(id_card=c.id ,id_user=data.id, price=c.price, psa=None, sold=False)) for c in booster]

    return [CardOut(id=card.id, id_expansion=card.id_expansion, name=card.name, rarity=card.rarity, price=card.price, card_number=card.card_number, frontcard=card.frontcard, backcard=card.backcard) for card in booster]

#TODO: Terminar esto con la clase CollectionCardOut
@router.get(
        "{id}/collection",
        response_model=list[CollectionCardOut],
        status_code=status.HTTP_200_OK
)
async def read_collection(id: int, token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if not get_user_by_id(data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    if not get_expansion_by_id(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expansion not found."
        )

    return 
