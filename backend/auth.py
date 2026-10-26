import uuid
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import EmailStr
from config import get_database
from schemas import UserSignup, UserLogin, TokenResponse, UserOut
from auth_utils import hash_password, verify_password, create_token, get_current_user
from pathlib import Path

router = APIRouter(prefix="/auth", tags=["Auth"])
ARTISAN_UPLOAD_DIR = Path("uploads") / "artisans"
MAX_ARTISAN_PHOTO_BYTES = 5 * 1024 * 1024
ARTISAN_PHOTO_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

def fmt_user(u) -> UserOut:
    return UserOut(
        id=str(u["_id"]),
        name=u["name"],
        email=u["email"],
        userType=u["userType"],
        location=u.get("location"),
        experience=u.get("experience"),
        craft=u.get("craft"),
        profilePhoto=u.get("profilePhoto"),
    )

async def create_user(body, user_type, db, artisan_details=None):
    if await db["users"].find_one({"email": body.email}):
        raise HTTPException(400, "Email already registered")
    doc = {
        "name": body.name, "email": body.email,
        "password": hash_password(body.password), "userType": user_type
    }
    if artisan_details:
        doc.update(artisan_details)
    result = await db["users"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return TokenResponse(token=create_token(str(result.inserted_id)), user=fmt_user(doc))

async def save_artisan_photo(photo: UploadFile) -> str:
    extension = ARTISAN_PHOTO_TYPES.get(photo.content_type or "")
    if not extension:
        raise HTTPException(400, "Upload an artisan photo in JPG, PNG, or WEBP format.")

    photo_bytes = await photo.read(MAX_ARTISAN_PHOTO_BYTES + 1)
    if not photo_bytes:
        raise HTTPException(400, "The artisan photo cannot be empty.")
    if len(photo_bytes) > MAX_ARTISAN_PHOTO_BYTES:
        raise HTTPException(413, "The artisan photo must be 5 MB or smaller.")

    filename = f"{uuid.uuid4().hex}{extension}"
    destination = ARTISAN_UPLOAD_DIR / filename
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(photo_bytes)
    except OSError as error:
        raise HTTPException(500, "Could not save the artisan photo.") from error
    return f"/uploads/artisans/{filename}"

@router.post("/signup", response_model=TokenResponse)
async def signup(body: UserSignup, db=Depends(get_database)):
    return await create_user(body, "customer", db)

@router.post("/artisan-signup", response_model=TokenResponse)
async def artisan_signup(
    name: str = Form(..., min_length=1, max_length=100),
    email: EmailStr = Form(...),
    password: str = Form(..., min_length=8, max_length=128),
    location: str = Form(..., min_length=2, max_length=120),
    experience: int = Form(..., ge=0, le=80),
    craft: str = Form(..., min_length=2, max_length=120),
    profile_photo: UploadFile = File(...),
    db=Depends(get_database),
):
    body = UserSignup(name=name.strip(), email=email.strip(), password=password)
    if await db["users"].find_one({"email": body.email}):
        raise HTTPException(400, "Email already registered")
    profile_photo_url = await save_artisan_photo(profile_photo)
    return await create_user(
        body,
        "artisan",
        db,
        {
            "location": location.strip(),
            "experience": experience,
            "craft": craft.strip(),
            "profilePhoto": profile_photo_url,
        },
    )

@router.get("/artisans")
async def get_artisan_profiles(db=Depends(get_database)):
    users = await db["users"].find({"userType": "artisan"}).to_list(1000)
    return {
        "artisans": [
            {
                "id": str(user["_id"]),
                "name": user["name"],
                "location": user.get("location", ""),
                "experience": user.get("experience", 0),
                "craft": user.get("craft", ""),
                "profilePhoto": user.get("profilePhoto", ""),
            }
            for user in users
            if user.get("profilePhoto")
        ]
    }

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