from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from config import get_database
from schemas import UserSignup, UserLogin, TokenResponse, UserOut
from auth_utils import hash_password, verify_password, create_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

def fmt_user(u) -> UserOut:
    return UserOut(id=str(u["_id"]), name=u["name"], email=u["email"], userType=u["userType"])

async def create_user(body, user_type, db):
    if await db["users"].find_one({"email": body.email}):
        raise HTTPException(400, "Email already registered")
    doc = {
        "name": body.name, "email": body.email,
        "password": hash_password(body.password), "userType": user_type
    }
    result = await db["users"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return TokenResponse(token=create_token(str(result.inserted_id)), user=fmt_user(doc))

@router.post("/signup", response_model=TokenResponse)
async def signup(body: UserSignup, db=Depends(get_database)):
    return await create_user(body, "customer", db)

@router.post("/artisan-signup", response_model=TokenResponse)
async def artisan_signup(body: UserSignup, db=Depends(get_database)):
    return await create_user(body, "artisan", db)

@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin, db=Depends(get_database)):
    user = await db["users"].find_one({"email": body.email})
    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(401, "Invalid credentials")
    return TokenResponse(token=create_token(str(user["_id"])), user=fmt_user(user))

@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return {"user": fmt_user(current_user)}

@router.post("/logout")
async def logout(current_user=Depends(get_current_user)):
    return {"message": "Logged out successfully"}