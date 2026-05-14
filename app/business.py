from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas
import math
from typing import List

def update_book_rating(db: Session, book_id: int, user_rating: float) -> schemas.BookRatingResponse:
    """
    Обновление рейтинга книги с использованием взвешенного алгоритма.
    Используется формула Байесовского среднего.
    """
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        return None
    

    total_votes = book.views if book.views > 0 else 1
    

    global_avg = db.query(func.avg(models.Book.rating)).scalar() or 3.0
    m = 5  
    old_rating = book.rating
    new_total_votes = total_votes + 1
    new_rating = (old_rating * total_votes + user_rating) / new_total_votes
    
    # Применяем байесовское сглаживание
    bayesian_rating = (new_total_votes * new_rating + m * global_avg) / (new_total_votes + m)
    
    book.rating = round(bayesian_rating, 2)
    db.commit()
    db.refresh(book)
    
    # Генерируем рекомендацию на основе нового рейтинга
    recommendation = ""
    if book.rating >= 4.5:
        recommendation = "Рекомендуется к обязательному прочтению!"
    elif book.rating >= 4.0:
        recommendation = "Отличная книга! Очень рекомендуется."
    elif book.rating >= 3.5:
        recommendation = "Хорошая книга, достойна внимания."
    elif book.rating >= 3.0:
        recommendation = " Средняя оценка. На любителя."
    else:
        recommendation = "Книга получила низкие оценки."
    
    return schemas.BookRatingResponse(
        message="Rating updated successfully",
        book_id=book.id,
        title=book.title,
        new_rating=book.rating,
        total_votes=new_total_votes,
        recommendation=recommendation
    )

def get_similar_books(db: Session, book_id: int, limit: int = 5) -> List[schemas.BookRecommendation]:
    """
    Алгоритм поиска похожих книг на основе:
    1. Общих категорий (вес 40%)
    2. Рейтинга (вес 30%)
    3. Года публикации (вес 20%)
    4. Количества просмотров (вес 10%)
    """
    target_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not target_book:
        return []
    
    all_books = db.query(models.Book).filter(models.Book.id != book_id).all()
    
    recommendations = []
    
    for book in all_books:
        score = 0
        reasons = []
        
        
        target_cats = set([cat.id for cat in target_book.categories])
        book_cats = set([cat.id for cat in book.categories])
        common_cats = target_cats.intersection(book_cats)
        
        if target_cats:
            category_score = len(common_cats) / len(target_cats)
            score += category_score * 0.4
            if common_cats:
                reasons.append(f"Общие категории ({len(common_cats)} совпадений)")
        
       
        rating_diff = 1 - abs(target_book.rating - book.rating) / 5
        score += rating_diff * 0.3
        if abs(target_book.rating - book.rating) < 1:
            reasons.append(f"Похожий рейтинг ({book.rating})")
        
       
        if target_book.published_year and book.published_year:
            year_diff = 1 - min(abs(target_book.published_year - book.published_year) / 100, 1)
            score += year_diff * 0.2
            if year_diff > 0.8:
                reasons.append(f"Близкий год публикации ({book.published_year})")
        
        
        max_views = db.query(func.max(models.Book.views)).scalar() or 1
        popularity_score = min(book.views / max_views, 1)
        score += popularity_score * 0.1
        if popularity_score > 0.7:
            reasons.append(f"Популярная книга ({book.views} просмотров)")
        
        
        if score > 0.3:
            recommendations.append(schemas.BookRecommendation(
                book_id=book.id,
                title=book.title,
                author=book.author.name,
                rating=book.rating,
                views=book.views,
                price=book.price,
                match_score=round(score * 100, 2),
                reasons=reasons[:3]  # Берем топ-3 причины
            ))
    
    
    recommendations.sort(key=lambda x: x.match_score, reverse=True)
    return recommendations[:limit]

def get_top_rated_books(db: Session, limit: int = 10, min_views: int = 1):
    """
    Получение топ книг с использованием алгоритма ранжирования.
    Использует комбинацию рейтинга и просмотров для справедливой оценки.
    """
    books = db.query(models.Book).filter(models.Book.views >= min_views).all()
    
    # Вычисляем доверительный интервал (нижнюю границу) для рейтинга
    # Используем формулу Wilson score для биномиальной пропорции
    scored_books = []
    for book in books:
        # Нормализуем рейтинг от 0 до 1
        rating_norm = book.rating / 5.0
        n = max(book.views, 1)
        
        # Wilson score с z=1.96 (95% доверительный интервал)
        z = 1.96
        p = rating_norm
        denominator = 1 + z*z/n
        centre = p + z*z/(2*n)
        error = z * math.sqrt((p*(1-p) + z*z/(4*n))/n)
        lower_bound = (centre - error) / denominator
        
        # Комбинируем нижнюю границу с популярностью
        final_score = lower_bound * (0.7 + 0.3 * min(n/100, 1))
        
        scored_books.append((final_score, book))
    
    
    scored_books.sort(key=lambda x: x[0], reverse=True)
    return [book for _, book in scored_books[:limit]]