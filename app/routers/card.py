from app.models import CardBase, CardOut
from app.db.database import CardDB, insert_card, get_card_by_id, get_cards, get_user_by_id, get_session
from app.tools.verifiers import verify_card, verify_user, verify_user_admin
from fastapi import APIRouter, status, HTTPException, Depends
from app.auth.auth import decode_token, oauth2_scheme, TokenData

router = APIRouter(
    prefix="/cards",
    tags=["Cards"]
)

@router.post("/", status_code = status.HTTP_201_CREATED)
async def create_card(cardBase: CardBase, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    user = verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_user_admin(user.is_admin) # Check if the user is admin

    insert_card(session, CardDB(
        id_expansion = cardBase.id_expansion,
        name = cardBase.name,
        rarity = cardBase.rarity,
        price = int(cardBase.price*100),
        card_number = cardBase.card_number,
        frontcard = cardBase.frontcard,
        backcard = cardBase.backcard
    ))


@router.post("/batch", status_code = status.HTTP_201_CREATED)
async def create_cards(cardBaseList: list[CardBase], token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    user = verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_user_admin(user.is_admin) # Check if the user is admin

    [insert_card(session, CardDB(
        id_expansion = cardBase.id_expansion,
        name = cardBase.name,
        rarity = cardBase.rarity,
        price = int(cardBase.price*100),
        card_number = cardBase.card_number,
        frontcard = cardBase.frontcard,
        backcard = cardBase.backcard
    )) for cardBase in cardBaseList]


@router.get(
        "/",
        response_model = list[CardOut], 
        status_code = status.HTTP_200_OK
)
async def read_all_cards(token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    verify_user(get_user_by_id(session, data.id)) # Check if the user exists

    return [CardOut(id = card.id, id_expansion = card.id_expansion, name = card.name, rarity = card.rarity, price = card.price/100, card_number = card.card_number, frontcard = card.frontcard, backcard = card.backcard) for card in get_cards(session)]


@router.get(
        "/{id}",
        response_model=CardOut,
        status_code = status.HTTP_200_OK
)
async def read_card_by_id(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    
    # Verifiers
    verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    card_target = verify_card(get_card_by_id(session, id)) # Check if the card exists

    return CardOut(
            id = card_target.id, 
            id_expansion = card_target.id_expansion, 
            name = card_target.name, 
            rarity = card_target.rarity,
            price = card_target.price/100,
            card_number = card_target.card_number,
            frontcard = card_target.frontcard, 
            backcard = card_target.backcard
        )
