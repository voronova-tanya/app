from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud, auth
from app.database import get_db

router = APIRouter(prefix="/authors", tags=["authors"])

@router.post("/", response_model=schemas.AuthorResponse, status_code=status.HTTP_201_CREATED)
def create_author(
    author: schemas.AuthorCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    return crud.create_author(db=db, author=author)

@router.get("/", response_model=List[schemas.AuthorResponse])
def read_authors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    authors = crud.get_authors(db, skip=skip, limit=limit)
    return authors

@router.get("/{author_id}", response_model=schemas.AuthorResponse)
def read_author(author_id: int, db: Session = Depends(get_db)):
    db_author = crud.get_author(db, author_id)
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return db_author

@router.put("/{author_id}", response_model=schemas.AuthorResponse)
def update_author(
    author_id: int,
    author: schemas.AuthorCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    updated_author = crud.update_author(db, author_id, author)
    if not updated_author:
        raise HTTPException(status_code=404, detail="Author not found")
    return updated_author

@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(
    author_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    if not crud.delete_author(db, author_id):
        raise HTTPException(status_code=404, detail="Author not found")
    return None