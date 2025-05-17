# 🌍 Country Name Predictor API

A RESTful API that predicts likely countries of origin for a given name and shows the most popular names for any country.  
Integrates [nationalize.io](https://api.nationalize.io/) and [restcountries.com](https://restcountries.com/).

---

## 🚀 Features

- Predict countries by name (`/names/?name=...`)
- Get top 5 names for a country (`/popular-names/?country=...`)
- Country data enrichment (region, flags, capitals, etc.)
- PostgreSQL persistent storage
- **JWT authentication**
- Auto-generated docs: **Swagger**
- Docker & Docker Compose ready
- Linting/formatting: **ruff**
- Unit tests for endpoints and business logic
- Environment via `.env`

---

## 🛠️ How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/country-name-predictor.git
cd country-name-predictor
```

### 2. Prepare `.env` File

```env
POSTGRES_DB=country_name_predictor
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
DJANGO_SECRET_KEY=super-secret-key
```

### 3. Start the Project

```bash
docker compose up --build
```

### 4. Apply Migrations

```bash
docker compose exec web python manage.py migrate
```

### 5. Create a Superuser

```bash
docker compose exec web python manage.py createsuperuser
```

---

## 🔑 Authentication

All endpoints require **JWT authentication**.

### Get a Token

POST to `/api/token/`:

```json
{
  "username": "yourusername",
  "password": "yourpassword"
}
```

### Use the Token

Include the following header in all requests:

```
Authorization: Bearer <your_access_token>
```

---

## 📖 API Documentation

Interactive documentation available after running the project:

- **Swagger UI**: [http://localhost:8000/api/doc/swagger/](http://localhost:8000/api/doc/swagger/)

---

## 📦 Environment Variables

| Variable            | Description            | Example value           |
|---------------------|------------------------|--------------------------|
| POSTGRES_DB         | DB name                | country_name_predictor   |
| POSTGRES_USER       | DB user                | postgres                 |
| POSTGRES_PASSWORD   | DB password            | yourpassword             |
| DJANGO_SECRET_KEY   | Django secret key      | super-secret-key         |


---

## 🧪 Running Tests

```bash
docker compose exec web python manage.py test
```

---

## ⚙️ Example Endpoints

### 1. Predict Countries by Name

`GET /names/?name=John`

```json
{
  "name": "John",
  "count_of_requests": 42,
  "last_accessed": "2025-06-17T12:05:00Z",
  "countries": [
    {
      "country_code": "US",
      "country_name": "United States of America",
      "probability": 0.75,
      "region": "Americas",
      "flag_svg": "https://...",
      "...": "..."
    }
  ]
}
```

### 2. Get Top 5 Names for a Country

`GET /popular-names/?country=US`

```json
{
  "country": "US",
  "top_names": [
    {"name": "John", "count_of_requests": 42},
    {"name": "Maria", "count_of_requests": 27}
  ]
}
```

---

## 🛠 Improvements & Technical Decisions

- ✅ Used **JWT** for secure and scalable auth.
- ✅ **drf-spectacular** used for OpenAPI docs with full integration.
- ✅ Implemented caching using `last_accessed` timestamp to avoid unnecessary API calls.
- ✅ All external API calls mocked in unit tests for speed and reliability.
- 🛑 **Trade-off:** API is synchronous — simple but might not scale under heavy concurrent load.

---

---

## 🐳 Docker Compose Services

- `web` — Django app
- `db` — PostgreSQL 16

---

## 🧑‍💻 Author

[Selemetov Alim](https://github.com/alim2709)

---

## 🏁 Good Luck!

Thank you for reading — and enjoy building with names and flags 🚀
