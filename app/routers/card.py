from app.models import CardBase, CardOut
from app.db.database import CardDB, insert_card, get_card_by_name, get_cards, get_user_by_username
from fastapi import APIRouter, status, HTTPException, Depends
from app.auth.auth import Token, decode_token, oauth2_scheme, TokenData

router = APIRouter(
    prefix="/cards",
    tags=["Cards"]
)

@router.post("/", status_code = status.HTTP_201_CREATED)
async def create_card(cardBase: CardBase, token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if get_user_by_username(data.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    cardDB = get_card_by_name(cardBase.name)
    if cardDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Card alredy exists"
        )
    insert_card(CardDB(
        id_expansion = cardBase.id_expansion,
        name = cardBase.name,
        rarity = cardBase.rarity,
        frontcard = cardBase.frontcard,
        backcard = cardBase.backcard
    ))


@router.get("/", response_model = list[CardOut], status_code = status.HTTP_200_OK)
async def read_all_cards(token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if get_user_by_username(data.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
    
    return [CardOut(id = card.id, id_expansion = card.id_expansion, name = card.name, rarity = card.rarity, frontcard = card.frontcard, backcard = card.backcard) for card in get_cards()]


@router.get("/{id}", status_code = status.HTTP_200_OK)
async def read_card_by_id(id: int, token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)

    if get_user_by_username(data.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )
    
    return [CardOut(id = card.id, id_expansion = card.id_expansion, name = card.name, rarity = card.rarity, frontcard = card.frontcard, backcard = card.backcard) for card in get_cards() if card.id == id]
