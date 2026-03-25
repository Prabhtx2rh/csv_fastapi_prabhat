from pathlib import Path
 
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_FILE_PATH = BASE_DIR / "data" / "students_complete.csv"
 
APP_TITLE = "Student Data API"
APP_DESCRIPTION = """
A FastAPI service that loads and serves student data from a CSV file.
 
## Features
- 📋 Fetch all student records with pagination
- 🔍 Search by name, major, city, or status
- 📊 Filter by GPA range, age range, scholarship, and more
- 👤 Fetch individual student by ID
- 📈 Summary statistics endpoint
"""
APP_VERSION = "1.0.0"
 