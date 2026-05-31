from fastapi import HTTPException, status
from app.db.database import CardDB, CardMarketDB, ExpansionDB, GenerationDB, UserDB, UserCardDB

# ========================== USER ==========================

def verify_user(user: UserDB) -> UserDB:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
    return user


def verify_user_username(user: UserDB) -> UserDB:
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username {user.username} already exists."
        )
    return user


def verify_user_email(user: UserDB) -> UserDB:
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email {user.email} already exists."
        )
    return user


def verify_user_admin(user_admin: bool):
    if not user_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )


def verify_user_target(user: UserDB) -> UserDB:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user.id} does not exist."
        )
    return user


def verify_user_currency(user_money: int, price: int):
    if user_money < price:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient funds"
        )

# ========================== CARDS ==========================

def verify_card(card: CardDB) -> CardDB:
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with id {card.id} does not exist."
        )
    return card


def verify_card_exists(card: CardDB) -> CardDB:
    if card:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Card with name {card.name} and {card.rarity} already exists in the expansion."
        )
    return card


# ========================== EXPANSIONS ==========================

def verify_expansion(expansion: ExpansionDB) -> ExpansionDB:
    if not expansion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expansion with id {expansion.id} not found."
        )
    return expansion


def verify_expansion_exists(expansion: ExpansionDB) -> ExpansionDB:
    if expansion:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Expansion already exists."
        )
    return expansion

# ========================== GENERATIONS ==========================

def verify_generation(generation: GenerationDB) -> GenerationDB:
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation with id {generation.id} not found."
        )
    return generation


def verify_generation_exists(generation: GenerationDB) -> GenerationDB:
    if generation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Generation alredy exists."
        )
    return generation


# ========================== USER CARD ==========================

def verify_user_card(user_card: UserCardDB) -> UserCardDB:
    if not user_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User card with id {user_card.id} does not exist."
        )
    return user_card


def verify_user_card_target(user_card: UserCardDB) -> UserCardDB:
    if not user_card:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User does not have the demanded card."
            )
    return user_card


def verify_user_card_psa_target(offer_psa: int, demanded_psa: int):
    if offer_psa != demanded_psa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User does not have the demanded card."
            )


def verify_user_card_owner(user_card_id: int, user_id: int):
    if user_card_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
    

def verify_user_card_for_sale(user_card_sold: bool):
    if user_card_sold is True:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User card already for sale."
        )
    
# ========================== MARKET ==========================

def verify_offer(offer: CardMarketDB) -> CardMarketDB:
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Offer with id {id} does not exist."
        )
    return offer
    

def verify_offer_owner(offer_user_id: int, user_id: int):
    if offer_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
    

def verify_offer_self_owner(offer_user_id: int, user_id: int):
    if offer_user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot buy your own offer."
        )