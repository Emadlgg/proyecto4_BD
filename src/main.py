'''
            DOCUMENTACIÓN INTERNA


    Autores: 
        Osman de León   // Creación de CRUDS
        Olivier Viau    // Datos de prueba, solución de errores
        Milton Polanco  //Creación de CRUDS
        Adrián Gonzáles  //Planificador de base de datos


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
    
    def get_input(self, prompt, input_type=str, validation=None, required=True):
        while True:
            try:
                value = input(prompt)
                if not value and required:
                    raise ValueError("Este campo es requerido")
                elif not value and not required:
                    return None
                
                converted = input_type(value) if value else None
                
                if validation and converted is not None and not validation(converted):
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
            # CAMBIAR: usar .nombre en lugar de .name
            print(f"\nFacultad '{faculty.nombre}' creada exitosamente con ID: {faculty.id}")
        except Exception as e:
            print(f"\nError al crear facultad: {str(e)}")
        input("\nPresione Enter para continuar...")
    
    def list_faculties(self):
        self.display_header("LISTADO DE FACULTADES")
        faculties = self.crud.faculty.list_faculties()
        
        if not faculties:
            print("No hay facultades registradas.")
        else:
            print("{:<5} {:<30} {:<20} {:<15} {:<15}".format("ID", "Nombre", "Ubicación", "Fundación", "Decano"))
            print("-" * 85)
            for faculty in faculties:
                foundation_date = faculty.fecha_fundacion.strftime('%Y-%m-%d') if faculty.fecha_fundacion else 'N/A'
                print("{:<5} {:<30} {:<20} {:<15} {:<15}".format(
                    faculty.id,
                    faculty.nombre,
                    faculty.ubicacion,
                    foundation_date,
                    faculty.decano or "N/A"
                ))
        input("\nPresione Enter para continuar...")
    
    def search_faculty(self):
        self.display_header("BUSCAR FACULTAD")
        try:
            faculty_id = self.get_input("ID de la facultad: ", input_type=int)
            faculty = self.crud.faculty.get_faculty(faculty_id)
            
            if faculty:
                print(f"\nFacultad encontrada:")
                print(f"ID: {faculty.id}")
                print(f"Nombre: {faculty.nombre}")
                print(f"Ubicación: {faculty.ubicacion}")
                print(f"Decano: {faculty.decano or 'N/A'}")
            else:
                print("Facultad no encontrada.")
        except Exception as e:
            print(f"\nError al buscar facultad: {str(e)}")
        input("\nPresione Enter para continuar...")

    def department_menu(self):
        print("Funcionalidad de departamentos en desarrollo...")
        input("\nPresione Enter para continuar...")

    def major_menu(self):
        print("Funcionalidad de carreras en desarrollo...")
        input("\nPresione Enter para continuar...")

    def classroom_menu(self):
        print("Funcionalidad de aulas en desarrollo...")
        input("\nPresione Enter para continuar...")

    def professor_menu(self):
        print("Funcionalidad de profesores en desarrollo...")
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
                # CAMBIAR: usar los nombres correctos de los parámetros
                nombre=first_name,
                apellido=last_name,
                fecha_nacimiento=birth_date,
                email=email,
                carrera_id=major_id,
                direccion=address,
                telefono=phone
            )
            print(f"\nEstudiante '{student.nombre} {student.apellido}' registrado exitosamente con ID: {student.id}")
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
    
    def update_student(self):
        self.display_header("ACTUALIZAR ESTUDIANTE")
        try:
            student_id = self.get_input("ID del estudiante a actualizar: ", input_type=int)
            student = self.crud.student.get_student(student_id)
            
            if not student:
                print("Estudiante no encontrado.")
                return
                
            print(f"\nEstudiante actual: {student.nombre} {student.apellido}")
            print("Deje en blanco los campos que no desea modificar:")
            
            nombre = self.get_input(f"Nombres ({student.nombre}): ", required=False) or student.nombre
            apellido = self.get_input(f"Apellidos ({student.apellido}): ", required=False) or student.apellido
            email = self.get_input(f"Email ({student.email}): ", required=False) or student.email
            
            updated_student = self.crud.student.update_student(
                student_id, 
                nombre=nombre, 
                apellido=apellido, 
                email=email
            )
            print(f"\n✅ Estudiante actualizado: {updated_student.nombre} {updated_student.apellido}")
            
        except Exception as e:
            print(f"\n❌ Error al actualizar estudiante: {str(e)}")
        input("\nPresione Enter para continuar...")

    def search_student(self):
        print("Funcionalidad de búsqueda de estudiantes en desarrollo...")
        input("\nPresione Enter para continuar...")

    def list_students(self):
        self.display_header("LISTADO DE ESTUDIANTES")
        try:
            students = self.crud.student.list_students()
            
            if not students:
                print("No hay estudiantes registrados.")
            else:
                print("{:<5} {:<20} {:<20} {:<30} {:<15}".format("ID", "Nombres", "Apellidos", "Email", "Carrera"))
                print("-" * 90)
                for student in students:
                    carrera_nombre = student.major.nombre if student.major else "Sin carrera"
                    print("{:<5} {:<20} {:<20} {:<30} {:<15}".format(
                        student.id,
                        student.nombre,
                        student.apellido,
                        student.email,
                        carrera_nombre
                    ))
        except Exception as e:
            print(f"\n❌ Error al listar estudiantes: {str(e)}")
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
                codigo=code,
                nombre=name,
                creditos=credits,
                carrera_id=major_id,
                descripcion=description
            )
            print(f"\nCurso '{course.nombre}' creado exitosamente con código: {course.codigo}")
        except Exception as e:
            print(f"\nError al crear curso: {str(e)}")
        input("\nPresione Enter para continuar...")
    
    def assign_professor(self):
        print("Funcionalidad de asignación de profesores en desarrollo...")
        input("\nPresione Enter para continuar...")

    def schedule_course(self):
        print("Funcionalidad de programación de horarios en desarrollo...")
        input("\nPresione Enter para continuar...")

    def list_courses(self):
        print("Funcionalidad de listado de cursos en desarrollo...")
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
            from reports import ReportGenerator
            
            print("Filtros disponibles (deje en blanco para omitir):")
            major_id = self.get_input("ID de carrera: ", input_type=int, required=False)
            status = self.get_input("Estado: ", required=False)
            year_from = self.get_input("Año desde: ", input_type=int, required=False)
            year_to = self.get_input("Año hasta: ", input_type=int, required=False)
            age_min = self.get_input("Edad mínima: ", input_type=int, required=False)
            
            # ALTERNATIVA: Si no hay datos, crear datos de ejemplo
            data = ReportGenerator.students_by_faculty_report(
                faculty_id=major_id,
                status=status,
                year_from=year_from,
                year_to=year_to,
                age_min=age_min
            )
            
            if not data:
                print("⚠️ No hay datos reales. Generando datos de ejemplo...")
                # Crear datos de ejemplo para demostración
                sample_data = [
                    {
                        'id': 1,
                        'nombre': 'Juan',
                        'apellido': 'Pérez',
                        'carrera': 'Ciencias de la Computación',
                        'facultad': 'Ingeniería',
                        'fecha_ingreso': '2023-01-15',
                        'estado': 'Activo'
                    },
                    {
                        'id': 2,
                        'nombre': 'María',
                        'apellido': 'González',
                        'carrera': 'Medicina General',
                        'facultad': 'Medicina',
                        'fecha_ingreso': '2023-01-20',
                        'estado': 'Activo'
                    }
                ]
                
                filename = f"estudiantes_carrera_ejemplo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    if sample_data:
                        writer = csv.DictWriter(file, fieldnames=sample_data[0].keys())
                        writer.writeheader()
                        writer.writerows(sample_data)
                
                print(f"\n✅ Datos de ejemplo exportados: {filename}")
                print("📝 Nota: Este es un reporte de demostración con datos sintéticos")
            else:
                filename = f"estudiantes_carrera_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                ReportGenerator.export_to_csv(data, filename)
                print(f"\n✅ Reporte exportado: {filename}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        input("\nPresione Enter para continuar...")

    def courses_by_semester_report(self):
        self.display_header("CURSOS POR SEMESTRE")
        print("✅ Generando reporte de ejemplo...")
        
        # Datos de ejemplo para demostración
        sample_data = [
            {
                'curso_id': 1,
                'codigo': 'CC3001',
                'nombre': 'Algoritmos y Estructuras de Datos',
                'creditos': 4,
                'semestre': 'Primer Semestre',
                'estudiantes_matriculados': 25
            },
            {
                'curso_id': 2,
                'codigo': 'CC3088',
                'nombre': 'Bases de Datos',
                'creditos': 4,
                'semestre': 'Primer Semestre',
                'estudiantes_matriculados': 30
            }
        ]
        
        filename = f"cursos_semestre_ejemplo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=sample_data[0].keys())
            writer.writeheader()
            writer.writerows(sample_data)
        
        print(f"\n✅ Reporte de ejemplo exportado: {filename}")
        print("📝 Nota: Este es un reporte de demostración con datos sintéticos")
        input("\nPresione Enter para continuar...")

    def active_enrollments_report(self):
        self.display_header("MATRÍCULAS ACTIVAS")
        print("✅ Generando reporte de ejemplo...")
        
        # Datos de ejemplo
        sample_data = [
            {
                'matricula_id': 1,
                'estudiante_nombre': 'Juan Pérez',
                'curso_nombre': 'Bases de Datos',
                'semestre': 'Primer Semestre',
                'estado': 'Activa',
                'fecha_matricula': '2025-01-15'
            },
            {
                'matricula_id': 2,
                'estudiante_nombre': 'María González',
                'curso_nombre': 'Algoritmos',
                'semestre': 'Primer Semestre',
                'estado': 'Activa',
                'fecha_matricula': '2025-01-16'
            }
        ]
        
        filename = f"matriculas_activas_ejemplo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=sample_data[0].keys())
            writer.writeheader()
            writer.writerows(sample_data)
        
        print(f"\n✅ {len(sample_data)} matrículas de ejemplo exportadas: {filename}")
        print("📝 Nota: Este es un reporte de demostración con datos sintéticos")
        input("\nPresione Enter para continuar...")

    def pending_payments_report(self):
        print("Reporte de pagos pendientes en desarrollo...")
        input("\nPresione Enter para continuar...")
    
    def students_faculty_report(self):
        self.display_header("REPORTE: ESTUDIANTES POR FACULTAD")
        try:
            from reports import ReportGenerator
            
            # Obtener filtros del usuario
            print("Filtros disponibles (deje en blanco para omitir):")
            faculty_id = self.get_input("ID de facultad: ", input_type=int, required=False)
            status = self.get_input("Estado (Activo/Inactivo/Graduado): ", required=False)
            year_from = self.get_input("Año de ingreso desde: ", input_type=int, required=False)
            year_to = self.get_input("Año de ingreso hasta: ", input_type=int, required=False)
            age_min = self.get_input("Edad mínima: ", input_type=int, required=False)
            
            # Generar reporte
            data = ReportGenerator.students_by_faculty_report(
                faculty_id=faculty_id,
                status=status,
                year_from=year_from,
                year_to=year_to,
                age_min=age_min
            )
            
            if data:
                print(f"\n✅ Se encontraron {len(data)} estudiantes.")
                
                # Mostrar preview de los primeros 5 registros
                print("\nVista previa (primeros 5 registros):")
                print("-" * 80)
                for i, row in enumerate(data[:5]):
                    print(f"{i+1}. {row.nombre} {row.apellido} - {row.facultad} - {row.estado}")
                
                if len(data) > 5:
                    print(f"... y {len(data) - 5} registros más")
                
                # Exportar a CSV
                filename = f"estudiantes_facultad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                result_message = ReportGenerator.export_to_csv(data, filename)
                print(f"\n📄 {result_message}")
            else:
                print("❌ No se encontraron datos con los filtros especificados.")
                
        except Exception as e:
            print(f"❌ Error generando reporte: {str(e)}")
        
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