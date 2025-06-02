'''
            DOCUMENTACIÓN INTERNA


    Autores: 
        Osman de León   // Creación de CRUDS
        Olivier Viau    // Datos de prueba, solución de errores
        Milton Polanco  //Creación de CRUDS
        Adrián González  //Planificador de base de datos


    Objetivo: ste programa es un Sistema de Gestión Universitaria (SGU) completo que maneja todas las operaciones académicas básicas de una universidad. 

    Estructura:
        schema.sql: Estructura de la base de datos con tablas, tipos personalizados, vistas, funciones, triggers e índices.

        models.py: Modelos ORM (SQLAlchemy) que representan las tablas de la base de datos.

        cruds.py: Implementa operaciones CRUD (Create, Read, Update, Delete) para cada entidad del sistema.

        main.py: Interfaz de línea de comandos para interactuar con el sistema.

        reports.py: Genera reportes en formato CSV.

        validation.py: Contiene validaciones y triggers a nivel de aplicación.
'''

from cruds import UniversityCRUD
from models import session
from datetime import datetime
import sys
import os

class UniversitySystem:
    def __init__(self):
        self.crud = UniversityCRUD()
        self.current_user = None
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self, title):
        self.clear_screen()
        print("=" * 50)
        print(f"{title:^50}")
        print("=" * 50)
    
    def display_menu(self, options):
        for key, option in options.items():
            print(f"{key}. {option['label']}")
        print("=" * 50)
    
    def get_input(self, prompt, input_type=str, validation=None):
        while True:
            try:
                value = input(prompt)
                if not value:
                    raise ValueError("Este campo es requerido")
                
                converted = input_type(value)
                
                if validation and not validation(converted):
                    raise ValueError("Valor no válido")
                
                return converted
            except ValueError as e:
                print(f"Error: {str(e)}. Intente nuevamente.")
    
    def main_menu(self):
        while True:
            self.display_header("SISTEMA UNIVERSITARIO")
            options = {
                '1': {'label': 'Gestión Académica', 'action': self.academic_menu},
                '2': {'label': 'Gestión de Estudiantes', 'action': self.student_menu},
                '3': {'label': 'Gestión de Profesores', 'action': self.professor_menu},
                '4': {'label': 'Gestión de Cursos', 'action': self.course_menu},
                '5': {'label': 'Reportes', 'action': self.reports_menu},
                '6': {'label': 'Salir', 'action': sys.exit}
            }
            self.display_menu(options)
            
            choice = input("Seleccione una opción: ")
            if choice in options:
                options[choice]['action']()
            else:
                print("Opción inválida. Intente nuevamente.")
    
    def academic_menu(self):
        self.display_header("GESTIÓN ACADÉMICA")
        options = {
            '1': {'label': 'Gestionar Facultades', 'action': self.faculty_menu},
            '2': {'label': 'Gestionar Departamentos', 'action': self.department_menu},
            '3': {'label': 'Gestionar Carreras', 'action': self.major_menu},
            '4': {'label': 'Gestionar Aulas', 'action': self.classroom_menu},
            '5': {'label': 'Volver al menú principal', 'action': lambda: None}
        }
        self.display_menu(options)
        choice = input("Seleccione una opción: ")
        if choice in options:
            options[choice]['action']()
    
    def faculty_menu(self):
        while True:
            self.display_header("GESTIÓN DE FACULTADES")
            options = {
                '1': {'label': 'Crear Facultad', 'action': self.create_faculty},
                '2': {'label': 'Listar Facultades', 'action': self.list_faculties},
                '3': {'label': 'Buscar Facultad', 'action': self.search_faculty},
                '4': {'label': 'Volver', 'action': lambda: None}
            }
            self.display_menu(options)
            choice = input("Seleccione una opción: ")
            if choice in options:
                options[choice]['action']()
                if choice == '4':
                    break
            else:
                print("Opción inválida. Intente nuevamente.")
    
    def create_faculty(self):
        self.display_header("CREAR NUEVA FACULTAD")
        try:
            name = self.get_input("Nombre de la facultad: ")
            location = self.get_input("Ubicación: ")
            foundation_date = self.get_input("Fecha de fundación (YYYY-MM-DD): ", 
                                          input_type=lambda x: datetime.strptime(x, '%Y-%m-%d').date())
            dean = self.get_input("Decano (opcional): ", required=False)
            
            faculty = self.crud.faculty.create_faculty(
                name=name,
                location=location,
                foundation_date=foundation_date,
                dean=dean
            )
            print(f"\nFacultad '{faculty.name}' creada exitosamente con ID: {faculty.id}")
        except Exception as e:
            print(f"\nError al crear facultad: {str(e)}")
        input("\nPresione Enter para continuar...")
    
    def list_faculties(self):
        self.display_header("LISTADO DE FACULTADES")
        faculties = self.crud.faculty.list_faculties()
        
        if not faculties:
            print("No hay facultades registradas.")
        else:
            print("{:<5} {:<30} {:<20} {:<15}".format("ID", "Nombre", "Ubicación", "Decano"))
            print("-" * 70)
            for faculty in faculties:
                print("{:<5} {:<30} {:<20} {:<15}".format(
                    faculty.id,
                    faculty.name,
                    faculty.location,
                    faculty.dean or "N/A"
                ))
        input("\nPresione Enter para continuar...")
    
    def student_menu(self):
        while True:
            self.display_header("GESTIÓN DE ESTUDIANTES")
            options = {
                '1': {'label': 'Registrar Estudiante', 'action': self.create_student},
                '2': {'label': 'Matricular Estudiante', 'action': self.enroll_student},
                '3': {'label': 'Actualizar Datos', 'action': self.update_student},
                '4': {'label': 'Buscar Estudiante', 'action': self.search_student},
                '5': {'label': 'Listar Estudiantes', 'action': self.list_students},
                '6': {'label': 'Volver', 'action': lambda: None}
            }
            self.display_menu(options)
            choice = input("Seleccione una opción: ")
            if choice in options:
                options[choice]['action']()
                if choice == '6':
                    break
            else:
                print("Opción inválida. Intente nuevamente.")
    
    def create_student(self):
        self.display_header("REGISTRAR NUEVO ESTUDIANTE")
        try:
            first_name = self.get_input("Nombres: ")
            last_name = self.get_input("Apellidos: ")
            birth_date = self.get_input("Fecha de nacimiento (YYYY-MM-DD): ", 
                                       input_type=lambda x: datetime.strptime(x, '%Y-%m-%d').date())
            email = self.get_input("Email institucional: ")
            major_id = self.get_input("ID de carrera (opcional): ", input_type=int, required=False)
            address = self.get_input("Dirección (opcional): ", required=False)
            phone = self.get_input("Teléfono (opcional): ", required=False)
            
            student = self.crud.student.create_student(
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
                email=email,
                major_id=major_id,
                address=address,
                phone=phone
            )
            print(f"\nEstudiante '{first_name} {last_name}' registrado exitosamente con ID: {student.id}")
        except Exception as e:
            print(f"\nError al registrar estudiante: {str(e)}")
        input("\nPresione Enter para continuar...")
    
    def enroll_student(self):
        self.display_header("MATRICULAR ESTUDIANTE")
        try:
            student_id = self.get_input("ID del estudiante: ", input_type=int)
            course_id = self.get_input("ID del curso: ", input_type=int)
            semester = self.get_input("Semestre (Verano/Primer Semestre/Segundo Semestre): ")
            
            enrollment = self.crud.student.enroll_student(
                student_id=student_id,
                course_id=course_id,
                semester=semester
            )
            print(f"\nMatrícula exitosa para el semestre {enrollment.semester}")
        except Exception as e:
            print(f"\nError al matricular estudiante: {str(e)}")
        input("\nPresione Enter para continuar...")
    
    def course_menu(self):
        while True:
            self.display_header("GESTIÓN DE CURSOS")
            options = {
                '1': {'label': 'Crear Curso', 'action': self.create_course},
                '2': {'label': 'Asignar Profesor', 'action': self.assign_professor},
                '3': {'label': 'Programar Horario', 'action': self.schedule_course},
                '4': {'label': 'Listar Cursos', 'action': self.list_courses},
                '5': {'label': 'Volver', 'action': lambda: None}
            }
            self.display_menu(options)
            choice = input("Seleccione una opción: ")
            if choice in options:
                options[choice]['action']()
                if choice == '5':
                    break
            else:
                print("Opción inválida. Intente nuevamente.")
    
    def create_course(self):
        self.display_header("CREAR NUEVO CURSO")
        try:
            code = self.get_input("Código del curso: ")
            name = self.get_input("Nombre del curso: ")
            credits = self.get_input("Créditos: ", input_type=int)
            major_id = self.get_input("ID de la carrera: ", input_type=int)
            description = self.get_input("Descripción (opcional): ", required=False)
            
            course = self.crud.course.create_course(
                code=code,
                name=name,
                credits=credits,
                major_id=major_id,
                description=description
            )
            print(f"\nCurso '{course.name}' creado exitosamente con código: {course.code}")
        except Exception as e:
            print(f"\nError al crear curso: {str(e)}")
        input("\nPresione Enter para continuar...")
    
    def reports_menu(self):
        while True:
            self.display_header("REPORTES")
            options = {
                '1': {'label': 'Estudiantes por Carrera', 'action': self.students_by_major_report},
                '2': {'label': 'Cursos por Semestre', 'action': self.courses_by_semester_report},
                '3': {'label': 'Matrículas Activas', 'action': self.active_enrollments_report},
                '4': {'label': 'Pagos Pendientes', 'action': self.pending_payments_report},
                '5': {'label': 'Volver', 'action': lambda: None}
            }
            self.display_menu(options)
            choice = input("Seleccione una opción: ")
            if choice in options:
                options[choice]['action']()
                if choice == '5':
                    break
            else:
                print("Opción inválida. Intente nuevamente.")
    
    def students_by_major_report(self):
        self.display_header("ESTUDIANTES POR CARRERA")
        try:
            filename = "reporte_estudiantes_carrera.csv"
            print("Generando reporte...")
            
            # Simulación de generación de reporte
            print(f"\nReporte generado exitosamente: {filename}")
            print("Contenido del reporte:")
            print("-" * 50)
            print("ID, Nombre, Carrera, Semestre, Estado")
            print("1, Juan Pérez, Ingeniería, Primer Semestre, Activo")
            print("2, María Gómez, Medicina, Segundo Semestre, Activo")
            print("-" * 50)
        except Exception as e:
            print(f"\nError al generar reporte: {str(e)}")
        input("\nPresione Enter para continuar...")
    
    def run(self):
        try:
            self.main_menu()
        except KeyboardInterrupt:
            print("\n\nSaliendo del sistema...")
        finally:
            session.close()
            sys.exit()

if __name__ == "__main__":
    system = UniversitySystem()
    system.run()