from app.db.database import get_user_cards, get_user_cards_by_expansion
from app.models import CardOut, UserCardListOut, UserCardOut

def get_formated_user_card(session, id: int, expansion: int | None, limit: int, offset: int):
    user_card_dict: dict[int, UserCardListOut] = {}
    user_cards, cards = get_user_cards(session, id, limit, offset) if expansion is None else get_user_cards_by_expansion(session, id, expansion, limit, offset)

    for card in cards:
        card_out: CardOut = CardOut(
                id = card.id,
                id_expansion = card.id_expansion,
                name = card.name,
                rarity = card.rarity,
                price = card.price/100,
                card_number = card.card_number,
                frontcard = card.frontcard,
                backcard = card.backcard
            )
        user_card_dict[card.id] = UserCardListOut(card=card_out, user_cards=[])

    for user_card in user_cards:
        user_card = UserCardOut(
                id = user_card.id,
                id_user = user_card.id_user,
                id_card = user_card.id_card,
                price = user_card.price/100,
                psa = user_card.psa,
                sold = user_card.sold
            )
        user_card_dict[user_card.id_card].user_cards.append(user_card)
    return user_card_dict.values()
