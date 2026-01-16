from app.models import UserIn, UserOut, UserBase

from app.db.database import UserDB, insert_user, get_user_by_username, get_users
from fastapi import APIRouter, status, HTTPException, Header, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.auth import Token, create_access_token, verify_password, get_hash_password, decode_token, oauth2_scheme, TokenData

router = APIRouter(
    prefix="/users",
    tags=["Users"]   
)

@router.post("/singup", status_code = status.HTTP_201_CREATED)
async def create_user(userIn: UserIn):
    userDB = get_user_by_username(userIn.username)
    if userDB:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    try:
        insert_user(UserDB(
            name = userIn.name,
            username = userIn.username,
            password = get_hash_password(userIn.password),
            email = userIn.email,
            money = 0,
            address = userIn.address,
            exchanges = 0
        ))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data entry"
        )


@router.post(
    "/login", 
    response_model = Token,
    status_code = status.HTTP_200_OK
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username: str | None = form_data.username
    password: str | None = form_data.password

    if username is None or password is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username/password incorrect"
        )

    userFound = get_user_by_username(username)

    if not userFound or not verify_password(password, userFound.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username/password incorrect"
        )

    token = create_access_token(
        UserBase(
            username = userFound.username,
            password = userFound.password
        )
    )
    return token


@router.get(
    "/",
    response_model = list[UserOut],
    status_code = status.HTTP_200_OK
)
async def read_all_users(token: str = Depends(oauth2_scheme)):
    
    data: TokenData = decode_token(token)
    
    if not get_user_by_username(data.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )
    
    return [UserOut(id = user.id, name = user.name, username = user.username, exchanges = user.exchanges) for user in get_users()]


@router.get("/{id}", status_code = status.HTTP_200_OK)
async def read_user(id: int, token: str = Depends(oauth2_scheme)):

    data: TokenData = decode_token(token)

    if not get_user_by_username(data.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )

    return [UserOut(id = user.id, name = user.name, username = user.username, exchanges = user.exchanges) for user in get_users() if user.id == id]
