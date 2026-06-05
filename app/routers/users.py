from app.models import CollectionCardOut, CollectionListOut, InventoryCardOut, LogHistoryOut, UserIn, UserListOut, UserOut, EditUser
from app.tools.mappers import history_to_dto
from app.tools.verifiers import verify_expansion, verify_user, verify_user_admin, verify_user_email, verify_user_target, verify_user_username
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page, paginate
from app.auth.auth import Token, create_access_token, verify_password, get_hash_password, decode_token, oauth2_scheme, TokenData
from app.tools.tools import get_formated_user_card
from app.db.database import get_session
from app.db.expansion import get_expansion_by_id
from app.db.user import UserDB, get_user_by_email, get_user_by_id, get_user_by_username, get_users, insert_user, remove_user_by_id, update_user
from app.db.loghistory import get_log_history_by_id, get_log_history_by_user_id


router = APIRouter(
    prefix="/users",
    tags=["Users"]   
)

@router.post("/signup", status_code = status.HTTP_201_CREATED)
async def create_user(userIn: UserIn, session = Depends(get_session)):
    # Verifiers
    verify_user_username(get_user_by_username(session, userIn.username))
    verify_user_email(get_user_by_email(session, userIn.email))

    insert_user(session, UserDB(
            name = userIn.name,
            username = userIn.username,
            password = get_hash_password(userIn.password),
            email = userIn.email,
            money = 0,
            opened_boosters = 0,
            exchanges = 0,
            is_admin = False
        ))


@router.post(
    "/login", 
    response_model = Token,
    status_code = status.HTTP_200_OK
)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session = Depends(get_session)):
    username: str | None = form_data.username
    password: str | None = form_data.password

    # Check if the username and password are provided
    if username is None or password is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username/password incorrect"
        )

    userFound = get_user_by_username(session, username)

    # Check if the user exists and if the password is correct
    if not userFound or not verify_password(password, userFound.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username/password incorrect"
        )

    token = create_access_token(userFound)
    return token


@router.get(
    "/",
    response_model = UserListOut,
    status_code = status.HTTP_200_OK
)
async def read_all_users(token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    
    # Verifiers
    user = verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_user_admin(user.is_admin) # Check if the user is admin
    
    return UserListOut(users=[UserOut(id = user.id, name = user.name, username = user.username, email = user.email, exchanges = user.exchanges, money = user.money/100, opened_boosters = user.opened_boosters, is_admin = user.is_admin) for user in get_users(session)])


@router.get(
        "/{id}", 
        response_model = UserOut, 
        status_code = status.HTTP_200_OK
)
async def read_user(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Check if the user exists and if the user is admin or if the user is the same as the target user
    if not get_user_by_id(session, data.id) or data.id is not id and not data.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )

    user_target = verify_user_target(get_user_by_id(session, id)) # Check if the target user exists
    
    return UserOut(
            id = user_target.id, 
            name = user_target.name, 
            username = user_target.username, 
            email = user_target.email,
            money = user_target.money/100, 
            opened_boosters = user_target.opened_boosters,
            exchanges = user_target.exchanges, 
            is_admin = user_target.is_admin
        )


@router.patch(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=UserOut
)
async def patch_user(id: int, user_data: EditUser, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    user = verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_user_admin(user.is_admin) # Check if the user is admin
    verify_user_target(get_user_by_id(session, id)) # Check if the target user exists

    updated_user = update_user(
        session=session,
        id=id,
        name=user_data.name,
        username=user_data.username,
        email=user_data.email,
        money=int(user_data.money*100) if user_data.money is not None else None,
        opened_boosters=user_data.opened_boosters,
        exchanges=user_data.exchanges,
        is_admin=user_data.is_admin
    )

    return UserOut(
            id = updated_user.id, 
            name = updated_user.name, 
            username = updated_user.username, 
            email = updated_user.email,
            money = updated_user.money/100, 
            opened_boosters = updated_user.opened_boosters,
            exchanges = updated_user.exchanges, 
            is_admin = updated_user.is_admin
        )


@router.delete(
    "/{id}",
    status_code = status.HTTP_200_OK
)
async def delete_user(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    user = verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_user_admin(user.is_admin) # Check if the user is admin
    verify_user_target(get_user_by_id(session, id)) # Check if the target user exists

    remove_user_by_id(session, id)


@router.get(
    "/{id}/inventory",
    response_model = InventoryCardOut,
    status_code = status.HTTP_200_OK
)
async def read_user_cards(id: int, expansion: int | None = None, limit: int = 10, offset: int = 0, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Check if the user exists and if the user is admin or if the user is the same as the target user
    if not get_user_by_id(session, data.id) or data.id is not id and not data.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
    
    # Verifiers
    verify_user_target(get_user_by_id(session, id)) # Check if the target user exists
    verify_expansion(get_expansion_by_id(session, expansion)) # Check if the expansion exists

    return InventoryCardOut(cards=get_formated_user_card(session, id, expansion, limit, offset))


@router.get(
        "/{id}/collection",
        response_model=CollectionListOut,
        status_code=status.HTTP_200_OK
)
async def read_collection(id: int, expansion: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_user_target(get_user_by_id(session, id)) # Check if the target user exists
    verify_expansion(get_expansion_by_id(session, expansion)) # Check if the expansion exists

    return CollectionListOut(
        collection=[
            CollectionCardOut(
                id_card=c.card.id, 
                card_number=c.card.card_number, 
                card_name=c.card.name, 
                quantity=len(c.user_cards), 
                frontcard=c.card.frontcard) 
                for c in get_formated_user_card(session, id, expansion, -1, -1)
            ]
    )


@router.get(
    "/{id}/logs",
    status_code=status.HTTP_200_OK,
    response_model=Page[LogHistoryOut]
)
async def read_user_logs(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    verify_user_target(get_user_by_id(session, id)) # Check if the target user exists
    verify_user_admin(data.is_admin) # Check if the user is admin

    return paginate([history_to_dto(log) for log in get_log_history_by_user_id(session, id)])


@router.get(
    "/{id}/logs/{log_id}",
    status_code=status.HTTP_200_OK
)
async def read_user_logs(id: int, log_id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    verify_user_target(get_user_by_id(session, id)) # Check if the target user exists
    verify_user_admin(data.is_admin) # Check if the user is admin

    return history_to_dto(get_log_history_by_id(session, log_id))