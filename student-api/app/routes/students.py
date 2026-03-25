from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.student import Student, PaginatedStudents, StatsSummary
from app.services.student_service import student_service

router = APIRouter(prefix="/data", tags=["Students"])


@router.get(
    "",
    response_model=PaginatedStudents,
    summary="Get all students",
    description=(
        "Returns a paginated list of students. "
        "Supports full-text search, filtering by major/city/status/GPA/age/scholarship, "
        "and sorting."
    ),
)
def get_students(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page (max 100)"),
    search: Optional[str] = Query(None, description="Search by first name, last name, or student ID"),
    major: Optional[str] = Query(None, description="Filter by major (case-insensitive)"),
    city: Optional[str] = Query(None, description="Filter by city (case-insensitive)"),
    status: Optional[str] = Query(None, description="Filter by payment status: Paid | Pending | Overdue"),
    min_gpa: Optional[float] = Query(None, ge=0.0, le=4.0, description="Minimum GPA"),
    max_gpa: Optional[float] = Query(None, ge=0.0, le=4.0, description="Maximum GPA"),
    min_age: Optional[int] = Query(None, ge=0, description="Minimum age"),
    max_age: Optional[int] = Query(None, ge=0, description="Maximum age"),
    has_scholarship: Optional[bool] = Query(None, description="Filter students who have (true) or don't have (false) a scholarship"),
    sort_by: Optional[str] = Query("student_id", description="Column to sort by"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort direction: asc or desc"),
):
    result = student_service.get_all(
        page=page,
        page_size=page_size,
        search=search,
        major=major,
        city=city,
        status=status,
        min_gpa=min_gpa,
        max_gpa=max_gpa,
        min_age=min_age,
        max_age=max_age,
        has_scholarship=has_scholarship,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return result


@router.get(
    "/{student_id}",
    response_model=Student,
    summary="Get student by ID",
    responses={404: {"description": "Student not found"}},
)
def get_student(student_id: str):
    student = student_service.get_by_id(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found.")
    return student


