from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.student import Student, PaginatedStudents
from app.services.student_service import student_service

router = APIRouter(prefix="/data", tags=["Students"])


@router.get("", response_model=PaginatedStudents)
def get_students(
    page     : int           = Query(1,  ge=1),
    page_size: int           = Query(20, ge=1, le=100),
    min_age  : Optional[int] = Query(None, description="Minimum age (optional)"),
    max_age  : Optional[int] = Query(None, description="Maximum age (optional)"),
):
    return student_service.get_all(
        page=page,
        page_size=page_size,
        min_age=min_age,
        max_age=max_age,
    )


@router.get("/{student_id}", response_model=Student)
def get_student(student_id: str):
    student = student_service.get_by_id(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found.")
    return student