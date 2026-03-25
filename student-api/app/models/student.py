from pydantic import BaseModel, Field
from typing import Optional, List


class Student(BaseModel):
    student_id: str
    first_name: str
    last_name: str
    age: int
    major: str
    gpa: Optional[float] = None
    attendance: float
    scholarship: int
    city: str
    status: str

    model_config = {"from_attributes": True}


class StudentSummary(BaseModel):
    """Lightweight model returned in list responses."""
    student_id: str
    first_name: str
    last_name: str
    major: str
    gpa: Optional[float] = None
    city: str
    status: str


class PaginatedStudents(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[StudentSummary]


class StatsSummary(BaseModel):
    total_students: int
    average_gpa: float
    average_attendance: float
    total_scholarship_awarded: int
    status_breakdown: dict
    major_breakdown: dict
    city_breakdown: dict


class ErrorResponse(BaseModel):
    detail: str
