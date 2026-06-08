from random import randint, choices
from app.tools.verifiers import verify_expansion, verify_offer, verify_offer_owner, verify_offer_self_owner, verify_offer_type, verify_user, verify_user_card_for_sale, verify_user_card_owner, verify_user_card_psa_target, verify_user_card_target, verify_user_currency, verify_user_target, verify_user_card
from app.tools.logs import buy_card_logs, exchange_card_logs, grade_cards_logs
from fastapi import APIRouter, status, Depends
from app.models import BoostedPackOut, ExchangeIn, OfferListOut, OfferOut, QuickSellIn, QuickSellOut, SellIn, UserCardGradeOut, CardOut
from app.auth.auth import decode_token, oauth2_scheme, TokenData
from app.db.card import PROBABILITIES, RARITY_VARIABLE, Rarity, get_cards_by_expansion_and_rarity
from app.db.cardmarket import GRADE_COST, CardMarketDB, ExchangeType, create_offer, get_offer_by_id, get_offers, get_offers_by_not_user_id, get_offers_by_user_id, remove_offer
from app.db.database import get_session
from app.db.expansion import get_expansion_by_id
from app.db.logactivity import Action, LogActivityDB, create_log_activity
from app.db.loghistory import LogHistoryDB, LogType, create_log_history
from app.db.user import get_user_by_id, update_user
from app.db.usercard import UserCardDB, create_user_card, get_user_card_by_card_id, get_user_card_by_id, remove_card, update_user_card

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
    user = verify_user(get_user_by_id(session, data.id)) # Get user and check if the user exists
    total_earn: int = 0

    # Log
    log = create_log_history(
        session,
        LogHistoryDB(
            id_user=data.id,
            description=f"Quick sell cards.",
            type=LogType.QUICK_SELL.value
        )
    )

    for c in cards.card_list_id:
        user_card = get_user_card_by_id(session, c)
        try:
            verify_user_card_for_sale(user_card.sold) # Check if the target user card is for sale
            if user_card and user_card.id_user == data.id:
                total_earn += remove_card(session, c).price
                create_log_activity(
                    session,
                    LogActivityDB(
                        id_user=data.id,
                        id_card=user_card.id_card,
                        id_log_history=log.id,
                        action=Action.LOST.value,
                        price=user_card.price,
                        psa=user_card.psa
                    )
                )
        except:
            continue
        

    update_user(session=session, id=data.id, money=user.money+total_earn)
    return QuickSellOut(total_earn=total_earn/100)


