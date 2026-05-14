from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, books, authors, categories


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Book Catalog API",
    description="REST API для управления каталогом книг с рекомендательной системой",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(books.router)
app.include_router(authors.router)
app.include_router(categories.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to Book Catalog API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}