from pydantic import BaseModel
#TODO: implementar los dto para devolver la informacion para no devolver objetos de la base de datos

#=============== USER ===============
class UserBase(BaseModel):
    username: str
    password: str


class UserIn(UserBase):
    name: str
    email: str


class UserOut(BaseModel):
    id: int
    name: str
    username: str
    email: str
    money: float
    opened_boosters: int
    exchanges: int
    is_admin: bool


class UserLoginIn(UserBase):
    pass

# =============== CARD ===============
class CardBase(BaseModel):
    id_expansion: int
    name: str
    rarity: str
    price: float
    card_number: int
    frontcard: str
    backcard: str


class CardOut(CardBase):
    id: int

# =============== EXPANSION ===============
class ExpansionBase(BaseModel):
    id_generacion: int
    name: str
    price: float
    year: int


class ExpansionOut(ExpansionBase):
    id: int

# =============== GENERATION ===============
class GenerationBase(BaseModel):
    name: str
    year: int


class GenerationOut(GenerationBase):
    id: int

# =============== USER_CARD ===============
class UserCardOut(BaseModel):
    id: int
    id_user: int
    id_card: int
    price: float
    psa: int | None
    sold: bool


class UserCardListOut(BaseModel):
    card: CardOut
    user_cards: list[UserCardOut]


class CollectionCardOut(BaseModel):
    id_card: int
    card_number: int
    card_name: str
    quantity: int
    frontcard: str


# TODO: terminar los que quedan
# =============== TRANSACTION ===============



# =============== TRADE ===============


