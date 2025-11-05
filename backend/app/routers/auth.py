# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core import models, schemas
from app.utils import security
from app.core.database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# ✅ USER REGISTER
@router.post(
    "/register",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_input: schemas.UserCreate = Body(...),
    db: AsyncSession = Depends(get_db)
):
    # 1. Kullanıcı email/username eşleşmesi var mı?
    query = select(models.User).where(
        (models.User.email == user_input.email) |
        (models.User.username == user_input.username)
    )
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email veya kullanıcı adı zaten kullanımda"
        )

    # 2. Şifreyi hashle
    hashed_password = security.create_hashed_password(user_input.password)

    # 3. Yeni kullanıcı oluştur
    new_user = models.User(
        username=user_input.username,
        email=user_input.email,
        password=hashed_password,   # ✅ DÜZELTİLDİ
    )

    # 4. Kaydet
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


# ✅ USER LOGIN
@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # 1. Kullanıcıyı bul
    query = select(models.User).where(models.User.username == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    # 2. Kullanıcı yoksa veya şifre yanlışsa
    if not user or not security.verify_password(form_data.password, user.password):  # ✅ DÜZELTİLDİ
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 3. JWT oluştur
    access_token = security.create_access_token(
        data={"sub": user.username}
    )

    return {"access_token": access_token, "token_type": "bearer"}
