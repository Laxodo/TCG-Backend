from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/users",
    tags=["Users"]   
)


class UserBase(BaseModel):
    username: str
    password: str


class UserIn(UserBase):
    name: str
    email: str
    money: float
    address: str
    exchanges: int


class UserDB(UserIn):
    id: int


class UserLoginIn(UserBase):
    pass


class TokenOut(BaseModel):
    token: str

users: list[UserDB] = []

@router.post("/singup", status_code = status.HTTP_201_CREATED)
async def create_user(userIn: UserIn):
    userFound = [u for u in users if u.username == userIn.username]
    if len(userFound) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    users.append(
        UserDB(
            id= len(users) + 1, 
            name = userIn.name, 
            username = userIn.username, 
            password = userIn.password,
            email = userIn.email,
            money = userIn.money,
            address = userIn.address,
            exchanges = userIn.exchanges
        )
    )


@router.post(
    "/login", 
    response_model = TokenOut,
    status_code = status.HTTP_200_OK
)
async def login_user(userLogin: UserLoginIn):
    userFound = [u for u in users if u.username == userLogin.username]
    user = userFound[0]
    if not userFound or userLogin.password != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username/password incorrect"
        )
    return TokenOut(
        token=f"mytoken:{user.id}-{user.username}"
    )


@router.get("/users", status_code = status.HTTP_200_OK)
async def get_users():
    lista = []
    for user in users:
        lista.append({
            "id" : user.id,
            "name" : user.name,
            "username" : user.username,
            "exchanges" : user.exchanges
        })
    return lista


@router.get("/{id}", status_code = status.HTTP_200_OK)
async def get_user_by_id(id: int):
    for user in users:
        if user.id == id:
            return {
                "id" : user.id,
                "name" : user.name,
                "username" : user.username,
                "exchanges" : user.exchanges
            }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User {id} does not exists"
    )
