@echo off
chcp 65001 >nul
echo ========================================
echo   Book Catalog API - Demonstration
echo ========================================
echo.

echo [1] Register user...
curl -X POST "http://localhost:8000/auth/register" -H "Content-Type: application/json" -d "{\"username\":\"demo\",\"email\":\"demo@mail.com\",\"password\":\"123\"}"
echo.
echo.

echo [2] Get token...
curl -X POST "http://localhost:8000/auth/token" -H "Content-Type: application/x-www-form-urlencoded" -d "username=demo&password=123"
echo.
echo.
echo IMPORTANT: Copy token from above and set it:
echo set TOKEN=your_token_here
echo.
pause
echo.

echo [3] Create author - Lev Tolstoy...
curl -X POST "http://localhost:8000/authors/" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"name\":\"Lev Tolstoy\",\"bio\":\"Russian writer\",\"birth_year\":1828}"
echo.
echo.

echo [4] Create author - Fyodor Dostoevsky...
curl -X POST "http://localhost:8000/authors/" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"name\":\"Fyodor Dostoevsky\",\"bio\":\"Russian novelist\",\"birth_year\":1821}"
echo.
echo.

echo [5] Create author - George Orwell...
curl -X POST "http://localhost:8000/authors/" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"name\":\"George Orwell\",\"bio\":\"British writer\",\"birth_year\":1903}"
echo.
echo.

echo [6] Create categories...
curl -X POST "http://localhost:8000/categories/" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"name\":\"Russian Classics\",\"description\":\"Classic Russian literature\"}"
echo.
curl -X POST "http://localhost:8000/categories/" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"name\":\"Dystopian\",\"description\":\"Dystopian fiction\"}"
echo.
curl -X POST "http://localhost:8000/categories/" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"name\":\"Philosophical Novel\",\"description\":\"Philosophical fiction\"}"
echo.
echo.

echo ========================================
echo   Creating 5 books...
echo ========================================
echo.

echo [7] Book 1: War and Peace (Tolstoy, Russian Classics)...
curl -X POST "http://localhost:8000/books/" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"title\":\"War and Peace\",\"description\":\"Epic novel about Napoleon's invasion\",\"price\":699,\"published_year\":1869,\"author_id\":1,\"category_ids\":[1]}"
echo.
echo.

echo [8] Book 2: Anna Karenina (Tolstoy, Russian Classics)...
curl -X POST "http://localhost:8000/books/" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"title\":\"Anna Karenina\",\"description\":\"Tragic love story\",\"price\":599,\"published_year\":1877,\"author_id\":1,\"category_ids\":[1]}"
echo.
echo.

echo [9] Book 3: Crime and Punishment (Dostoevsky, Russian Classics + Philosophical)...
curl -X POST "http://localhost:8000/books/" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"title\":\"Crime and Punishment\",\"description\":\"Psychological drama\",\"price\":549,\"published_year\":1866,\"author_id\":2,\"category_ids\":[1,3]}"
echo.
echo.

echo [10] Book 4: The Brothers Karamazov (Dostoevsky, Russian Classics + Philosophical)...
curl -X POST "http://localhost:8000/books/" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"title\":\"The Brothers Karamazov\",\"description\":\"Spiritual drama\",\"price\":649,\"published_year\":1880,\"author_id\":2,\"category_ids\":[1,3]}"
echo.
echo.

echo [11] Book 5: 1984 (Orwell, Dystopian)...
curl -X POST "http://localhost:8000/books/" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"title\":\"1984\",\"description\":\"Totalitarian nightmare\",\"price\":499,\"published_year\":1949,\"author_id\":3,\"category_ids\":[2]}"
echo.
echo.

echo ========================================
echo   Adding ratings to books...
echo ========================================
echo.

echo [12] Rating War and Peace: 4.9...
curl -X POST "http://localhost:8000/books/1/rate" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"user_rating\":4.9}"
echo.
echo.

echo [13] Rating Anna Karenina: 4.7...
curl -X POST "http://localhost:8000/books/2/rate" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"user_rating\":4.7}"
echo.
echo.

echo [14] Rating Crime and Punishment: 4.8...
curl -X POST "http://localhost:8000/books/3/rate" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"user_rating\":4.8}"
echo.
echo.

echo [15] Rating Brothers Karamazov: 4.6...
curl -X POST "http://localhost:8000/books/4/rate" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"user_rating\":4.6}"
echo.
echo.

echo [16] Rating 1984: 4.9...
curl -X POST "http://localhost:8000/books/5/rate" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"user_rating\":4.9}"
echo.
echo.

echo ========================================
echo   DEMONSTRATION OF BUSINESS LOGIC
echo ========================================
echo.

echo [17] Get all books list...
curl "http://localhost:8000/books/"
echo.
echo.

echo [18] RECOMMENDATIONS: Similar to War and Peace (Book 1)...
curl "http://localhost:8000/books/1/similar?limit=5"
echo.
echo.
echo EXPLANATION: Algorithm finds books by same author (Tolstoy)
echo and same category (Russian Classics) with high match_score
echo.

echo [19] RECOMMENDATIONS: Similar to Crime and Punishment (Book 3)...
curl "http://localhost:8000/books/3/similar?limit=5"
echo.
echo.
echo EXPLANATION: Algorithm finds books by Dostoevsky and
echo philosophical novels with high match_score
echo.

echo [20] TOP RATED BOOKS (Wilson score with confidence interval)...
curl "http://localhost:8000/books/top/rated?limit=5&min_views=1"
echo.
echo.
echo EXPLANATION: Wilson score ensures fair ranking - books with
echo many high ratings appear above books with few perfect ratings
echo.

echo ========================================
echo   Demonstration completed!
echo ========================================
echo.
echo SUMMARY:
echo - 5 books created (Tolstoy, Dostoevsky, Orwell)
echo - Ratings from 4.6 to 4.9
echo - Recommendation algorithm working
echo - Top books ranking working
echo.
pause
