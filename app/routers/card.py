from typing import Optional
from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/cards",
    tags=["Cards"]
)

class CardDB(BaseModel):
    id: int
    name: str
    price: float
    psa: float
    rare: str
    frontcard: Optional[str]
    backcard: Optional[str]
    offert: bool

class CardIn(BaseModel):
    name: str
    price: float
    psa: float
    rare: str
    frontcard: Optional[str] = None
    backcard: Optional[str] = None
    offert: bool

cards: list[CardDB] = []

@router.post("/", status_code = status.HTTP_201_CREATED)
async def create_card(CardIn: CardIn):
    cards.append(
        CardDB(
            id = len(cards) + 1,
            name = CardIn.name,
            price = CardIn.price,
            psa = CardIn.psa,
            rare = CardIn.rare,
            frontcard = CardIn.frontcard,
            backcard = CardIn.backcard,
            offert = CardIn.offert
        )
    )

@router.get("/", status_code = status.HTTP_200_OK)
async def get_cards():
    lista = []
    for card in cards:
        lista.append(
            {
                "id": card.id,
                "name": card.name,
                "price": card.price,
                "psa": card.psa,
                "rare": card.rare,
                "offert": card.offert
            }
        )
    return lista

@router.get("/{id}", status_code = status.HTTP_200_OK)
async def get_card_by_id(id: int):
    for card in cards:
        if card.id == id:
            return {
                "id": card.id,
                "name": card.name,
                "price": card.price,
                "psa": card.psa,
                "rare": card.rare,
                "offert": card.offert
            }
            
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = f"La carta con el id {id} no existe"
    )

@router.delete("/{id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_card_by_id(id: int):
    cardFound = [c for c in cards if c.id == id]
    if not cardFound:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"La carta con el id {id} no existe"
        )
    
    cards.remove(cardFound[0])
    return {f"La carta con el id {id} se ha eliminado correctamente"}
