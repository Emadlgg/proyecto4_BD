from models import session, Faculty, Department, Major, Student, Professor, Course, Classroom, Enrollment, Schedule, CourseAssignment, Book, BookLoan, Payment, Scholarship, AcademicEvent, Evaluation, Attendance, Laboratory, Thesis, AuditLog
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseCRUD:
    @staticmethod
    def handle_error(e: Exception, message: str = "Database error"):
        logger.error(f"{message}: {str(e)}")
        session.rollback()
        raise ValueError(f"{message}: {str(e)}")

class FacultyCRUD(BaseCRUD):
    @staticmethod
    def create_faculty(name: str, location: str, foundation_date: date = None, phone: str = None, dean: str = None) -> Faculty:
        try:
            faculty = Faculty(
                name=name,
                location=location,
                foundation_date=foundation_date,
                phone=phone,
                dean=dean
            )
            session.add(faculty)
            session.commit()
            return faculty
        except IntegrityError as e:
            raise ValueError("Faculty name must be unique")
        except Exception as e:
            BaseCRUD.handle_error(e, "Error creating faculty")

    @staticmethod
    def get_faculty(faculty_id: int) -> Optional[Faculty]:
        return session.query(Faculty).get(faculty_id)

    @staticmethod
    def update_faculty(faculty_id: int, **kwargs) -> Faculty:
        try:
            faculty = session.query(Faculty).get(faculty_id)
            if not faculty:
                raise ValueError("Faculty not found")
            
            for key, value in kwargs.items():
                setattr(faculty, key, value)
            
            session.commit()
            return faculty
        except IntegrityError as e:
            raise ValueError("Faculty name must be unique")
        except Exception as e:
            BaseCRUD.handle_error(e, "Error updating faculty")

    @staticmethod
    def list_faculties() -> List[Faculty]:
        return session.query(Faculty).all()

class DepartmentCRUD(BaseCRUD):
    @staticmethod
    def create_department(name: str, faculty_id: int, budget: float = None, head: str = None, email: str = None) -> Department:
        try:
            department = Department(
                name=name,
                faculty_id=faculty_id,
                budget=budget,
                head=head,
                email=email
            )
            session.add(department)
            session.commit()
            return department
        except Exception as e:
            BaseCRUD.handle_error(e, "Error creating department")

    @staticmethod
    def get_departments_by_faculty(faculty_id: int) -> List[Department]:
        return session.query(Department).filter_by(faculty_id=faculty_id).all()

class MajorCRUD(BaseCRUD):
    @staticmethod
    def create_major(name: str, faculty_id: int, duration_years: int, total_credits: int, degree: str = None) -> Major:
        try:
            major = Major(
                name=name,
                faculty_id=faculty_id,
                duration_years=duration_years,
                total_credits=total_credits,
                degree=degree
            )
            session.add(major)
            session.commit()
            return major
        except IntegrityError as e:
            raise ValueError("Major name must be unique")
        except Exception as e:
            BaseCRUD.handle_error(e, "Error creating major")

class StudentCRUD(BaseCRUD):
    @staticmethod
    def create_student(first_name: str, last_name: str, birth_date: date, email: str, major_id: int = None, 
                      address: str = None, phone: str = None) -> Student:
        try:
            student = Student(
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
                email=email,
                major_id=major_id,
                address=address,
                phone=phone
            )
            session.add(student)
            session.commit()
            return student
        except IntegrityError as e:
            raise ValueError("Student email must be unique")
        except Exception as e:
            BaseCRUD.handle_error(e, "Error creating student")

    @staticmethod
    def enroll_student(student_id: int, course_id: int, semester: str) -> Enrollment:
        try:
            # Check if student is already enrolled
            existing = session.query(Enrollment).filter_by(
                student_id=student_id,
                course_id=course_id,
                semester=semester
            ).first()
            
            if existing:
                raise ValueError("Student is already enrolled in this course for the selected semester")
            
            enrollment = Enrollment(
                student_id=student_id,
                course_id=course_id,
                semester=semester
            )
            session.add(enrollment)
            session.commit()
            return enrollment
        except Exception as e:
            BaseCRUD.handle_error(e, "Error enrolling student")

class CourseCRUD(BaseCRUD):
    @staticmethod
    def create_course(code: str, name: str, credits: int, major_id: int, 
                     description: str = None, department_id: int = None, 
                     prerequisite_id: int = None) -> Course:
        try:
            course = Course(
                code=code,
                name=name,
                credits=credits,
                major_id=major_id,
                description=description,
                department_id=department_id,
                prerequisite_id=prerequisite_id
            )
            session.add(course)
            session.commit()
            return course
        except IntegrityError as e:
            raise ValueError("Course code must be unique")
        except Exception as e:
            BaseCRUD.handle_error(e, "Error creating course")

    @staticmethod
    def assign_professor(course_id: int, professor_id: int, semester: str, 
                         is_coordinator: bool = False, hours_per_week: int = None) -> CourseAssignment:
        try:
            assignment = CourseAssignment(
                course_id=course_id,
                professor_id=professor_id,
                semester=semester,
                is_coordinator=is_coordinator,
                hours_per_week=hours_per_week
            )
            session.add(assignment)
            session.commit()
            return assignment
        except Exception as e:
            BaseCRUD.handle_error(e, "Error assigning professor to course")

