# Multi-Vendor E-commerce Backend

Production-minded multi-vendor e-commerce backend built with Django REST Framework, Redis, WebSockets, JWT authentication, and Docker.

This project focuses on real-world backend requirements: role-based vendor/customer flows, order lifecycle, payment simulation, realtime chat/notifications, caching, and clean API error handling.

## Why This Project Matters
- Recruiters and technical reviewers first evaluate architecture clarity and delivery quality.
- This backend demonstrates practical engineering patterns, not only CRUD.
- API design includes security, realtime communication, optimization, and deployment readiness.

## Core Features
- Multi-vendor system (customer + vendor roles)
- JWT authentication (login/refresh)
- Product and category management
- Cart and order workflow
- Payment simulation with stock validation
- Review and rating system
- Realtime customer-vendor chat (WebSocket)
- Realtime notifications (WebSocket)
- Redis caching and query optimizations
- Global custom error handling for frontend-friendly responses

## Tech Stack
- Python 3.10+
- Django 5
- Django REST Framework
- JWT: `djangorestframework-simplejwt`
- Realtime: Django Channels + Channels Redis
- Redis (channel layer + cache)
- PostgreSQL (Docker/prod)
- SQLite (local quick start)
- Docker + Docker Compose
- OpenAPI docs: drf-spectacular

## Architecture Highlights
- App-based modular structure (`users`, `vendors`, `products`, `orders`, `chat`, `services`, etc.)
- Signal-driven automation for notifications and order events
- ASGI + WebSocket routing for realtime features
- Environment-based settings (`local`, `production`)
- Global exception handler for consistent API errors
- Pagination and query optimization (`select_related`, `prefetch_related`)

## Getting Started (Local)

### 1. Clone
```bash
git clone <your-repo-url>
cd ecommerce
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create `.env` in project root:

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=ecommerce
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5432

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_CHANNEL_DB=0
REDIS_CACHE_DB=1

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Start Development Server
```bash
python manage.py runserver
```

### 8. Seed Demo Data (Optional)
Create showcase data for demos and recruiter review:

```bash
python manage.py seed_demo_data --vendors 5 --products 20 --orders 10
```

Default demo credentials created by the command:
- Vendor users: `demo_vendor_1` ... `demo_vendor_5`
- Customer users: `demo_customer_1` ...
- Password: `DemoPass123!`

API docs:
- `http://127.0.0.1:8000/api/docs/`
- `http://127.0.0.1:8000/api/schema/`

## Run with Docker

### 1. Build and Start
```bash
docker compose up --build
```

### 2. Apply Migrations in Container
```bash
docker compose exec web python manage.py migrate
```

### 3. (Optional) Create Superuser
```bash
docker compose exec web python manage.py createsuperuser
```

Services:
- API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Authentication Flow (JWT)

### Register
`POST /users/register/`

### Login
`POST /users/login/`

### Refresh Token
`POST /users/refresh/`

Send JWT in headers:
```http
Authorization: Bearer <access_token>
```

## API Endpoints (Summary)

### Users
- `POST /users/register/`
- `POST /users/login/`
- `POST /users/refresh/`

### Vendors
- `GET, POST /vendors/`
- `GET, PUT, PATCH, DELETE /vendors/{id}/`
- `GET, PUT /vendors/me/`

### Products & Categories
- `GET, POST /products/products/`
- `GET, PUT, PATCH, DELETE /products/products/{id}/`
- `GET, POST /products/categories/`
- `GET, PUT, PATCH, DELETE /products/categories/{id}/`
- `GET /products/api/products/` (search/list alias)
- `GET /products/api/products/top/`
- `GET, POST /products/api/products/{product_id}/images/`
- `DELETE /products/api/products/{product_id}/images/{id}/`

### Orders
- `GET, POST /orders/orders/`
- `GET /orders/orders/{id}/`
- `POST /orders/orders/{id}/pay/`
- `POST /orders/orders/{id}/ship/`

### Notifications
- `GET /services/api/notifications/`
- `POST /services/api/notifications/{id}/read/`
- `GET /services/vendors/notifications/`

### Chat
- `GET /api/chat/rooms/`
- `GET /api/chat/rooms/{id}/messages/`

### Wishlist
- `POST /api/wishlist/add/`
- `GET /api/wishlist/`
- `DELETE /api/wishlist/remove/{id}/`

### Reviews
- `GET, POST /api/products/{id}/reviews/`
- `DELETE /api/reviews/{id}/`

### API Documentation
- `GET /api/schema/`
- `GET /api/docs/`

## WebSocket Endpoints
- Notifications: `ws://localhost:8000/ws/notifications/`
- Chat room: `ws://localhost:8000/ws/chat/{room_id}/`

## Example Error Response
The API uses a global exception handler so frontend receives consistent errors:

```json
{
  "error": "Product not found",
  "code": "not_found",
  "status": 404
}
```

## Performance & Reliability
- Default pagination enabled (page size: 20)
- Query optimization in list endpoints
- Redis caching for high-traffic reads
- Role-aware queryset restrictions
- Structured logging and production settings

## Caching Implementation
- Backend: Redis (`django.core.cache.backends.redis.RedisCache`)
- Product list and category list responses are cached to reduce DB load
- Versioned cache keys are used for safer invalidation after create/update/delete
- Top products endpoint is cache-backed for faster homepage/read-heavy traffic

## Testing
```bash
python manage.py test
```

## Project Structure (High-Level)
```text
ecommerce/
  config/
  users/
  vendors/
  products/
  orders/
  cart/
  reviews/
  wishlist/
  services/
  chat/
  Dockerfile
  docker-compose.yml
  requirements.txt
```

## Notes
- Local dev can run with SQLite quickly.
- Docker setup is prepared for PostgreSQL + Redis + Gunicorn/ASGI.
- Realtime features require Redis running.

## License
Add your preferred license (MIT/Apache-2.0/etc.).
