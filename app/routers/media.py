from app.auth.auth import decode_token, oauth2_scheme, TokenData
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

    # Check if the user exists and if the user is admin
    if not get_user_by_id(session, data.id) or not data.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )

    if file.filename in listdir("app/static"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="File already exists.",
        )


    with open(f"app/static/{file.filename}", "wb") as f:
        f.write(file.file.read())

    return f"/static/{file.filename}"
