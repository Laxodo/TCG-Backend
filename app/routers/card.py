from app.models import CardBase, CardOut
from app.db.database import CardDB, insert_card, get_card_by_name, get_card_by_id, get_cards, get_user_by_id
from fastapi import APIRouter, status, HTTPException, Depends, Body
from app.auth.auth import Token, decode_token, oauth2_scheme, TokenData

router = APIRouter(
    prefix="/cards",
    tags=["Cards"]
)

@router.post("/", status_code = status.HTTP_201_CREATED)
async def create_card(cardBase: CardBase, token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if not get_user_by_id(data.id) or not data.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    insert_card(CardDB(
        id_expansion = cardBase.id_expansion,
        name = cardBase.name,
        rarity = cardBase.rarity,
        price = cardBase.price,
        card_number = cardBase.card_number,
        frontcard = cardBase.frontcard,
        backcard = cardBase.backcard
    ))


@router.post("/batch", status_code = status.HTTP_201_CREATED)
async def create_cards(cardBaseList: list[CardBase], token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if not get_user_by_id(data.id) or not data.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
    
    [insert_card(CardDB(
        id_expansion = cardBase.id_expansion,
        name = cardBase.name,
        rarity = cardBase.rarity,
        price = cardBase.price,
        card_number = cardBase.card_number,
        frontcard = cardBase.frontcard,
        backcard = cardBase.backcard
    )) for cardBase in cardBaseList]


@router.get(
        "/",
        response_model = list[CardOut], 
        status_code = status.HTTP_200_OK
)
async def read_all_cards(token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if not get_user_by_id(data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
    
    return [CardOut(id = card.id, id_expansion = card.id_expansion, name = card.name, rarity = card.rarity, price = card.price, card_number = card.card_number, frontcard = card.frontcard, backcard = card.backcard) for card in get_cards()]


@router.get("/{id}", status_code = status.HTTP_200_OK)
async def read_card_by_id(id: int, token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if not get_user_by_id(data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )
    
    card_target = get_card_by_id(id)

    return CardOut(
            id = card_target.id, 
            id_expansion = card_target.id_expansion, 
            name = card_target.name, 
            rarity = card_target.rarity,
            price = card.price,
            frontcard = card_target.frontcard, 
            backcard = card_target.backcard
        )
