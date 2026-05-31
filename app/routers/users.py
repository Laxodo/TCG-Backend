from app.models import CollectionCardOut, UserIn, UserOut, UserCardListOut, EditUser
from app.tools.verifiers import verify_expansion, verify_user, verify_user_admin, verify_user_email, verify_user_target, verify_user_username
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.auth import Token, create_access_token, verify_password, get_hash_password, decode_token, oauth2_scheme, TokenData
from app.tools.tools import get_formated_user_card
from app.db.database import (
    UserDB,
    get_expansion_by_id,
    get_user_by_email, 
    insert_user,
    get_session,
    get_user_by_username, 
    get_user_by_id, 
    get_users, 
    update_user,
    remove_user_by_id
)

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
    response_model = list[UserOut],
    status_code = status.HTTP_200_OK
)
async def read_all_users(token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    
    # Verifiers
    user = verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_user_admin(user.is_admin) # Check if the user is admin
    
    return [UserOut(id = user.id, name = user.name, username = user.username, email = user.email, exchanges = user.exchanges, money = user.money/100, opened_boosters = user.opened_boosters, is_admin = user.is_admin) for user in get_users(session)]


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
async def patch_user(id: int, user: EditUser, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    user = verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_user_admin(user.is_admin) # Check if the user is admin
    verify_user_target(get_user_by_id(session, id)) # Check if the target user exists

    user.money = int(user.money*100) if user.money is not None else user.money
    updated_user = update_user(session, id, **user.model_dump())

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
    response_model = list[UserCardListOut],
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

    return get_formated_user_card(session, id, expansion, limit, offset)


@router.get(
        "/{id}/collection",
        response_model=list[CollectionCardOut],
        status_code=status.HTTP_200_OK
)
async def read_collection(id: int, expansion: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_user_target(get_user_by_id(session, id)) # Check if the target user exists
    verify_expansion(get_expansion_by_id(session, expansion)) # Check if the expansion exists

    collection_card_list: list[CollectionCardOut] = []

    for card_list in get_formated_user_card(session, id, expansion, -1, -1):
        collection_card_list.append(
                CollectionCardOut(
                        id_card=card_list.card.id,
                        card_number=card_list.card.card_number,
                        card_name=card_list.card.name,
                        quantity=len(card_list.user_cards),
                        frontcard=card_list.card.frontcard,
                    )
            )

    return collection_card_list
