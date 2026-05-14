from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, crud, auth, business
from app.database import get_db

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    
    author = crud.get_author(db, book.author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    return crud.create_book(db=db, book=book, owner_id=current_user.id)

@router.get("/", response_model=List[schemas.BookResponse])
def read_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    books = crud.get_books(db, skip=skip, limit=limit)
    return books

@router.get("/{book_id}", response_model=schemas.BookResponse)
def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.get_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    
    db_book.views += 1
    db.commit()
    db.refresh(db_book)
    
    return db_book

@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int,
    book_update: schemas.BookUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    db_book = crud.get_book(db, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    
    if db_book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    updated_book = crud.update_book(db, book_id, book_update)
    return updated_book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    db_book = crud.get_book(db, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    
    if db_book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    crud.delete_book(db, book_id)
    return None

@router.post("/{book_id}/rate", response_model=schemas.BookRatingResponse)
def rate_book(
    book_id: int,
    rating_data: schemas.BookRatingUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):

    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    result = business.update_book_rating(db, book_id, rating_data.user_rating)
    return result

@router.get("/{book_id}/similar", response_model=List[schemas.BookRecommendation])
def get_similar_books(
    book_id: int,
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db)
):

    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    recommendations = business.get_similar_books(db, book_id, limit)
    return recommendations

@router.get("/top/rated", response_model=List[schemas.BookResponse])
def get_top_rated_books(
    limit: int = Query(10, ge=1, le=50),
    min_views: int = Query(1, ge=0),
    db: Session = Depends(get_db)
):

    top_books = business.get_top_rated_books(db, limit, min_views)
    return top_books