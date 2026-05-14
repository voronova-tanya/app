from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    
    class Config:
        orm_mode = True  

# Author schemas
class AuthorBase(BaseModel):
    name: str
    bio: Optional[str] = None
    birth_year: Optional[int] = Field(None, ge=1800, le=2024)

class AuthorCreate(AuthorBase):
    pass

class AuthorResponse(AuthorBase):
    id: int
    
    class Config:
        orm_mode = True

# Category schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    
    class Config:
        orm_mode = True

# Book schemas
class BookBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = Field(gt=0, description="Price must be greater than 0")
    published_year: Optional[int] = Field(None, ge=1000, le=2024)

class BookCreate(BookBase):
    author_id: int
    category_ids: Optional[List[int]] = []

class BookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    published_year: Optional[int] = Field(None, ge=1000, le=2024)
    author_id: Optional[int] = None
    category_ids: Optional[List[int]] = None

class BookResponse(BookBase):
    id: int
    rating: float
    views: int
    author: AuthorResponse
    categories: List[CategoryResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# Business schemas
class BookRatingRequest(BaseModel):
    rating: float = Field(ge=0, le=5, description="Rating from 0 to 5")

class BookRatingUpdate(BaseModel):
    user_rating: float = Field(ge=0, le=5)

class BookRatingResponse(BaseModel):
    message: str
    book_id: int
    title: str
    new_rating: float
    total_votes: int
    recommendation: str

class BookRecommendation(BaseModel):
    book_id: int
    title: str
    author: str
    rating: float
    views: int
    price: float
    match_score: float
    reasons: List[str]

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None