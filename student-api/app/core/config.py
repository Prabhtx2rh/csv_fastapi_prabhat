import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR      = Path(__file__).resolve().parent.parent.parent
CSV_FILE_PATH = BASE_DIR / "data" / "students_complete.csv"

MYSQL_USER     = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST     = os.getenv("MYSQL_HOST")
MYSQL_PORT     = os.getenv("MYSQL_PORT")
MYSQL_DB       = os.getenv("MYSQL_DB")

APP_TITLE       = os.getenv("APP_TITLE",   "Student Data API")
APP_VERSION     = os.getenv("APP_VERSION", "1.0.0")
APP_DESCRIPTION = "A FastAPI service that loads and serves student data from a CSV file."