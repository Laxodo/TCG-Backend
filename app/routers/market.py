from random import randint, choices
from app.tools.logs import buy_card_logs, exchange_card_logs, grade_cards_logs
from fastapi import APIRouter, status, HTTPException, Depends
from app.models import OfferOut, QuickSellIn, QuickSellOut, SellIn, UserCardGradeOut, CardOut
from app.auth.auth import decode_token, oauth2_scheme, TokenData
from app.db.database import (
    GRADE_COST,
    Action,
    CardMarketDB,
    ExchangeType,
    LogActivityDB,
    LogHistoryDB,
    LogType,
    Rarity,
    UserCardDB,
    create_log_activity,
    create_log_history,
    rarity_variable,
    probabilities,
    get_session,
    get_card_by_id,
    create_user_card,
    get_user_by_id, 
    get_user_card_by_id,
    get_user_card_by_card_id,
    get_expansion_by_id,
    get_cards_by_expansion_and_rarity,
    update_user, 
    update_user_card, 
    remove_card,
    create_offer,
    remove_offer,
    get_offers,
    get_offer_by_id
) 

router = APIRouter(
    prefix="/market",
    tags=["Market"]
)

@router.post(
    "/cards/quick-sell",
    status_code=status.HTTP_200_OK,
    response_model=QuickSellOut
)
async def quick_sell_cards(cards: QuickSellIn, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    user = get_user_by_id(session, data.id)

    # Check if the user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    total_earn: int = 0

    log = create_log_history(
        session,
        LogHistoryDB(
            id_user=data.id,
            description=f"Quick sell cards with ids {cards.card_list_id}",
            type=LogType.QUICK_SELL.value
        )
    )

    for c in cards.card_list_id:
        user_card = get_user_card_by_id(session, c)
        if user_card and user_card.id_user == data.id:
            total_earn += remove_card(session, c).price
            create_log_activity(
                session,
                LogActivityDB(
                    id_user=data.id,
                    id_card=c,
                    id_log_history=log.id,
                    action=Action.LOST.value,
                    price=user_card.price,
                    psa=user_card.psa
                )
            )

    update_user(session=session, id=data.id, money=user.money+total_earn)
    return QuickSellOut(total_earn=total_earn/100)


@router.post(
    "/cards/{id}/sell",
    status_code=status.HTTP_200_OK
)
async def sell_card(id: int, card: SellIn, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
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

    # Check if the user card is owned by the user
    if user_card.id_user != data.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    # Check if the target user card is for sale
    if user_card.sold is True:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User card already for sale."
        )

    create_offer(session, CardMarketDB(id_user=data.id, id_user_card=user_card.id, exchange_type=ExchangeType.on_sale.value, price=int(card.price*100)))
    update_user_card(session, id, sold=True)


@router.post(
    "/offers/{id}/buy",
    status_code=status.HTTP_200_OK
)
async def buy_card(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    offer = get_offer_by_id(session, id)

    # Check if the offer exists
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Offer with id {id} does not exist."
        )

    user_card_offer = get_user_card_by_id(session, offer.id_user_card)

    # Check if the user card exists
    if not user_card_offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User card with id {offer.id_user_card} does not exist."
        )

    # Check if the target user card is for sale
    if user_card_offer.sold is False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User card is not for sale."
        )

    user_buyer = get_user_by_id(session, data.id)

    # Check if the user exists
    if not user_buyer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    user_seller = get_user_by_id(session, user_card_offer.id_user)

    # Check if the seller exists
    if not user_seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_card_offer.id_user} does not exist."
        )

    # Check if the offer is a sale
    if offer.exchange_type == ExchangeType.on_sale.value:
        # Check if the user have enough money
        if user_buyer.money < offer.price:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="User does not have enough money."
            )

        # Update users
        update_user(session, data.id, money=user_buyer.money-offer.price)
        update_user(session, user_seller.id, money=user_seller.money+offer.price)
        update_user_card(session, user_card_offer.id, sold=False, id_user=data.id)
        remove_offer(session, offer.id)

        # Logs
        buy_card_logs(session, user_buyer, user_seller, user_card_offer, data, offer)

    # Check if the offer is an exchange
    if offer.exchange_type == ExchangeType.on_exchange.value:
        demanded_card = get_user_card_by_card_id(session, data.id, offer.id_card, offer.psa)

        # Check if the user have the demanded card
        if not demanded_card:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User does not have the demanded card."
            )

        # Check if the PSA values match
        if offer.psa != demanded_card.psa:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User does not have the demanded card."
            )

        update_user_card(session, user_card_offer.id, sold=False, id_user=data.id) # Send card
        update_user_card(session, demanded_card.id, sold=False, id_user=user_seller.id) # Obtain card
        remove_offer(session, offer.id)

        # Logs
        exchange_card_logs(session, user_buyer, user_seller, demanded_card, user_card_offer, data)


