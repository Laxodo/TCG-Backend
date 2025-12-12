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
# TODO: terminar los que quedan
# =============== GENERATION ===============



# =============== USER_CARD ===============



# =============== TRANSACTION ===============



# =============== TRADE ===============


