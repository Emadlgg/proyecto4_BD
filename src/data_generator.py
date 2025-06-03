from models import session, Faculty, Department, Major, Student, Professor, Course, Enrollment
from faker import Faker
import random
from datetime import date, datetime

fake = Faker(['es_ES', 'en_US'])  # Usar datos en español e inglés

def clear_existing_data():
    """Limpiar datos existentes si los hay"""
    try:
        session.query(Enrollment).delete()
        session.query(Course).delete()
        session.query(Student).delete()
        session.query(Professor).delete()
        session.query(Major).delete()
        session.query(Department).delete()
        session.query(Faculty).delete()
        session.commit()
        print("✅ Datos existentes limpiados")
    except Exception as e:
        session.rollback()
        print(f"⚠️ Error limpiando datos: {e}")

def generate_faculties():
    """Generar facultades"""
    faculty_names = [
        'Ingeniería', 'Medicina', 'Ciencias', 'Arquitectura', 'Derecho',
        'Economía', 'Psicología', 'Comunicación', 'Arte', 'Educación'
    ]
    
    faculties = []
    for name in faculty_names:
        faculty = Faculty(
            nombre=f"Facultad de {name}",
            ubicacion=f"Edificio {chr(65 + len(faculties))}",  # A, B, C, etc.
            decano=fake.name(),
            telefono=fake.phone_number()[:15],
            fecha_fundacion=fake.date_between(start_date='-50y', end_date='-10y')
        )
        faculties.append(faculty)
        session.add(faculty)
    
    session.commit()
    print(f"✅ {len(faculties)} facultades creadas")
    return faculties

def generate_departments(faculties):
    """Generar departamentos"""
    departments = []
    dept_names = ['Ciencias Básicas', 'Investigación', 'Postgrados', 'Extensión']
    
    for faculty in faculties:
        for dept_name in dept_names[:random.randint(2, 4)]:
            department = Department(
                nombre=f"{dept_name} - {faculty.nombre}",
                facultad_id=faculty.id,
                email=f"{dept_name.lower().replace(' ', '.')}@{faculty.nombre.lower().replace(' ', '')}.uvg.edu.gt"[:100]
            )
            departments.append(department)
            session.add(department)
    
    session.commit()
    print(f"✅ {len(departments)} departamentos creados")
    return departments

def generate_majors(faculties):
    """Generar carreras con duraciones válidas (1-6 años)"""
    major_templates = {
        'Ingeniería': [
            ('Ciencias de la Computación', 'Ingeniería', 5, 200),
            ('Ingeniería Industrial', 'Ingeniería', 5, 190),
            ('Ingeniería Civil', 'Ingeniería', 5, 210),
            ('Ingeniería Mecánica', 'Ingeniería', 5, 200),
            ('Ingeniería Eléctrica', 'Ingeniería', 5, 195)
        ],
        'Medicina': [
            ('Medicina General', 'Licenciatura', 6, 350),  # ← MÁXIMO 6 AÑOS
            ('Enfermería', 'Licenciatura', 4, 160),
            ('Fisioterapia', 'Licenciatura', 4, 150),
            ('Nutrición', 'Licenciatura', 4, 140)
        ],
        'Ciencias': [
            ('Matemática', 'Licenciatura', 4, 160),
            ('Física', 'Licenciatura', 4, 165),
            ('Química', 'Licenciatura', 4, 170),
            ('Biología', 'Licenciatura', 4, 155)
        ],
        'Arquitectura': [
            ('Arquitectura', 'Licenciatura', 5, 220),
            ('Diseño Gráfico', 'Licenciatura', 4, 140),
            ('Diseño Industrial', 'Licenciatura', 4, 150)
        ],
        'Derecho': [
            ('Derecho', 'Licenciatura', 5, 180),
            ('Ciencias Políticas', 'Licenciatura', 4, 140)
        ],
        'Economía': [
            ('Economía', 'Licenciatura', 4, 150),
            ('Administración de Empresas', 'Licenciatura', 4, 145),
            ('Contaduría Pública', 'Licenciatura', 4, 140)
        ],
        'Psicología': [
            ('Psicología Clínica', 'Licenciatura', 5, 180),
            ('Psicología Organizacional', 'Licenciatura', 4, 150)
        ],
        'Comunicación': [
            ('Comunicación Social', 'Licenciatura', 4, 130),
            ('Periodismo', 'Licenciatura', 4, 135),
            ('Publicidad', 'Licenciatura', 4, 130)
        ],
        'Arte': [
            ('Bellas Artes', 'Licenciatura', 4, 120),
            ('Música', 'Licenciatura', 4, 125),
            ('Teatro', 'Licenciatura', 4, 120)
        ],
        'Educación': [
            ('Pedagogía', 'Licenciatura', 4, 140),
            ('Educación Primaria', 'Licenciatura', 3, 120),
            ('Educación Especial', 'Licenciatura', 4, 145)
        ]
    }
    
    majors = []
    for faculty in faculties:
        faculty_key = faculty.nombre.replace('Facultad de ', '')
        if faculty_key in major_templates:
            for major_name, titulo, duracion, creditos in major_templates[faculty_key]:
                # Validar duración (probablemente 1-6 años)
                if duracion < 1 or duracion > 6:
                    duracion = 4  # Valor por defecto seguro
                
                major = Major(
                    nombre=major_name,
                    facultad_id=faculty.id,
                    titulo=titulo,
                    duracion_anos=duracion,
                    creditos_totales=creditos
                )
                majors.append(major)
                session.add(major)
    
    session.commit()
    print(f"✅ {len(majors)} carreras creadas")
    return majors