@router.get(
    "/offers",
    status_code=status.HTTP_200_OK,
    response_model=list[OfferOut]
)
async def read_offer(token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Check if the user exists
    if not get_user_by_id(session, data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    return [OfferOut(**offer) for offer in get_offers(session)]


@router.get(
    "/offers/{id}",
    status_code=status.HTTP_200_OK,
    response_model=OfferOut
)
async def read_offer_by_id(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Check if the user exists
    if not get_user_by_id(session, data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    return get_offer_by_id(session, id)


@router.delete(
    "/offers/{id}",
    status_code=status.HTTP_200_OK
)
async def cancel_offer(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    offer = get_offer_by_id(session, id)

    # Check if the offer exists and if the user is the owner
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Offer with id {id} does not exist."
        )
    
    # Check if the user is the owner of the offer
    if offer.id_user != data.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    user_card = get_user_card_by_id(session, offer.id_user_card)

    # Check if the user card exists
    if not user_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User card with id {offer.id_user_card} does not exist."
        )
    
    # Check if the user exists
    if not get_user_by_id(session, data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    

    update_user_card(session, user_card.id, sold=False)
    remove_offer(session, offer.id)


@router.post(
    "/cards/{id}/exchange",
    status_code=status.HTTP_200_OK
)
async def exchange_card(id: int, id_card: int, psa: int | None = None, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
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

    create_offer(session, CardMarketDB(id_user=data.id, id_user_card=user_card.id, id_card=id_card, psa=psa, exchange_type=ExchangeType.on_exchange.value))
    update_user_card(session, id, sold=True)


@router.post(
    "/cards/{id}/grade",
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

    # Check if user has enough money
    if user.money < GRADE_COST:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient funds"
        )

    update_user(session, data.id, money=user.money-GRADE_COST)

    psa: int =  randint(1,10)
    price: float = user_card.card.price * (1.6 ** (psa - 5))

    # Logs
    grade_cards_logs(session, data.id, user_card, psa, price)

    updated_user_card = update_user_card(session, id, psa=psa, price=int(price))
    return UserCardGradeOut(grade=updated_user_card.psa)


@router.post(
        "/boosters/{id}/open", 
        response_model=list[CardOut],
        status_code=status.HTTP_200_OK
)
async def open_boosted_pack(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    
    user = get_user_by_id(session, data.id)
    expansion = get_expansion_by_id(session, id)

    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    # Check if expansion exists
    if not expansion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expansion not found."
        )

    # Check if user has enough money
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

    # Logs
    log = create_log_history(
        session,
        LogHistoryDB(
            id_user=data.id,
            description=f"Opened boosted pack with id {expansion.id}",
            type=LogType.OPEN_BOOSTER.value
        )
    )

    for c in booster:
        create_user_card(session, UserCardDB(id_card=c.id ,id_user=data.id, price=c.price, psa=None, sold=False))
        create_log_activity(
            session,
            LogActivityDB(
                id_user=data.id,
                id_card=c.id,
                id_log_history=log.id,
                action=Action.GET.value,
                price=c.price,
                psa=None
            )
        )

    return [CardOut(id=card.id, id_expansion=card.id_expansion, name=card.name, rarity=card.rarity, price=card.price/100, card_number=card.card_number, frontcard=card.frontcard, backcard=card.backcard) for card in booster]