from pydantic import BaseModel

#=============== USER ===============
class UserBase(BaseModel):
    username: str
    password: str


class UserIn(UserBase):
    name: str
    email: str
    money: float
    address: str


class UserOut(BaseModel):
    id: int
    name : str
    username : str
    exchanges : int 


class UserLoginIn(UserBase):
    pass

# =============== CARD ===============
class CardBase(BaseModel):
    id_expansion: int
    name: str
    rarity: str
    frontcard: str
    backcard: str


class CardOut(CardBase):
    id: int

# =============== EXPANSION ===============
class ExpansionBase(BaseModel):
    id_generacion: int
    name: str
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
class CardUserBase(BaseModel):
    id_user: int
    id_card: int
    psa: float
    sold: bool
    price: float


class CardUserOut(CardUserBase):
    id: int
# TODO: terminar los que quedan
# =============== USER_CARD ===============



# =============== TRANSACTION ===============



# =============== TRADE ===============


