# 🎓 Student Data API

A production-ready **FastAPI** service that loads student records from a CSV file, caches them in memory at startup, and exposes clean REST endpoints with filtering, searching, and pagination.

---

## 📁 Project Structure

```
student-api/
├── app/
│   ├── main.py                  # FastAPI app, lifespan, global error handlers
│   ├── core/
│   │   └── config.py            # App settings & CSV path
│   ├── models/
│   │   └── student.py           # Pydantic response models
│   ├── services/
│   │   └── student_service.py   # CSV loading, caching, filtering logic
│   └── routes/
│       └── students.py          # /data endpoints
├── data/
│   └── students_complete.csv    # Sample CSV file
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/student-api.git
cd student-api
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be available at **http://127.0.0.1:8000**

---

## 📖 Interactive Docs

| Interface | URL |
|-----------|-----|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

---

## 🔌 API Endpoints

### Root & Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Welcome message & links |
| `GET` | `/health` | Liveness probe |

---

### Students — `GET /data`

Returns a paginated list of students with optional filters.

**Query Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | `1` | Page number (1-indexed) |
| `page_size` | int | `20` | Results per page (max 100) |
| `search` | string | — | Search by first name, last name, or student ID |
| `major` | string | — | Filter by major (case-insensitive) |
| `city` | string | — | Filter by city |
| `status` | string | — | `Paid` \| `Pending` \| `Overdue` |
| `min_gpa` | float | — | Minimum GPA (0.0 – 4.0) |
| `max_gpa` | float | — | Maximum GPA (0.0 – 4.0) |
| `min_age` | int | — | Minimum age |
| `max_age` | int | — | Maximum age |
| `has_scholarship` | bool | — | `true` = has scholarship, `false` = no scholarship |
| `sort_by` | string | `student_id` | Column to sort by |
| `sort_order` | string | `asc` | `asc` or `desc` |

**Example requests**

```bash
# All students, page 1
curl http://127.0.0.1:8000/data

# Computer Science students with GPA ≥ 3.5
curl "http://127.0.0.1:8000/data?major=computer+science&min_gpa=3.5"

# Search by name, sorted by GPA descending
curl "http://127.0.0.1:8000/data?search=olivia&sort_by=gpa&sort_order=desc"

# Overdue students with a scholarship
curl "http://127.0.0.1:8000/data?status=Overdue&has_scholarship=true"

# Page 2 with 10 results per page
curl "http://127.0.0.1:8000/data?page=2&page_size=10"
```

**Response**

```json
{
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "data": [
    {
      "student_id": "STU_1000",
      "first_name": "Liam",
      "last_name": "Smith",
      "major": "Mathematics",
      "gpa": 3.8,
      "city": "Seattle",
      "status": "Paid"
    }
  ]
}
```

---

### Student by ID — `GET /data/{student_id}`

Returns the full record for a single student.

```bash
curl http://127.0.0.1:8000/data/STU_1000
```

**Response**

```json
{
  "student_id": "STU_1000",
  "first_name": "Liam",
  "last_name": "Smith",
  "age": 21,
  "major": "Mathematics",
  "gpa": 3.8,
  "attendance": 92.5,
  "scholarship": 3000,
  "city": "Seattle",
  "status": "Paid"
}
```

Returns `404` if the student is not found.

---

### Statistics — `GET /data/meta/stats`

Aggregate statistics across all records.

```bash
curl http://127.0.0.1:8000/data/meta/stats
```

**Response**

```json
{
  "total_students": 110,
  "average_gpa": 3.21,
  "average_attendance": 85.4,
  "total_scholarship_awarded": 195000,
  "status_breakdown": { "Paid": 60, "Pending": 30, "Overdue": 20 },
  "major_breakdown": { "Computer Science": 15, "Mathematics": 12 },
  "city_breakdown": { "New York": 14, "Seattle": 10 }
}
```

---

### Metadata

```bash
# All distinct majors
curl http://127.0.0.1:8000/data/meta/majors

# All distinct cities
curl http://127.0.0.1:8000/data/meta/cities
```

---

## 🧠 Design Decisions

| Concern | Approach |
|---------|----------|
| **CSV loading** | Loaded once at startup via FastAPI `lifespan`; held in memory as a pandas DataFrame |
| **Caching** | No re-reads on every request — all queries operate on the in-memory DataFrame |
| **Data cleaning** | Column names normalised, major/status title-cased, whitespace stripped, duplicates and missing-ID rows dropped |
| **Missing values** | `gpa` NaN → `null` in JSON (Pydantic `Optional[float]`) |
| **Error handling** | 404 for missing student; 503/500 global handlers; startup failure exits cleanly |
| **Validation** | All query params validated by FastAPI/Pydantic (type, range, regex) |
| **Separation of concerns** | `routes` → HTTP layer; `services` → business logic; `models` → data contracts; `core` → config |

---

## 📦 CSV Format

The service expects a CSV with the following columns:

```
student_id, first_name, last_name, age, major, gpa, attendance, scholarship, city, status
```

Column names are case-insensitive and whitespace-tolerant.

---

## 🛠 Tech Stack

- **FastAPI** — web framework
- **Uvicorn** — ASGI server
- **Pandas** — CSV loading and in-memory querying
- **Pydantic v2** — request/response validation
