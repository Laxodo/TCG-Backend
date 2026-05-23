from app.models import CollectionCardOut, UserIn, UserOut, UserBase, CardOut, UserCardOut, UserCardListOut
from fastapi import APIRouter, status, HTTPException, Header, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.auth import Token, create_access_token, verify_password, get_hash_password, decode_token, oauth2_scheme, TokenData
from app.tools.tools import get_formated_user_card
from app.db.database import (
    UserDB,
    get_expansion_by_id, 
    insert_user,
    get_session,
    get_user_by_username, 
    get_user_by_id, 
    get_users, 
    update_user,
    remove_user_by_id,
    get_user_cards,
    get_user_cards_by_expansion,
    get_card_by_id,
    remove_card
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]   
)

@router.post("/singup", status_code = status.HTTP_201_CREATED)
async def create_user(userIn: UserIn, session = Depends(get_session)):
    # Check if the username is already taken
    if get_user_by_username(session, userIn.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    try:
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
    
    # Check if the user exists and if the user is admin
    if not get_user_by_id(session, data.id) or not data.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )
    
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

    user_target = get_user_by_id(session, id)

    # Check if the target user exists
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
            money = user_target.money/100, 
            opened_boosters = user_target.opened_boosters,
            exchanges = user_target.exchanges, 
            is_admin = user_target.is_admin
        )


@router.delete(
    "/{id}",
    status_code = status.HTTP_200_OK
)
async def delete_user(id: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)
    # Check if the user exists and if the user is admin
    if not get_user_by_id(session, data.id) or not data.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )
    
    # Check if the target user exists
    if not get_user_by_id(session, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} does not exist",
        )

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
    
    # Check if the target user exists
    if not get_user_by_id(session, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} does not exist",
        )
    
    # Check if the expansion exists
    if not get_expansion_by_id(session, expansion):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expansion not found."
        )

    return get_formated_user_card(session, id, expansion, limit, offset)


@router.post(
    "/inventory/quick-sell",
    status_code=status.HTTP_200_OK
)
async def quick_sell_cards(cards: list[int], token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Check if the user exists
    if not get_user_by_id(session, data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )
   
    user = get_user_by_id(session, data.id)

    total_earn = sum([remove_card(session, c).price for c in cards if not get_card_by_id(session, c)])
    update_user(session=session, id=data.id, money=user.money+total_earn)


@router.get(
        "/{id}/collection",
        response_model=list[CollectionCardOut],
        status_code=status.HTTP_200_OK
)
async def read_collection(id: int, expansion: int, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Check if the user exists
    if not get_user_by_id(session, data.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    # Check if the targeted user exists
    if not get_user_by_id(session, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} does not exist."
        )

    # Check if the expansion exists
    if not get_expansion_by_id(session, expansion):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expansion not found."
        )

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