@router.post(
    "/cards/{id}/sell",
    status_code=status.HTTP_200_OK
)
async def sell_card(id: int, card: SellIn, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    user_card = verify_user_card(get_user_card_by_id(session, id))

    # Verifiers
    verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_user_card_owner(user_card.id_user, data.id) # Check if the user card is owned by the user
    verify_user_card_for_sale(user_card.sold) # Check if the target user card is for sale

    create_offer(session, CardMarketDB(id_user=data.id, id_user_card=user_card.id, exchange_type=ExchangeType.sale.value, price=int(card.price*100)))
    update_user_card(session, id, sold=True)


@router.post(
    "/offers/{id}/buy",
    status_code=status.HTTP_200_OK
)
async def buy_card(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    offer = verify_offer(get_offer_by_id(session, id)) # Check if the offer exists
    user_card_offer = verify_user_card(get_user_card_by_id(session, offer.id_user_card)) # Check if the user card exists
    user_buyer = verify_user(get_user_by_id(session, data.id)) # Check if the buyer exists
    user_seller = verify_user_target(get_user_by_id(session, user_card_offer.id_user)) # Check if the seller exists

    #Verifiers
    verify_user_card_for_sale(not user_card_offer.sold) # Check if the target user card is for sale
    verify_offer_self_owner(user_buyer.id, offer.id_user) # Check if the user is the owner of the offer

    # Check if the offer is a sale
    if offer.exchange_type == ExchangeType.sale.value:
        # Check if the user have enough money
        verify_user_currency(user_buyer.money, offer.price)

        # Update users
        update_user(session, data.id, money=user_buyer.money-offer.price)
        update_user(session, user_seller.id, money=user_seller.money+offer.price)
        update_user_card(session, user_card_offer.id, sold=False, id_user=data.id)
        remove_offer(session, offer.id)

        # Logs
        buy_card_logs(session, user_buyer, user_seller, user_card_offer, data, offer)

    # Check if the offer is an exchange
    if offer.exchange_type == ExchangeType.exchange.value:
        demanded_card = verify_user_card_target(get_user_card_by_card_id(session, data.id, offer.id_card, offer.psa)) # Check if the user have the demanded card

        # Verifiers
        verify_user_card_psa_target(offer.psa, demanded_card.psa) # Check if the PSA values match

        #Update database
        update_user(session, data.id, exchanges=user_buyer.exchanges+1)
        update_user(session, user_seller.id, exchanges=user_seller.exchanges+1)
        update_user_card(session, user_card_offer.id, sold=False, id_user=data.id) # Send card
        update_user_card(session, demanded_card.id, sold=False, id_user=user_seller.id) # Obtain card
        remove_offer(session, offer.id)

        # Logs
        exchange_card_logs(session, user_buyer, user_seller, demanded_card, user_card_offer, data)


@router.get(
    "/offers",
    status_code=status.HTTP_200_OK,
    response_model=OfferListOut
)
async def read_offer(id_user: int | None = None, type: str | None = None, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Check if the user exists
    verify_user(get_user_by_id(session, data.id))
    verify_user_target(get_user_by_id(session, id_user)) if id_user else None
    verify_offer_type(type)

    offers = []

    if id_user and not data.is_admin:
        offers = get_offers_by_user_id(session, id_user, type)
    if not id_user and not data.is_admin:
        offers = get_offers_by_not_user_id(session, data.id, type)
    if data.is_admin:
        offers = get_offers(session)

    return OfferListOut(
        offers=[
            OfferOut(
                id=offer.id, 
                id_card=offer.id_card, 
                id_user_card=offer.id_user_card, 
                exchange_type=offer.exchange_type, 
                image_card_offer=offer.user_card.card.frontcard if offer.user_card and offer.user_card.card else None, 
                image_card_demanded=offer.card.frontcard if offer.card else None,
                expansion_name=offer.user_card.card.expansion.name,
                price=offer.price/100 if offer.price else None, 
                psa=offer.psa
            ) 
            for offer in offers
        ]
    )


@router.get(
    "/offers/{id}",
    status_code=status.HTTP_200_OK,
    response_model=OfferOut
)
async def read_offer_by_id(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Check if the user exists
    verify_user(get_user_by_id(session, data.id))

    offer = get_offer_by_id(session, id)

    return OfferOut(
        id=offer.id, 
        id_card=offer.id_card, 
        id_user_card=offer.id_user_card, 
        exchange_type=offer.exchange_type, 
        image_card_offer=offer.user_card.card.frontcard if offer.user_card and offer.user_card.card else None, 
        image_card_demanded=offer.card.frontcard if offer.card else None,
        expansion_name=offer.user_card.card.expansion.name,
        price=offer.price/100 if offer.price else None, 
        psa=offer.psa
    ) 


@router.delete(
    "/offers/{id}",
    status_code=status.HTTP_200_OK
)
async def cancel_offer(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    offer = verify_offer(get_offer_by_id(session, id)) # Check if the offer exists
    user_card = verify_user_card(get_user_card_by_id(session, offer.id_user_card)) # Check if the user card exists

    # Verifiers
    verify_offer_owner(offer.id_user, data.id) # Check if the user is the owner of the offer
    verify_user(get_user_by_id(session, data.id)) # Check if the user exists

    # Update database
    update_user_card(session, user_card.id, sold=False)
    remove_offer(session, offer.id)


@router.post(
    "/cards/{id}/exchange",
    status_code=status.HTTP_200_OK
)
async def exchange_card(id: int, target: ExchangeIn, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    user_card = verify_user_card(get_user_card_by_id(session, id)) # Check if the user card exists

    # Verifiers
    verify_user_card_owner(user_card.id_user, data.id) # Check if the user card is owned by the user
    verify_user(get_user_by_id(session, data.id)) # Check if the user exists

    # Update database
    create_offer(session, CardMarketDB(id_user=data.id, id_user_card=user_card.id, id_card=target.id_card, psa=target.psa, exchange_type=ExchangeType.exchange.value))
    update_user_card(session, id, sold=True)


@router.post(
    "/cards/{id}/grade",
    status_code=status.HTTP_200_OK,
    response_model=UserCardGradeOut
)
async def grade_card(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    user = verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    user_card = verify_user_card(get_user_card_by_id(session, id)) # Check if the user card exists


    # Check if user has enough money
    verify_user_currency(user.money, GRADE_COST)

    update_user(session, data.id, money=user.money-GRADE_COST)

    psa: int =  randint(1,10)
    price: float = user_card.card.price * (1.6 ** (psa - 5))

    # Logs
    grade_cards_logs(session, data.id, user_card, psa, price)

    updated_user_card = update_user_card(session, id, psa=psa, price=int(price))
    return UserCardGradeOut(grade=updated_user_card.psa)


@router.post(
        "/boosters/{id}/open", 
        response_model=BoostedPackOut,
        status_code=status.HTTP_200_OK
)
async def open_boosted_pack(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    user = verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    expansion = verify_expansion(get_expansion_by_id(session, id)) # Check if the expansion exists

    # Check if user has enough money
    verify_user_currency(user.money, expansion.price)

    update_user(session, data.id, money=user.money-expansion.price, opened_boosters=user.opened_boosters+1)    

    # Select radom cards for the booster pack
    booster = choices(get_cards_by_expansion_and_rarity(session, id, Rarity.common), k=5)
    booster += choices(get_cards_by_expansion_and_rarity(session, id, Rarity.uncommon), k=3)
    booster += choices(get_cards_by_expansion_and_rarity(session, id, Rarity.rare), k=1)
    card_rarity: Rarity = choices(RARITY_VARIABLE, weights=PROBABILITIES, k=1)[0]
    booster += choices(get_cards_by_expansion_and_rarity(session, id, card_rarity), k=1)

    # Logs
    log = create_log_history(
        session,
        LogHistoryDB(
            id_user=data.id,
            description=f"Opened boosted pack with id {expansion.id}",
            type=LogType.OPEN_BOOSTER.value,
            money_exchange = -expansion.price
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

    return BoostedPackOut(booster=[CardOut(id=card.id, id_expansion=card.id_expansion, name=card.name, rarity=card.rarity, price=card.price/100, card_number=card.card_number, frontcard=card.frontcard, backcard=card.backcard) for card in booster])