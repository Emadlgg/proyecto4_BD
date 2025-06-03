from models import session, Faculty, Department, Major, Student, Professor, Course, Enrollment, Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import date, datetime
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

# Agregar clase para mapear vistas
class FacultyDetailView(Base):
    __tablename__ = 'vista_facultades_detalladas'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    ubicacion = Column(String(100))
    decano = Column(String(100))
    total_departamentos = Column(Integer)
    total_carreras = Column(Integer)

class FacultyCRUD(BaseCRUD):
    @staticmethod
    def create_faculty(name: str, location: str, foundation_date: date = None, phone: str = None, dean: str = None):
        try:
            faculty = Faculty(
                nombre=name,
                ubicacion=location,
                fecha_fundacion=foundation_date,
                telefono=phone,
                decano=dean
            )
            session.add(faculty)
            session.commit()
            session.refresh(faculty)  # Para obtener el ID generado
            return faculty
            
        except IntegrityError as e:
            session.rollback()
            raise ValueError("Faculty name must be unique")
        except Exception as e:
            BaseCRUD.handle_error(e, "Error creating faculty")

    @staticmethod
    def list_faculties():
        try:
            return session.query(Faculty).order_by(Faculty.nombre).all()
        except Exception as e:
            BaseCRUD.handle_error(e, "Error listing faculties")

    @staticmethod
    def get_faculty(faculty_id: int):
        try:
            return session.query(Faculty).filter(Faculty.id == faculty_id).first()
        except Exception as e:
            BaseCRUD.handle_error(e, "Error getting faculty")

    @staticmethod
    def update_faculty(faculty_id: int, **kwargs):
        try:
            faculty = session.query(Faculty).filter(Faculty.id == faculty_id).first()
            if not faculty:
                raise ValueError("Faculty not found")
            
            for key, value in kwargs.items():
                if hasattr(faculty, key):
                    setattr(faculty, key, value)
            
            session.commit()
            return faculty
        except Exception as e:
            BaseCRUD.handle_error(e, "Error updating faculty")

    @staticmethod
    def delete_faculty(faculty_id: int):
        try:
            faculty = session.query(Faculty).filter(Faculty.id == faculty_id).first()
            if not faculty:
                raise ValueError("Faculty not found")
            
            session.delete(faculty)
            session.commit()
            return True
        except Exception as e:
            BaseCRUD.handle_error(e, "Error deleting faculty")

    @staticmethod
    def list_faculties_detailed():
        """Usar vista para mostrar listado con estadísticas"""
        try:
            return session.query(FacultyDetailView).order_by(FacultyDetailView.nombre).all()
        except Exception as e:
            BaseCRUD.handle_error(e, "Error listing detailed faculties")

class StudentCRUD(BaseCRUD):
    @staticmethod
    def create_student(nombre: str, apellido: str, fecha_nacimiento: date, email: str, 
                      carrera_id: int = None, direccion: str = None, telefono: str = None):
        try:
            student = Student(
                nombre=nombre,
                apellido=apellido,
                fecha_nacimiento=fecha_nacimiento,
                email=email,
                carrera_id=carrera_id,
                direccion=direccion,
                telefono=telefono
            )
            session.add(student)
            session.commit()
            session.refresh(student)
            return student
        except IntegrityError as e:
            session.rollback()
            raise ValueError("Email must be unique")
        except Exception as e:
            BaseCRUD.handle_error(e, "Error creating student")

    @staticmethod
    def list_students():
        try:
            return session.query(Student).join(Major, Student.carrera_id == Major.id, isouter=True).order_by(Student.apellido, Student.nombre).all()
        except Exception as e:
            BaseCRUD.handle_error(e, "Error listing students")

    @staticmethod
    def get_student(student_id: int):
        try:
            return session.query(Student).filter(Student.id == student_id).first()
        except Exception as e:
            BaseCRUD.handle_error(e, "Error getting student")

    @staticmethod
    def update_student(student_id: int, **kwargs):
        try:
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise ValueError("Student not found")
            
            for key, value in kwargs.items():
                if hasattr(student, key):
                    setattr(student, key, value)
            
            session.commit()
            return student
        except Exception as e:
            BaseCRUD.handle_error(e, "Error updating student")

    @staticmethod
    def delete_student(student_id: int):
        try:
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise ValueError("Student not found")
            
            session.delete(student)
            session.commit()
            return True
        except Exception as e:
            BaseCRUD.handle_error(e, "Error deleting student")

class ProfessorCRUD(BaseCRUD):
    @staticmethod
    def create_professor(nombre: str, apellido: str, departamento_id: int, fecha_contratacion: date,
                        especializacion: str = None, salario: float = None, email: str = None):
        try:
            professor = Professor(
                nombre=nombre,
                apellido=apellido,
                departamento_id=departamento_id,
                fecha_contratacion=fecha_contratacion,
                especializacion=especializacion,
                salario=salario,
                email=email
            )
            session.add(professor)
            session.commit()
            session.refresh(professor)
            return professor
        except IntegrityError as e:
            session.rollback()
            raise ValueError("Email must be unique")
        except Exception as e:
            BaseCRUD.handle_error(e, "Error creating professor")

    @staticmethod
    def list_professors():
        try:
            return session.query(Professor).join(Department).order_by(Professor.apellido, Professor.nombre).all()
        except Exception as e:
            BaseCRUD.handle_error(e, "Error listing professors")

    @staticmethod
    def get_professor(professor_id: int):
        try:
            return session.query(Professor).filter(Professor.id == professor_id).first()
        except Exception as e:
            BaseCRUD.handle_error(e, "Error getting professor")

class CourseCRUD(BaseCRUD):
    @staticmethod
    def create_course(codigo: str, nombre: str, creditos: int, carrera_id: int, 
                     descripcion: str = None, prerequisito_id: int = None, departamento_id: int = None):
        try:
            course = Course(
                codigo=codigo,
                nombre=nombre,
                creditos=creditos,
                carrera_id=carrera_id,
                descripcion=descripcion,
                prerequisito_id=prerequisito_id,
                departamento_id=departamento_id
            )
            session.add(course)
            session.commit()
            session.refresh(course)
            return course
        except IntegrityError as e:
            session.rollback()
            raise ValueError("Course code must be unique")
        except Exception as e:
            BaseCRUD.handle_error(e, "Error creating course")

    @staticmethod
    def list_courses():
        try:
            return session.query(Course).join(Major).order_by(Course.codigo).all()
        except Exception as e:
            BaseCRUD.handle_error(e, "Error listing courses")

    @staticmethod
    def get_course(course_id: int):
        try:
            return session.query(Course).filter(Course.id == course_id).first()
        except Exception as e:
            BaseCRUD.handle_error(e, "Error getting course")

class EnrollmentCRUD(BaseCRUD):
    @staticmethod
    def enroll_student(estudiante_id: int, curso_id: int, semestre: str):
        try:
            enrollment = Enrollment(
                estudiante_id=estudiante_id,
                curso_id=curso_id,
                semestre=semestre
            )
            session.add(enrollment)
            session.commit()
            return enrollment
        except IntegrityError as e:
            session.rollback()
            raise ValueError("Student already enrolled in this course for this semester")
        except Exception as e:
            BaseCRUD.handle_error(e, "Error enrolling student")

class UniversityCRUD:
    def __init__(self):
        self.faculty = FacultyCRUD()
        self.student = StudentCRUD()
        self.professor = ProfessorCRUD()
        self.course = CourseCRUD()
        self.enrollment = EnrollmentCRUD()