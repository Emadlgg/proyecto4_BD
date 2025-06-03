from models import session, Student, Faculty, Course, Major, Enrollment
from sqlalchemy import func, and_, or_
import csv
from datetime import datetime, date
from typing import List, Dict, Any
import os

class ReportGenerator:
    REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'reports')
    
    @classmethod
    def ensure_reports_directory(cls):
        """Crear directorio de reportes si no existe"""
        if not os.path.exists(cls.REPORTS_DIR):
            os.makedirs(cls.REPORTS_DIR)
        return cls.REPORTS_DIR
    
    @staticmethod
    def student_enrollment_report(output_file: str = "student_enrollments.csv", **filters):
        """Genera reporte de matriculas con múltiples filtros"""
        query = session.query(
            Student.id.label("student_id"),
            Student.first_name,
            Student.last_name,
            Course.code.label("course_code"),
            Course.name.label("course_name"),
            Enrollment.semester,
            Enrollment.grade
        ).join(
            Enrollment, Student.id == Enrollment.student_id
        ).join(
            Course, Enrollment.course_id == Course.id
        )
        
        # Aplicar filtros dinámicos
        if 'semester' in filters:
            query = query.filter(Enrollment.semester == filters['semester'])
        if 'major_id' in filters:
            query = query.filter(Student.major_id == filters['major_id'])
        if 'min_credits' in filters:
            query = query.filter(Course.credits >= filters['min_credits'])
        
        results = query.all()
        
        # Exportar a CSV
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ID Estudiante', 'Nombre', 'Apellido', 'Código Curso', 
                           'Nombre Curso', 'Semestre', 'Calificación'])
            
            for row in results:
                writer.writerow([
                    row.student_id,
                    row.first_name,
                    row.last_name,
                    row.course_code,
                    row.course_name,
                    row.semester,
                    row.grade.value if row.grade else 'N/A'
                ])
        
        return f"Reporte generado en {output_file}"

    @staticmethod
    def department_statistics_report() -> Dict[str, Any]:
        """Reporte estadístico por departamento"""
        stats = session.query(
            Department.name,
            func.count(Professor.id).label("professor_count"),
            func.avg(Professor.salary).label("avg_salary"),
            func.count(Course.id).label("course_count")
        ).join(
            Professor, Department.id == Professor.department_id
        ).join(
            Course, Department.id == Course.department_id
        ).group_by(
            Department.name
        ).all()
        
        return [{
            "department": row.name,
            "professors": row.professor_count,
            "avg_salary": float(row.avg_salary) if row.avg_salary else 0,
            "courses": row.course_count
        } for row in stats]

    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str):
        """Exporta cualquier conjunto de datos a CSV"""
        if not data:
            raise ValueError("No hay datos para exportar")
            
        keys = data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        
        return f"Datos exportados a {filename}"
    
    @staticmethod
    def students_by_faculty_report(faculty_id=None, status=None, year_from=None, year_to=None, age_min=None):
        """Reporte de estudiantes por facultad con 5 filtros"""
        try:
            query = session.query(
                Student.id,
                Student.nombre,
                Student.apellido,
                Major.nombre.label('carrera'),
                Faculty.nombre.label('facultad'),
                Student.fecha_ingreso,
                Student.estado
            ).join(Major, Student.carrera_id == Major.id)\
             .join(Faculty, Major.facultad_id == Faculty.id)
            
            # Filtro 1: Por facultad
            if faculty_id:
                query = query.filter(Faculty.id == faculty_id)
            
            # Filtro 2: Por estado
            if status:
                query = query.filter(Student.estado == status)
            
            # Filtro 3: Por año de ingreso (desde)
            if year_from:
                query = query.filter(Student.fecha_ingreso >= date(year_from, 1, 1))
            
            # Filtro 4: Por año de ingreso (hasta)
            if year_to:
                query = query.filter(Student.fecha_ingreso <= date(year_to, 12, 31))
            
            # Filtro 5: Por edad mínima
            if age_min:
                birth_year = datetime.now().year - age_min
                query = query.filter(Student.fecha_nacimiento <= date(birth_year, 12, 31))
            
            return query.all()
            
        except Exception as e:
            raise ValueError(f"Error generating report: {str(e)}")

    @staticmethod
    def courses_by_semester_report(semester=None, faculty_id=None, min_credits=None, max_students=None, professor_id=None):
        """Reporte de cursos por semestre con 5 filtros"""
        try:
            query = session.query(
                Course.id,
                Course.codigo,
                Course.nombre,
                Course.creditos,
                Major.nombre.label('carrera'),
                Faculty.nombre.label('facultad'),
                func.count(Enrollment.estudiante_id).label('total_estudiantes')
            ).join(Major, Course.carrera_id == Major.id)\
             .join(Faculty, Major.facultad_id == Faculty.id)\
             .outerjoin(Enrollment, Course.id == Enrollment.curso_id)
            
            # Filtro 1: Por semestre
            if semester:
                query = query.filter(Enrollment.semestre == semester)
            
            # Filtro 2: Por facultad
            if faculty_id:
                query = query.filter(Faculty.id == faculty_id)
            
            # Filtro 3: Por créditos mínimos
            if min_credits:
                query = query.filter(Course.creditos >= min_credits)
            
            # Filtro 4: Por máximo número de estudiantes
            query = query.group_by(Course.id, Course.codigo, Course.nombre, Course.creditos, Major.nombre, Faculty.nombre)
            
            if max_students:
                query = query.having(func.count(Enrollment.estudiante_id) <= max_students)
            
            # Filtro 5: Por profesor (si tienes asignación de profesores)
            # if professor_id:
            #     query = query.join(CourseAssignment).filter(CourseAssignment.profesor_id == professor_id)
            
            return query.all()
            
        except Exception as e:
            raise ValueError(f"Error generating courses report: {str(e)}")

    @staticmethod
    def professors_by_department_report(department_id=None, min_salary=None, max_salary=None, active_only=None, hire_year=None):
        """Reporte de profesores por departamento con 5 filtros"""
        try:
            query = session.query(
                Professor.id,
                Professor.nombre,
                Professor.apellido,
                Professor.especializacion,
                Professor.salario,
                Professor.fecha_contratacion,
                Professor.activo,
                Department.nombre.label('departamento'),
                Faculty.nombre.label('facultad')
            ).join(Department, Professor.departamento_id == Department.id)\
             .join(Faculty, Department.facultad_id == Faculty.id)
            
            # Filtro 1: Por departamento
            if department_id:
                query = query.filter(Department.id == department_id)
            
            # Filtro 2: Por salario mínimo
            if min_salary:
                query = query.filter(Professor.salario >= min_salary)
            
            # Filtro 3: Por salario máximo
            if max_salary:
                query = query.filter(Professor.salario <= max_salary)
            
            # Filtro 4: Solo activos
            if active_only:
                query = query.filter(Professor.activo == True)
            
            # Filtro 5: Por año de contratación
            if hire_year:
                query = query.filter(func.extract('year', Professor.fecha_contratacion) == hire_year)
            
            return query.all()
            
        except Exception as e:
            raise ValueError(f"Error generating professors report: {str(e)}")

    @staticmethod
    def export_to_csv(data, filename: str):
        """Exportar datos a CSV en carpeta específica"""
        if not data:
            raise ValueError("No hay datos para exportar")
        
        # Asegurar que existe el directorio
        reports_dir = ReportGenerator.ensure_reports_directory()
        
        # Ruta completa del archivo
        full_path = os.path.join(reports_dir, filename)
        
        with open(full_path, 'w', newline='', encoding='utf-8') as file:
            if hasattr(data[0], '_fields'):  # Named tuple
                fieldnames = data[0]._fields
            else:  # SQLAlchemy result
                fieldnames = data[0].keys()
            
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in data:
                if hasattr(row, '_asdict'):
                    writer.writerow(row._asdict())
                else:
                    writer.writerow(dict(row._asdict() if hasattr(row, '_asdict') else row))
        
        return f"Datos exportados a {full_path}"