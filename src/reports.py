from models import session, Student, Course, Enrollment, Department
from sqlalchemy import func, and_, or_
import csv
from datetime import datetime
from typing import Dict, Any, List

class ReportGenerator:
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