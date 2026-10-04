from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# ── Auth ──────────────────────────────────────────
class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    name: str
    email: str
    userType: str

class TokenResponse(BaseModel):
    token: str
    user: UserOut

# ── Cart ──────────────────────────────────────────
class CartItemIn(BaseModel):
    productId: str
    title: str
    price: float
    image: str = ""
    quantity: int = 1

class CartItemOut(BaseModel):
    id: str
    productId: str
    title: str
    price: float
    image: str
    quantity: int

class CartOut(BaseModel):
    items: List[CartItemOut]

class UpdateQuantity(BaseModel):
    quantity: int

# ── Wishlist ──────────────────────────────────────
class WishlistItemIn(BaseModel):
    productId: str
    title: str
    price: float
    image: str = ""

class WishlistItemOut(BaseModel):
    id: str
    productId: str
    title: str
    price: float
    image: str

class WishlistOut(BaseModel):
    items: List[WishlistItemOut]

# ── Products ──────────────────────────────────────
class ProductOut(BaseModel):
    id: str
    title: str
    description: str
    price: float
    category: str
    image: str
    stock: int
    artisanName: Optional[str] = None
    artisanId: Optional[str] = None

class ProductsOut(BaseModel):
    products: List[ProductOut]

# ── Notes ─────────────────────────────────────────
class NoteIn(BaseModel):
    note: str

class NoteOut(BaseModel):
    note: str

# ── Payment ───────────────────────────────────────
class PaymentIn(BaseModel):
    itemIds: List[str]

class PaymentOut(BaseModel):
    success: bool
    message: str