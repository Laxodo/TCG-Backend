from pydantic import BaseModel

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


class EditUser(BaseModel):
    name: str | None
    username: str | None
    email: str | None
    money: float | None
    opened_boosters: int | None
    exchanges: int | None
    is_admin: bool | None


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


class UserCardGradeOut(BaseModel):
    grade: int

# =============== MARKET ===============

class QuickSellOut(BaseModel):
    total_earn: float


class QuickSellIn(BaseModel):
    card_list_id: list[int]


class SellIn(BaseModel):
    price: float


class OfferOut(BaseModel):
    id: int
    id_user_card: int
    exchange_type: str
    price: float
    id_card: int
    psa: int | None

# =============== LOGACTIVITY ===============

class LogActivityOut(BaseModel):
    id_user: int
    id_card: int
    id_log_history: int
    action: str
    price: int
    psa: int | None


# =============== LOGHISTORY ===============

class LogHistoryOut(BaseModel):
    id_user: int
    id_card: int
    action: str
    price: int
    psa: int | None