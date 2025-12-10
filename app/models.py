from pydantic import BaseModel

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

