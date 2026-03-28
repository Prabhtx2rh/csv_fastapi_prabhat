from sqlalchemy import Column, String, Integer, Float
from app.core.database import Base


class StudentDB(Base):
    __tablename__ = "students"

    student_id = Column(String(20),  primary_key=True, index=True)
    first_name = Column(String(50),  nullable=False)
    last_name  = Column(String(50),  nullable=False)
    age        = Column(Integer,     nullable=False)
    major      = Column(String(100), nullable=False)
    gpa        = Column(Float,       nullable=True)
    attendance = Column(Float,       nullable=False)
    scholarship= Column(Integer,     nullable=False, default=0)
    city       = Column(String(100), nullable=False)
    status     = Column(String(20),  nullable=False)