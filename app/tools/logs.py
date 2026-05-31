from app.db.database import GRADE_COST, Action, LogActivityDB, LogHistoryDB, LogType, create_log_activity, create_log_history


def grade_cards_logs(session, id_user, user_card, psa, price):
    log = create_log_history(
        session,
        LogHistoryDB(
            id_user=id_user,
            description=f"Graded card with id {user_card.id} to PSA {psa} for {GRADE_COST/100}€",
            type=LogType.GRADE.value
        )
    )

    create_log_activity(
            session,
            LogActivityDB(
                id_user=id_user,
                id_card=user_card.id_card,
                id_log_history=log.id,
                action=Action.LOST.value,
                price=user_card.price,
                psa=user_card.psa
            )
    )

    create_log_activity(
            session,
            LogActivityDB(
                id_user=id_user,
                id_card=user_card.id_card,
                id_log_history=log.id,
                action=Action.GET.value,
                price=price,
                psa=psa
            )
    )


def exchange_card_logs(session, user_buyer, user_seller, demanded_card, user_card_offer, data):
    user_buyer_log = create_log_history(
            session,
            LogHistoryDB(
                id_user=user_buyer.id,
                id_user_interacted=user_seller.id,
                description = f"Exchanged card with id {demanded_card.id} for card with id {user_card_offer.id} from user with id {user_seller.id}",
                type = LogType.EXCHANGE.value
            )
        )

    create_log_activity(
        session,
        LogActivityDB(
            id_user=user_buyer.id,
            id_card=user_card_offer.id_card,
            id_log_history=user_buyer_log.id,
            action=Action.GET.value,
            price=user_card_offer.price,
            psa=user_card_offer.psa
        )
    )

    create_log_activity(
        session,
        LogActivityDB(
            id_user=user_buyer.id,
            id_card=demanded_card.id_card,
            id_log_history=user_buyer_log.id,
            action=Action.LOST.value,
            price=demanded_card.price,
            psa=demanded_card.psa
        )
    )

    user_seller_log = create_log_history(
        session,
        LogHistoryDB(
            id_user=user_seller.id,
            id_user_interacted=data.id,
            description = f"Exchanged card with id {user_card_offer.id} for card with id {demanded_card.id} from user with id {data.id}",
            type=LogType.EXCHANGE.value
        )
    )

    create_log_activity(
        session,
        LogActivityDB(
            id_user=user_seller.id,
            id_card=demanded_card.id_card,
            id_log_history=user_seller_log.id,
            action=Action.GET.value,
            price=demanded_card.price,
            psa=demanded_card.psa
        )
    )

    create_log_activity(
        session,
        LogActivityDB(
            id_user=user_seller.id,
            id_card=user_card_offer.id_card,
            id_log_history=user_seller_log.id,
            action=Action.LOST.value,
            price=user_card_offer.price,
            psa=user_card_offer.psa
        )
    )


def buy_card_logs(session, user_buyer, user_seller, user_card_offer, data, offer):
    user_buyer_log = create_log_history(
        session,
        LogHistoryDB(
            id_user=user_buyer.id,
            id_user_interacted=user_seller.id,
            description=f"Bought card with id {user_card_offer.id} from user with id {user_seller.id} for {offer.price/100}€",
            type=LogType.SALE.value,
            money_exchange=-offer.price
        )
    )

    create_log_activity(
        session,
        LogActivityDB(
            id_user=user_buyer.id,
            id_card=user_card_offer.id_card,
            id_log_history=user_buyer_log.id,
            action=Action.GET.value,
            price=user_card_offer.price,
            psa=user_card_offer.psa
        )
    )
        
    user_seller_log = create_log_history(
        session,
        LogHistoryDB(
            id_user=user_seller.id,
            id_user_interacted=data.id,
            description=f"Sold card with id {user_card_offer.id} to user with id {user_buyer.id} for {offer.price/100}€",
            type=LogType.SALE.value,
            money_exchange=offer.price
        )
    )

    create_log_activity(
        session,
        LogActivityDB(
            id_user=user_seller.id,
            id_card=user_card_offer.id_card,
            id_log_history=user_seller_log.id,
            action=Action.LOST.value,
            price=user_card_offer.price,
            psa=user_card_offer.psa
        )
    )