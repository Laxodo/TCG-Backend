from random import randint, choices
from fastapi import APIRouter, status, HTTPException, Depends
from app.models import UserCardGradeOut, CardOut
from app.auth.auth import decode_token, oauth2_scheme, TokenData
from app.db.database import (
    ExchangeType,
    Rarity,
    UserCardDB,
    rarity_variable,
    probabilities,
    get_session,
    get_card_by_id,
    create_user_card,
    get_user_by_id, 
    get_user_card_by_id,
    get_expansion_by_id,
    get_cards_by_expansion_and_rarity,
    update_user, 
    update_user_card, 
    remove_card,
    create_card_offer,
    remove_card_offer,
    read_cards_offers,
    read_card_offer_by_id
) 

router = APIRouter(
    prefix="/market",
    tags=["Market"]
)

@router.post(
    "/quick-sell",
    status_code=status.HTTP_200_OK
)
async def quick_sell_cards(cards: list[int], token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Check if the user exists
    if not get_user_by_id(session, data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
   
    user = get_user_by_id(session, data.id)

    total_earn = sum([remove_card(session, c).price for c in cards if not get_card_by_id(session, c)])
    update_user(session=session, id=data.id, money=user.money+total_earn)


@router.post(
    "/sell/{id}",
    status_code=status.HTTP_200_OK
)
async def sell_card(id: int, price: float, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    user_card = get_user_card_by_id(session, id)

    # Check if the user exists
    if not get_user_by_id(session, data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    # Check if the user card exists
    if not user_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User card with id {id} does not exist."
        )

    # Check if the target user card is for sale
    if user_card.sold is True:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User card already for sale."
        )

    create_card_offer(session, user_card.id, exchange_type=ExchangeType.on_sale.value, price=int(price*100))
    update_user_card(session, id, sold=True)


@router.post(
    "/buy/{id}",
    status_code=status.HTTP_200_OK
)
async def buy_card(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    user = get_user_by_id(session, data.id)
    user_card = get_user_card_by_id(session, id)

    # Check if the user exists
    if not get_user_by_id(session, data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    # Check if the user card exists
    if not user_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User card with id {id} does not exist."
        )

    # Check if the target user card is for sale
    if user_card.sold is False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User card already for sale."
        )

    offer = read_card_offer_by_id(session, id)

    # Check if the user have enough money
    if user.money < offer.price:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="User card already for sale."
        )

    update_user(session, data.id, money=user.money-offer.price)
    update_user_card(session, id, sold=False, id_user=data.id)
    remove_card_offer(session, offer.id)


@router.get(
    "/offers/cards",
    status_code=status.HTTP_200_OK
)
async def get_cards(token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Check if the user exists
    if not get_user_by_id(session, data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    return read_cards_offers(session)


@router.get(
    "/offers/cards/{id}",
    status_code=status.HTTP_200_OK
)
async def get_cards(token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Check if the user exists
    if not get_user_by_id(session, data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    return read_card_offer_by_id(session, id)


@router.post(
    "/cancell-sell/{id}",
    status_code=status.HTTP_200_OK
)
async def cancell_sale_card(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    user_card = get_user_card_by_id(session, id)
    
    # Check if the user exists
    if not get_user_by_id(session, data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    # Check if the user card exists
    if not user_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User card with id {id} does not exist."
        )

    # Check if the target user card is for sale
    if user_card.sold is False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User card already for sale."
        )

    offer = read_card_offer_by_id(session, id)
    update_user_card(session, id, sold=False)
    remove_card_offer(session, offer.id)


@router.post(
    "/grade/{id}",
    status_code=status.HTTP_200_OK,
    response_model=UserCardGradeOut
)
async def grade_card(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    user = get_user_by_id(session, data.id)
    user_card = get_user_card_by_id(session, id)

    # Check if the user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
    
    # Check if the user card exists
    if not user_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User card with id {id} does not exist."
        )

    if user.money < 25:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient funds"
        )

    psa: int =  randint(1,10)
    price: float = user_card.card.price * (1.6 ** (psa - 5))

    updated_user_card = update_user_card(session, id, psa=psa, price=int(price))
    return UserCardGradeOut(grade=updated_user_card.psa)


@router.get(
        "/open-boosted/{id}", 
        response_model=list[CardOut],
        status_code=status.HTTP_200_OK
)
async def open_boosted_pack(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    
    user = get_user_by_id(session, data.id)
    expansion = get_expansion_by_id(session, id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    if not expansion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expansion not found."
        )

    if user.money < expansion.price:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient funds."
        )

    update_user(session, data.id, money=user.money-expansion.price)    

    booster = choices(get_cards_by_expansion_and_rarity(session, id, Rarity.common), k=5)
    booster += choices(get_cards_by_expansion_and_rarity(session, id, Rarity.uncommon), k=3)
    booster += choices(get_cards_by_expansion_and_rarity(session, id, Rarity.rare), k=1)
    card_rarity: Rarity = choices(rarity_variable, weights=probabilities, k=1)[0]
    booster += choices(get_cards_by_expansion_and_rarity(session, id, card_rarity), k=1)

    [create_user_card(session, UserCardDB(id_card=c.id ,id_user=data.id, price=c.price, psa=None, sold=False)) for c in booster]

    return [CardOut(id=card.id, id_expansion=card.id_expansion, name=card.name, rarity=card.rarity, price=card.price/100, card_number=card.card_number, frontcard=card.frontcard, backcard=card.backcard) for card in booster]
