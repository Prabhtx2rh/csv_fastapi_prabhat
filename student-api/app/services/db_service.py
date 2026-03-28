import math
import pandas as pd
from sqlalchemy.orm import Session

from app.models.db_models import StudentDB
from app.core.config import CSV_FILE_PATH


def insert_csv_to_db(db: Session) -> dict:
    df = pd.read_csv(CSV_FILE_PATH)

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())
    df["major"]  = df["major"].str.title()
    df["status"] = df["status"].str.title()
    df = df.dropna(subset=["student_id"])
    df = df.drop_duplicates(subset=["student_id"])

    inserted = 0
    skipped  = 0

    for _, row in df.iterrows():
        existing = db.query(StudentDB).filter(
            StudentDB.student_id == row["student_id"]
        ).first()

        if existing:
            skipped += 1
            continue

        gpa_value = row.get("gpa")
        student = StudentDB(
            student_id  = row["student_id"],
            first_name  = row["first_name"],
            last_name   = row["last_name"],
            age         = int(row["age"]),
            major       = row["major"],
            gpa         = None if (isinstance(gpa_value, float) and math.isnan(gpa_value)) else gpa_value,
            attendance  = float(row["attendance"]),
            scholarship = int(row["scholarship"]),
            city        = row["city"],
            status      = row["status"],
        )

        db.add(student)
        inserted += 1

    db.commit()

    return {
        "message" : "CSV data inserted successfully",
        "inserted": inserted,
        "skipped" : skipped,
        "total"   : inserted + skipped,
    }


def get_all_students_from_db(
    db        : Session,
    page      : int = 1,
    page_size : int = 20,
) -> dict:
    query = db.query(StudentDB)

    total       = query.count()
    total_pages = max(1, math.ceil(total / page_size))
    page        = max(1, min(page, total_pages))
    offset      = (page - 1) * page_size
    students    = query.offset(offset).limit(page_size).all()

    return {
        "total"      : total,
        "page"       : page,
        "page_size"  : page_size,
        "total_pages": total_pages,
        "data"       : students,
    }


def get_student_by_id_from_db(db: Session, student_id: str):
    return db.query(StudentDB).filter(
        StudentDB.student_id == student_id
    ).first()