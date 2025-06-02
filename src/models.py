from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, ForeignKey, Enum, Boolean, Time, Text, CheckConstraint, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, validates
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from datetime import datetime, timedelta
import re
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de la base de datos
Base = declarative_base()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/university_db')
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
Session = sessionmaker(bind=engine)
session = Session()

# Enums para tipos personalizados
class SemesterType(PyEnum):
    SUMMER = "Verano"
    FIRST = "Primer Semestre"
    SECOND = "Segundo Semestre"

class ClassroomType(PyEnum):
    THEORY = "Teoría"
    LAB = "Laboratorio"
    AUDITORIUM = "Auditorio"

class GradeType(PyEnum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"
    NP = "NP"

class PaymentType(PyEnum):
    TUITION = "Matrícula"
    FINE = "Multa"
    DONATION = "Donación"

class ThesisStatus(PyEnum):
    IN_PROGRESS = "En progreso"
    FINISHED = "Finalizada"
    APPROVED = "Aprobada"
    FAILED = "Reprobada"


class Faculty(Base):
    __tablename__ = 'facultad'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    location = Column(String(100))
    foundation_date = Column(Date)
    phone = Column(String(15))
    dean = Column(String(100))
    
    departments = relationship("Department", back_populates="faculty")
    majors = relationship("Major", back_populates="faculty")
    
    @validates('name')
    def validate_name(self, key, name):
        if len(name) < 3:
            raise ValueError("Faculty name must be at least 3 characters")
        return name.title()

class Department(Base):
    __tablename__ = 'departamento'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    faculty_id = Column(Integer, ForeignKey('facultad.id'), nullable=False)
    budget = Column(Numeric(12, 2))
    head = Column(String(100))
    email = Column(String(100))
    
    faculty = relationship("Faculty", back_populates="departments")
    professors = relationship("Professor", back_populates="department")
    
    __table_args__ = (
        CheckConstraint('budget >= 0', name='check_positive_budget'),
        {'schema': 'public'}
    )

class Major(Base):
    __tablename__ = 'carrera'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    faculty_id = Column(Integer, ForeignKey('facultad.id'), nullable=False)
    duration_years = Column(Integer, nullable=False)
    total_credits = Column(Integer, nullable=False)
    degree = Column(String(50))  # Licenciatura, Maestría, etc.
    
    faculty = relationship("Faculty", back_populates="majors")
    students = relationship("Student", back_populates="major")
    courses = relationship("Course", back_populates="major")
    
    @validates('duration_years')
    def validate_duration(self, key, years):
        if years < 1 or years > 6:
            raise ValueError("Duration must be between 1 and 6 years")
        return years

class Student(Base):
    __tablename__ = 'estudiante'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birth_date = Column(Date, nullable=False)
    address = Column(Text)
    phone = Column(String(15))
    email = Column(String(100), unique=True, nullable=False)
    major_id = Column(Integer, ForeignKey('carrera.id'))
    enrollment_date = Column(Date, default=datetime.now().date())
    status = Column(String(20), default='Active')  # Active, Inactive, Graduated
    
    major = relationship("Major", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student")
    book_loans = relationship("BookLoan", back_populates="student")
    payments = relationship("Payment", back_populates="student")
    thesis = relationship("Thesis", back_populates="student")
    
    @validates('email')
    def validate_email(self, key, email):
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise ValueError("Invalid email format")
        if not email.endswith(('@uvg.edu.gt', '@estudiantec.edu.gt')):
            raise ValueError("Only institutional emails allowed")
        return email
    
    @validates('birth_date')
    def validate_birth_date(self, key, date):
        min_age_date = datetime.now().date().replace(year=datetime.now().year - 16)
        if date > min_age_date:
            raise ValueError("Student must be at least 16 years old")
        return date

class Professor(Base):
    __tablename__ = 'profesor'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    specialization = Column(String(100))
    department_id = Column(Integer, ForeignKey('departamento.id'), nullable=False)
    hire_date = Column(Date, nullable=False)
    salary = Column(Numeric(10, 2), nullable=False)
    email = Column(String(100), unique=True)
    is_active = Column(Boolean, default=True)
    
    department = relationship("Department", back_populates="professors")
    course_assignments = relationship("CourseAssignment", back_populates="professor")
    advised_theses = relationship("Thesis", back_populates="advisor")
    
    __table_args__ = (
        CheckConstraint('salary > 0', name='check_positive_salary'),
    )

class Course(Base):
    __tablename__ = 'curso'
    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    credits = Column(Integer, nullable=False)
    description = Column(Text)
    major_id = Column(Integer, ForeignKey('carrera.id'), nullable=False)
    prerequisite_id = Column(Integer, ForeignKey('curso.id'))
    department_id = Column(Integer, ForeignKey('departamento.id'))
    
    major = relationship("Major", back_populates="courses")
    prerequisite = relationship("Course", remote_side=[id])
    department = relationship("Department")
    schedules = relationship("Schedule", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")
    assignments = relationship("CourseAssignment", back_populates="course")
    evaluations = relationship("Evaluation", back_populates="course")
    
    __table_args__ = (
        CheckConstraint('credits > 0', name='check_positive_credits'),
    )

class Classroom(Base):
    __tablename__ = 'aula'
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    building = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    type = Column(Enum(ClassroomType), nullable=False)
    has_projector = Column(Boolean, default=False)
    has_computers = Column(Boolean, default=False)
    
    schedules = relationship("Schedule", back_populates="classroom")
    
    @validates('capacity')
    def validate_capacity(self, key, capacity):
        if capacity < 1:
            raise ValueError("Capacity must be at least 1")
        return capacity

class Enrollment(Base):
    __tablename__ = 'matricula'
    student_id = Column(Integer, ForeignKey('estudiante.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('curso.id'), primary_key=True)
    semester = Column(Enum(SemesterType), primary_key=True)
    grade = Column(Enum(GradeType))
    enrollment_date = Column(DateTime, server_default=func.now())
    status = Column(String(20), default='Active')
    
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    
    @validates('grade')
    def validate_grade(self, key, grade):
        if grade == GradeType.NP and self.semester == SemesterType.SUMMER:
            raise ValueError("NP grade not allowed in summer semester")
        return grade

class Schedule(Base):
    __tablename__ = 'horario'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('curso.id'), nullable=False)
    classroom_id = Column(Integer, ForeignKey('aula.id'), nullable=False)
    day = Column(String(10), nullable=False)  # Lunes, Martes, etc.
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    course = relationship("Course", back_populates="schedules")
    classroom = relationship("Classroom", back_populates="schedules")
    
    __table_args__ = (
        CheckConstraint('end_time > start_time', name='check_valid_time_range'),
    )

class CourseAssignment(Base):
    __tablename__ = 'asignacion_profesor'
    professor_id = Column(Integer, ForeignKey('profesor.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('curso.id'), primary_key=True)
    semester = Column(Enum(SemesterType), primary_key=True)
    is_coordinator = Column(Boolean, default=False)
    hours_per_week = Column(Integer)
    
    professor = relationship("Professor", back_populates="course_assignments")
    course = relationship("Course", back_populates="assignments")

class Book(Base):
    __tablename__ = 'libro'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    isbn = Column(String(20), unique=True, nullable=False)
    publisher = Column(String(100))
    publication_year = Column(Integer)
    edition = Column(String(10))
    status = Column(String(20), default='Available')  # Available, Loaned, Reserved
    
    loans = relationship("BookLoan", back_populates="book")
    
    @validates('publication_year')
    def validate_year(self, key, year):
        current_year = datetime.now().year
        if year < 1800 or year > current_year:
            raise ValueError(f"Publication year must be between 1800 and {current_year}")
        return year

class BookLoan(Base):
    __tablename__ = 'prestamo_libro'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('libro.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('estudiante.id'), nullable=False)
    loan_date = Column(Date, nullable=False, default=datetime.now().date())
    due_date = Column(Date, nullable=False)
    return_date = Column(Date)
    fine = Column(Numeric(8, 2), default=0.0)
    
    book = relationship("Book", back_populates="loans")
    student = relationship("Student", back_populates="book_loans")
    
    @validates('due_date')
    def validate_due_date(self, key, date):
        if date <= datetime.now().date():
            raise ValueError("Due date must be in the future")
        max_due_date = datetime.now().date() + timedelta(days=30)
        if date > max_due_date:
            raise ValueError("Maximum loan period is 30 days")
        return date

class Payment(Base):
    __tablename__ = 'pago'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('estudiante.id'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(DateTime, nullable=False, default=func.now())
    payment_type = Column(Enum(PaymentType), nullable=False)
    description = Column(Text)
    reference_number = Column(String(50), unique=True)
    
    student = relationship("Student", back_populates="payments")
    
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_positive_amount'),
    )

class Scholarship(Base):
    __tablename__ = 'beca'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)
    student_id = Column(Integer, ForeignKey('estudiante.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    requirements = Column(Text)
    
    student = relationship("Student")
    
    __table_args__ = (
        CheckConstraint('percentage > 0 AND percentage <= 100', name='check_percentage_range'),
        CheckConstraint('end_date IS NULL OR end_date > start_date', name='check_valid_dates'),
    )

class AcademicEvent(Base):
    __tablename__ = 'evento_academico'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    event_date = Column(Date, nullable=False)
    start_time = Column(Time)
    end_time = Column(Time)
    responsible_id = Column(Integer, ForeignKey('profesor.id'), nullable=False)
    location = Column(String(100), nullable=False)
    cost = Column(Numeric(8, 2), default=0.0)
    capacity = Column(Integer)
    
    responsible = relationship("Professor")

class Evaluation(Base):
    __tablename__ = 'evaluacion'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('curso.id'), nullable=False)
    name = Column(String(100), nullable=False)
    evaluation_type = Column(String(20), nullable=False)  # Partial, Final, Project, etc.
    evaluation_date = Column(Date, nullable=False)
    weight = Column(Numeric(5, 2), nullable=False)
    description = Column(Text)
    
    course = relationship("Course", back_populates="evaluations")
    
    __table_args__ = (
        CheckConstraint('weight > 0 AND weight <= 100', name='check_weight_range'),
    )

class Attendance(Base):
    __tablename__ = 'asistencia'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('estudiante.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('curso.id'), nullable=False)
    date = Column(Date, nullable=False)
    present = Column(Boolean, nullable=False)
    justification = Column(Text)
    
    __table_args__ = (
        CheckConstraint('date <= CURRENT_DATE', name='check_date_not_future'),
        {'schema': 'public'}
    )

class Laboratory(Base):
    __tablename__ = 'laboratorio'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    responsible_id = Column(Integer, ForeignKey('profesor.id'), nullable=False)
    capacity = Column(Integer, nullable=False)
    equipment = Column(Text)
    opening_hours = Column(Text)
    
    responsible = relationship("Professor")

class Thesis(Base):
    __tablename__ = 'tesis'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    student_id = Column(Integer, ForeignKey('estudiante.id'), nullable=False)
    advisor_id = Column(Integer, ForeignKey('profesor.id'), nullable=False)
    start_date = Column(Date, nullable=False, default=datetime.now().date())
    submission_date = Column(Date)
    status = Column(Enum(ThesisStatus), nullable=False)
    grade = Column(Numeric(3, 1))
    file_url = Column(Text)
    
    student = relationship("Student", back_populates="thesis")
    advisor = relationship("Professor", back_populates="advised_theses")
    
    __table_args__ = (
        CheckConstraint('grade >= 0 AND grade <= 10', name='check_grade_range'),
    )

class AuditLog(Base):
    __tablename__ = 'auditoria_cambios'
    id = Column(Integer, primary_key=True)
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=False)
    operation = Column(String(10), nullable=False)  # INSERT, UPDATE, DELETE
    change_date = Column(DateTime, nullable=False, default=func.now())
    user = Column(String(50), nullable=False)
    old_values = Column(JSON)
    new_values = Column(JSON)

def init_db():
    Base.metadata.create_all(engine)
    print("Database initialized successfully")

if __name__ == "__main__":
    init_db()