def generate_professors(departments):
    """Generar profesores"""
    professors = []
    for _ in range(200):  # 200 profesores
        department = random.choice(departments)
        professor = Professor(
            nombre=fake.first_name(),
            apellido=fake.last_name(),
            especializacion=fake.job(),
            departamento_id=department.id,
            fecha_contratacion=fake.date_between(start_date='-20y', end_date='today'),
            salario=round(random.uniform(15000, 50000), 2),
            email=fake.unique.email(),
            activo=random.choice([True, True, True, False])  # 75% activos
        )
        professors.append(professor)
        session.add(professor)
        
        # Commit cada 50 registros para evitar problemas de memoria
        if len(professors) % 50 == 0:
            session.commit()
    
    session.commit()
    print(f"✅ {len(professors)} profesores creados")
    return professors

def generate_students(majors):
    """Generar estudiantes"""
    students = []
    major_ids = [major.id for major in majors]
    
    for i in range(1000):  # 1000 estudiantes
        major_id = random.choice(major_ids) if random.random() > 0.1 else None  # 10% sin carrera
        
        student = Student(
            nombre=fake.first_name(),
            apellido=fake.last_name(),
            fecha_nacimiento=fake.date_between(start_date='-30y', end_date='-18y'),
            direccion=fake.address()[:200],  # Limitar longitud
            telefono=fake.phone_number()[:15],
            email=fake.unique.email(),
            carrera_id=major_id,
            fecha_ingreso=fake.date_between(start_date='-5y', end_date='today'),
            estado=random.choice(['Activo', 'Activo', 'Activo', 'Inactivo', 'Graduado'])  # Más activos
        )
        students.append(student)
        session.add(student)
        
        # Commit cada 100 registros
        if (i + 1) % 100 == 0:
            session.commit()
            print(f"  📝 {i + 1} estudiantes procesados...")
    
    session.commit()
    print(f"✅ {len(students)} estudiantes creados")
    return students

def generate_courses(majors):
    """Generar cursos"""
    courses = []
    course_prefixes = ['MAT', 'FIS', 'QUI', 'BIO', 'ING', 'MED', 'DER', 'ECO', 'PSI', 'COM']
    
    for major in majors:
        # 5-10 cursos por carrera
        for i in range(random.randint(5, 10)):
            prefix = random.choice(course_prefixes)
            code = f"{prefix}{random.randint(1000, 9999)}"
            
            course = Course(
                codigo=code,
                nombre=fake.catch_phrase()[:100],
                creditos=random.randint(1, 6),
                descripcion=fake.text(max_nb_chars=500),
                carrera_id=major.id
            )
            courses.append(course)
            session.add(course)
    
    session.commit()
    print(f"✅ {len(courses)} cursos creados")
    return courses

def generate_enrollments(students, courses):
    """Generar matrículas"""
    enrollments = []
    # Usar los valores EXACTOS del ENUM tipo_semestre
    semesters = ['Primer Semestre', 'Segundo Semestre', 'Verano']  # ← VALORES CORRECTOS
    grades = ['A', 'B', 'C', 'D', 'F', None]  # None para cursos en progreso
    estados = ['Activa', 'Finalizada', 'Retirada']  # Usar valores del ENUM estado_matricula
    
    active_students = [s for s in students if s.estado == 'Activo']
    
    for student in active_students[:500]:  # Solo 500 estudiantes activos
        # Cada estudiante se matricula en 3-6 cursos
        student_courses = random.sample(courses, min(random.randint(3, 6), len(courses)))
        
        for course in student_courses:
            enrollment = Enrollment(
                estudiante_id=student.id,
                curso_id=course.id,
                semestre=random.choice(semesters),  # Usar valores válidos del ENUM
                calificacion=random.choice(grades),
                estado=random.choice(estados),      # Usar valores válidos del ENUM
                fecha_matricula=fake.date_time_between(start_date='-2y', end_date='now')
            )
            enrollments.append(enrollment)
            session.add(enrollment)
    
    try:
        session.commit()
        print(f"✅ {len(enrollments)} matrículas creadas")
    except Exception as e:
        session.rollback()
        print(f"⚠️ Error creando matrículas: {e}")
    
    return enrollments

def main():
    """Función principal para generar todos los datos"""
    print("🚀 Iniciando generación de datos de prueba...")
    
    # 1. Limpiar datos existentes
    clear_existing_data()
    
    # 2. Generar en orden correcto (respetando foreign keys)
    faculties = generate_faculties()
    departments = generate_departments(faculties)
    majors = generate_majors(faculties)
    professors = generate_professors(departments)
    students = generate_students(majors)
    courses = generate_courses(majors)
    enrollments = generate_enrollments(students, courses)
    
    # 3. Resumen final
    print("\n📊 RESUMEN DE DATOS GENERADOS:")
    print(f"  • Facultades: {len(faculties)}")
    print(f"  • Departamentos: {len(departments)}")
    print(f"  • Carreras: {len(majors)}")
    print(f"  • Profesores: {len(professors)}")
    print(f"  • Estudiantes: {len(students)}")
    print(f"  • Cursos: {len(courses)}")
    print(f"  • Matrículas: {len(enrollments)}")
    print(f"  📈 TOTAL: {len(faculties) + len(departments) + len(majors) + len(professors) + len(students) + len(courses) + len(enrollments)} registros")
    
    print("\n✅ Generación de datos completada exitosamente!")
    print("🎯 Ahora tienes más de 1000 registros de prueba coherentes y variados.")

if __name__ == "__main__":
    main()