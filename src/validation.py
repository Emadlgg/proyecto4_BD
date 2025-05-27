from models import session, Student, Enrollment, Schedule, Classroom
from sqlalchemy import event
from datetime import time
from typing import Optional

class Validations:
    @staticmethod
    def validate_classroom_availability(classroom_id: int, day: str, start_time: time, end_time: time) -> bool:
        """Valida que el aula no esté ocupada en el horario seleccionado"""
        conflicting_schedules = session.query(Schedule).filter(
            Schedule.classroom_id == classroom_id,
            Schedule.day == day,
            Schedule.start_time < end_time,
            Schedule.end_time > start_time
        ).count()
        
        return conflicting_schedules == 0

    @staticmethod
    def validate_student_enrollment_limit(student_id: int, semester: str, max_courses: int = 6) -> bool:
        """Valida que el estudiante no exceda el límite de cursos por semestre"""
        current_enrollments = session.query(Enrollment).filter(
            Enrollment.student_id == student_id,
            Enrollment.semester == semester
        ).count()
        
        return current_enrollments < max_courses

# Triggers a nivel de aplicación
@event.listens_for(Enrollment, 'before_insert')
def validate_enrollment(mapper, connection, target):
    """Trigger para validar matrícula antes de insertar"""
    validator = Validations()
    
    # Verificar límite de cursos
    if not validator.validate_student_enrollment_limit(target.student_id, target.semester):
        raise ValueError("El estudiante ha alcanzado el límite de cursos para este semestre")
    
    # Verificar que el curso tenga aula asignada
    course_schedules = session.query(Schedule).filter_by(course_id=target.course_id).count()
    if course_schedules == 0:
        raise ValueError("El curso no tiene horarios asignados")

@event.listens_for(Schedule, 'before_insert')
def validate_schedule(mapper, connection, target):
    """Trigger para validar horario antes de insertar"""
    validator = Validations()
    
    # Verificar disponibilidad de aula
    if not validator.validate_classroom_availability(
        target.classroom_id, 
        target.day, 
        target.start_time, 
        target.end_time
    ):
        raise ValueError("El aula ya está ocupada en este horario")
    
    # Verificar capacidad del aula
    classroom = session.query(Classroom).get(target.classroom_id)
    course_enrollments = session.query(Enrollment).filter_by(
        course_id=target.course_id,
        semester=target.semester
    ).count()
    
    if course_enrollments > classroom.capacity:
        raise ValueError("El aula no tiene capacidad para todos los estudiantes inscritos")