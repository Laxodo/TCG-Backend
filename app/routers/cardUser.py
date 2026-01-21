from app.models import CardUserBase, CardUserOut
from app.db.database import CardUserDB, insert_cardUser, get_cardsUser, get_card_by_user, get_user_by_username, get_users
from fastapi import APIRouter, status, HTTPException, Depends
from app.auth.auth import decode_token, oauth2_scheme, TokenData

router = APIRouter(
    prefix="/cardUser",
    tags=["CardUser"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_cardUser(cardUserBase: CardUserBase, token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)
    
    if get_user_by_username(data.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    cardUserDB = get_card_by_user(cardUserBase.id_user)
    if cardUserDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Card alredy exists"
        )
    insert_cardUser(CardUserDB(
        id_user = cardUserBase.id_user,
        id_card = cardUserBase.id_card,
        psa = cardUserBase.psa,
        sold = cardUserBase.sold,
        price = cardUserBase.price
    ))


@router.get("/", response_model=list[CardUserOut], status_code=status.HTTP_200_OK)
async def read_all_cards_user(token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)
    
    if get_user_by_username(data.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
    
    return [CardUserOut(id=cardUser.id, id_user=cardUser.id_user, id_card=cardUser.id_card, psa=cardUser.psa, sold=cardUser.sold, price=cardUser.price) for cardUser in get_users() if cardUser.id_user == id]