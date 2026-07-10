from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import UserCreate
from database import get_db
from sqlalchemy import text
from auth import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
   # 1. check email
    result = await db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": payload.email})
    if result.mappings().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. insert — THIS IS MISSING
    result = await db.execute(
        text("INSERT INTO users (email, password) VALUES (:email, :password)"),
        {"email": payload.email, "password": hash_password(payload.password)}
    )
    await db.commit()

    # 3. fetch and return
    result = await db.execute(text("SELECT * FROM users WHERE id = :id"), {"id": result.lastrowid})
    return result.mappings().first()


@router.post("/login")
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),  # 👈 form data not JSON
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        text("SELECT * FROM users WHERE email = :email"),
        {"email": form_data.username}    # 👈 .username not .email
    )
    user = result.mappings().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"user_id": user["id"]})
    return {"access_token": token, "token_type": "bearer"}
