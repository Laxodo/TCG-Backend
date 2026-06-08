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


class UserListOut(BaseModel):
    users: list[UserOut]


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


class CardListOut(BaseModel):
    cards: list[CardOut]


# =============== EXPANSION ===============
class ExpansionBase(BaseModel):
    id_generacion: int
    name: str
    price: float
    year: int


class ExpansionOut(ExpansionBase):
    id: int


class ExpansionListOut(BaseModel):
    expansions: list[ExpansionOut]


# =============== GENERATION ===============
class GenerationBase(BaseModel):
    name: str
    year: int


class GenerationOut(GenerationBase):
    id: int


class GenerationListOut(BaseModel):
    generations: list[GenerationOut]


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


class InventoryCardOut(BaseModel):
    cards: list[UserCardListOut]


class CollectionCardOut(BaseModel):
    id_card: int
    card_number: int
    card_name: str
    quantity: int
    frontcard: str


class CollectionListOut(BaseModel):
    collection: list[CollectionCardOut]


class UserCardGradeOut(BaseModel):
    grade: int


# =============== MARKET ===============
class QuickSellOut(BaseModel):
    total_earn: float


class QuickSellIn(BaseModel):
    card_list_id: list[int]


class SellIn(BaseModel):
    price: float


class ExchangeIn(BaseModel):
    id_card: int
    psa: int | None


class OfferOut(BaseModel):
    id: int
    id_card: int | None
    id_user_card: int
    exchange_type: str
    image_card_offer: str
    image_card_demanded: str | None
    expansion_name: str
    price: float | None
    psa: int | None


class OfferListOut(BaseModel):
    offers: list[OfferOut]


class BoostedPackOut(BaseModel):
    booster: list[CardOut]


# =============== LOGACTIVITY ===============
class LogActivityCardOut(BaseModel):
    id: int
    name: str
    price: float
    frontcard: str


class LogActivityOut(BaseModel):
    id_user: int
    card: LogActivityCardOut | None
    id_log_history: int
    action: str
    price: float
    psa: int | None


# =============== LOGHISTORY ===============
class LogHistoryUserOut(BaseModel):
    id: int
    username: str
    is_admin: bool


class LogHistoryOut(BaseModel):
    user: LogHistoryUserOut
    user_interacted: LogHistoryUserOut | None
    description: str
    type: str
    money_exchange: int
    date: str
    activities: list[LogActivityOut]


class LogHistoryListOut(BaseModel):
    logs: list[LogHistoryOut]