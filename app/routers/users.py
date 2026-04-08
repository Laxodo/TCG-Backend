from app.models import UserIn, UserOut, UserBase
from app.db.database import UserDB, insert_user, get_user_by_username, get_user_by_id, get_users, remove_user_by_id
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
    if userDB is not None:
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
            opened_boosters = 0,
            exchanges = 0,
            is_admin = False
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

    token = create_access_token(userFound)
    return token


@router.get(
    "/",
    response_model = list[UserOut],
    status_code = status.HTTP_200_OK
)
async def read_all_users(token: str = Depends(oauth2_scheme)):
    
    data: TokenData = decode_token(token)
    
    if not get_user_by_id(data.id) or not data.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )
    
    return [UserOut(id = user.id, name = user.name, username = user.username, email = user.email, exchanges = user.exchanges, money = user.money, opened_boosters = user.opened_boosters, is_admin = user.is_admin) for user in get_users()]


@router.get("/{id}", status_code = status.HTTP_200_OK)
async def read_user(id: int, token: str = Depends(oauth2_scheme)):

    data: TokenData = decode_token(token)

    user = get_user_by_id(data.id)

    if not user or not data.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )

    user_target = get_user_by_id(id)
    if not user_target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} does not exist",
        )
        
    return UserOut(
            id = user_target.id, 
            name = user_target.name, 
            username = user_target.username, 
            email = user_target.email,
            money = user_target.money, 
            opened_boosters = user_target.opened_boosters,
            exchanges = user_target.exchanges, 
            is_admin = user_target.is_admin
        )


@router.delete(
    "/{id}",
    status_code = status.HTTP_200_OK
)
async def delete_user(id: int, token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)
    if not get_user_by_id(data.id) or not data.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )
    remove_user_by_id(id)
