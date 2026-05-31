from app.auth.auth import decode_token, oauth2_scheme, TokenData
from app.tools.verifiers import verify_user, verify_user_admin
from fastapi import APIRouter, status, HTTPException, Depends, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from app.db.database import get_user_by_id, get_session
from os import listdir

router = APIRouter(
    prefix="/media",
    tags=["Media"]   
)

@router.post(
    "/upload", 
    status_code = status.HTTP_201_CREATED, 
)
async def upload_file(file: UploadFile, token: str = Depends(oauth2_scheme), session = Depends(get_session)):
    data: TokenData = decode_token(token)

    # Verifiers
    user = verify_user(get_user_by_id(session, data.id)) # Check if the user exists
    verify_user_admin(user.is_admin) # Check if the user is admin

    if file.filename in listdir("app/static"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="File already exists.",
        )


    with open(f"app/static/{file.filename}", "wb") as f:
        f.write(file.file.read())

    return f"/static/{file.filename}"