class ClassroomCRUD(BaseCRUD):
    @staticmethod
    def create_classroom(code: str, building: str, capacity: int, 
                         classroom_type: str, has_projector: bool = False, 
                         has_computers: bool = False) -> Classroom:
        try:
            classroom = Classroom(
                code=code,
                building=building,
                capacity=capacity,
                type=classroom_type,
                has_projector=has_projector,
                has_computers=has_computers
            )
            session.add(classroom)
            session.commit()
            return classroom
        except IntegrityError as e:
            raise ValueError("Classroom code must be unique")
        except Exception as e:
            BaseCRUD.handle_error(e, "Error creating classroom")

class ScheduleCRUD(BaseCRUD):
    @staticmethod
    def create_schedule(course_id: int, classroom_id: int, day: str, 
                        start_time: str, end_time: str) -> Schedule:
        try:
            # Convert string times to time objects
            start = datetime.strptime(start_time, '%H:%M').time()
            end = datetime.strptime(end_time, '%H:%M').time()
            
            schedule = Schedule(
                course_id=course_id,
                classroom_id=classroom_id,
                day=day,
                start_time=start,
                end_time=end
            )
            session.add(schedule)
            session.commit()
            return schedule
        except Exception as e:
            BaseCRUD.handle_error(e, "Error creating schedule")

class BookCRUD(BaseCRUD):
    @staticmethod
    def create_book(title: str, author: str, isbn: str, 
                    publisher: str = None, publication_year: int = None, 
                    edition: str = None) -> Book:
        try:
            book = Book(
                title=title,
                author=author,
                isbn=isbn,
                publisher=publisher,
                publication_year=publication_year,
                edition=edition
            )
            session.add(book)
            session.commit()
            return book
        except IntegrityError as e:
            raise ValueError("Book ISBN must be unique")
        except Exception as e:
            BaseCRUD.handle_error(e, "Error creating book")

class BookLoanCRUD(BaseCRUD):
    @staticmethod
    def loan_book(book_id: int, student_id: int, due_date: date) -> BookLoan:
        try:
            # Check if book is available
            book = session.query(Book).get(book_id)
            if not book or book.status != 'Available':
                raise ValueError("Book is not available for loan")
            
            loan = BookLoan(
                book_id=book_id,
                student_id=student_id,
                due_date=due_date
            )
            session.add(loan)
            
            # Update book status
            book.status = 'Loaned'
            session.commit()
            return loan
        except Exception as e:
            BaseCRUD.handle_error(e, "Error loaning book")

class PaymentCRUD(BaseCRUD):
    @staticmethod
    def create_payment(student_id: int, amount: float, payment_type: str, 
                       description: str = None, reference_number: str = None) -> Payment:
        try:
            payment = Payment(
                student_id=student_id,
                amount=amount,
                payment_type=payment_type,
                description=description,
                reference_number=reference_number
            )
            session.add(payment)
            session.commit()
            return payment
        except Exception as e:
            BaseCRUD.handle_error(e, "Error creating payment")

class EvaluationCRUD(BaseCRUD):
    @staticmethod
    def create_evaluation(course_id: int, name: str, evaluation_type: str, 
                          evaluation_date: date, weight: float, 
                          description: str = None) -> Evaluation:
        try:
            evaluation = Evaluation(
                course_id=course_id,
                name=name,
                evaluation_type=evaluation_type,
                evaluation_date=evaluation_date,
                weight=weight,
                description=description
            )
            session.add(evaluation)
            session.commit()
            return evaluation
        except Exception as e:
            BaseCRUD.handle_error(e, "Error creating evaluation")

class ThesisCRUD(BaseCRUD):
    @staticmethod
    def create_thesis(title: str, student_id: int, advisor_id: int, 
                      status: str = "En progreso", grade: float = None, 
                      file_url: str = None) -> Thesis:
        try:
            thesis = Thesis(
                title=title,
                student_id=student_id,
                advisor_id=advisor_id,
                status=status,
                grade=grade,
                file_url=file_url
            )
            session.add(thesis)
            session.commit()
            return thesis
        except Exception as e:
            BaseCRUD.handle_error(e, "Error creating thesis")

class AuditCRUD(BaseCRUD):
    @staticmethod
    def get_audit_logs(table_name: str = None, record_id: int = None, 
                       start_date: date = None, end_date: date = None) -> List[AuditLog]:
        query = session.query(AuditLog)
        
        if table_name:
            query = query.filter_by(table_name=table_name)
        if record_id:
            query = query.filter_by(record_id=record_id)
        if start_date:
            query = query.filter(AuditLog.change_date >= start_date)
        if end_date:
            query = query.filter(AuditLog.change_date <= end_date)
        
        return query.order_by(AuditLog.change_date.desc()).all()

# Clase principal que agrupa todos los CRUDs
class UniversityCRUD:
    def __init__(self):
        self.faculty = FacultyCRUD()
        self.department = DepartmentCRUD()
        self.major = MajorCRUD()
        self.student = StudentCRUD()
        self.course = CourseCRUD()
        self.classroom = ClassroomCRUD()
        self.schedule = ScheduleCRUD()
        self.book = BookCRUD()
        self.book_loan = BookLoanCRUD()
        self.payment = PaymentCRUD()
        self.evaluation = EvaluationCRUD()
        self.thesis = ThesisCRUD()
        self.audit = AuditCRUD()

# Ejemplo de uso
if __name__ == "__main__":
    crud = UniversityCRUD()
    
    # Crear una facultad
    try:
        faculty = crud.faculty.create_faculty(
            name="Ingeniería",
            location="Edificio T1",
            dean="Dr. Juan Pérez"
        )
        print(f"Facultad creada: {faculty.name}")
    except ValueError as e:
        print(f"Error: {str(e)}")