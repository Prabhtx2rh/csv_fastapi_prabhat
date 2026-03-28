from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import MYSQL_HOST, MYSQL_DB
from app.services.db_service import (
    insert_csv_to_db,
    get_all_students_from_db,
    get_student_by_id_from_db,
)

router = APIRouter(tags=["Database"])


@router.get("/check_db")
def check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status"  : "connected",
            "host"    : MYSQL_HOST,
            "database": MYSQL_DB,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")


@router.post("/db/insert")
def insert_data(db: Session = Depends(get_db)):
    try:
        return insert_csv_to_db(db)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insert failed: {str(e)}")


@router.get("/db/students")
def get_students_from_db(
    page     : int = 1,
    page_size: int = 20,
    db       : Session = Depends(get_db),
):
    return get_all_students_from_db(db=db, page=page, page_size=page_size)


@router.get("/db/students/{student_id}")
def get_student_from_db(student_id: str, db: Session = Depends(get_db)):
    student = get_student_by_id_from_db(db, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found.")
    return student