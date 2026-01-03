# Mini Assessment Engine

A Django-based REST API that simulates a core academic assessment platform.  
Built with **Django 5+**, **PostgreSQL**, and **Django Rest Framework**.

## 🚀 Features

### Functional
- **Exam Management**: List and retrieve exams with questions (MCQ & Text).
- **Secure Submissions**: Students can take exams and submit answers.
- **Automated Grading**:
  - **Exact Match**: Automatically grades MCQs.
  - **Fuzzy Match**: Uses similarity algorithms (Mock AI) to grade text answers.
- **Results**: Students view their own private submission history.

### Technical & Non-Functional
- **Efficiency**: Optimized queries using `prefetch_related` and batch processing to avoid N+1 issues.
- **Security**: JWT Authentication (SimpleJWT) with stateless sessions. User data isolation.
- **Database**: Normalized PostgreSQL Schema with proper constraints.
- **Documentation**: Auto-generated Swagger/OpenAPI docs.
- **Containerization**: Docker support for the database layer.

---

## 🛠 Tech Stack

- **Backend**: Python 3, Django, Django Rest Framework (DRF)
- **Database**: PostgreSQL (Dockerized)
- **Auth**: JWT (djangorestframework-simplejwt)
- **Docs**: drf-spectacular (OpenAPI 3.0)

---

## 🏗 System Architecture

### Database Schema (Normalized)
- **User**: Standard Django Auth.
- **Exam**: Meta-data (title, duration).
- **Question**: Linked to Exam. Stores `question_type` (MCQ/TEXT) and `options` (JSON).
- **Submission**: Links User <-> Exam. Stores final score.
- **Answer**: Links Submission <-> Question. Stores raw student input and correctness.

### Grading Service (`core/services.py`)
Decoupled logic that evaluates a submission.  
- **MCQ**: String comparison (Trimmed/Lowercased).
- **Text**: `difflib.SequenceMatcher` with >0.8 threshold.

---

## ⚡ Setup & Run

### 1. Prerequisites
- Python 3.10+
- Docker & Docker Compose (for Postgres)

### 2. Environment
Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

Configure the following variables in `.env`:
```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=assessment_engine_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5433

# JWT Token Configuration
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60    # Access token expires in 1 hour
JWT_REFRESH_TOKEN_LIFETIME_DAYS=15      # Refresh token expires in 15 days
```

Install dependencies:
```bash
pip install -r requirements.txt

# Start Database (Postgres on port 5433)
docker compose up -d
```

### 3. Initialize
```bash
# Run Migrations
python3 manage.py migrate
```

### 4. Run Server
```bash
python3 manage.py runserver
```
API available at `http://127.0.0.1:8000/`.

---

## 🧪 Testing

### Automated Tests
Run the rigorous test suite covering Auth, Validation, and Grading limits:
```bash
python3 manage.py test core
```

### Manual Testing (Swagger)
Access Swagger UI at:  
`http://127.0.0.1:8000/api/schema/swagger-ui/`

**Key Payloads**:
1. **Register**: `POST /api/auth/register/` `{ "username": "...", "password": "..." }`
2. **Login**: `POST /api/auth/login/` -> Get Token -> **Authorize**
3. **Submit**: `POST /api/submit/`
    ```json
    {
      "exam_id": 1,
      "answers": [{"question_id": 1, "student_answer": "..."}]
    }
    ```

---

## 🔍 Optimizations Implemented
- **Exam Listing**: Uses `prefetch_related('questions')` to fetch all questions for exams in 2 queries instead of N+1.
- **Submissions**: Validates and fetches related Questions in a **single batch query** (`filter(id__in=...)`) during submission processing, reducing database round-trips significantly.
