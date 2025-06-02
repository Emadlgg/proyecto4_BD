
'''
pip install faker names sqlalchemy python-dotenv

python mock_data.py


'''

import random
from datetime import datetime, timedelta
from models import session, Faculty, Department, Major, Student, Professor, Course, Classroom, Enrollment, Schedule, CourseAssignment, Book, BookLoan, Payment, Scholarship, AcademicEvent, Evaluation, Thesis
from cruds import UniversityCRUD
import names
from faker import Faker

fake = Faker()
crud = UniversityCRUD()

def generate_test_data():
    print("Generando datos de prueba...")
    
    faculties = []
    faculty_names = ["Ingeniería", "Ciencias", "Humanidades", "Medicina", "Derecho"]
    for name in faculty_names:
        faculty = crud.faculty.create_faculty(
            name=name,
            location=fake.building_number(),
            foundation_date=fake.date_between(start_date='-50y', end_date='-10y'),
            dean=fake.name()
        )
        faculties.append(faculty)

    departments = []
    for faculty in faculties:
        for i in range(5):
            dept = crud.department.create_department(
                name=f"Departamento de {fake.bs().title()}",
                faculty_id=faculty.id,
                budget=random.randint(50000, 500000),
                head=fake.name()
            )
            departments.append(dept)

    majors = []
    degree_types = ["Licenciatura", "Maestría", "Doctorado", "Técnico", "Bachillerato"]
    for faculty in faculties:
        for i in range(3):
            major = crud.major.create_major(
                name=f"{degree_types[i]} en {fake.job().title()}",
                faculty_id=faculty.id,
                duration_years=random.choice([3, 4, 5]),
                total_credits=random.randint(120, 300)
            )
            majors.append(major)

    professors = []
    for dept in departments:
        for i in range(20):
            prof = Professor(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                specialization=fake.job(),
                department_id=dept.id,
                hire_date=fake.date_between(start_date='-20y', end_date='-1y'),
                salary=random.randint(5000, 15000),
                email=fake.email(),
                is_active=random.choice([True, False])
            )
            session.add(prof)
            professors.append(prof)
    session.commit()
    

    students = []
    for i in range(1000):
        student = crud.student.create_student(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            birth_date=fake.date_of_birth(minimum_age=16, maximum_age=40),
            email=fake.unique.email(),
            major_id=random.choice(majors).id if random.random() > 0.1 else None,
            address=fake.address(),
            phone=fake.phone_number()
        )
        students.append(student)

    courses = []
    for major in majors:
        for i in range(10):
            course = crud.course.create_course(
                code=f"{major.name[:3].upper()}{random.randint(100, 999)}",
                name=f"Curso de {fake.bs().title()}",
                credits=random.choice([3, 4, 5]),
                major_id=major.id,
                description=fake.text(),
                department_id=random.choice(departments).id,
                prerequisite_id=random.choice(courses).id if courses and random.random() > 0.7 else None
            )
            courses.append(course)

    classrooms = []
    building_names = ["A", "B", "C", "D", "E", "F", "G", "H"]
    for i in range(50):
        classroom = crud.classroom.create_classroom(
            code=f"{random.choice(building_names)}{random.randint(100, 999)}",
            building=random.choice(building_names),
            capacity=random.choice([20, 30, 40, 50, 100]),
            classroom_type=random.choice(["Teoría", "Laboratorio", "Auditorio"]),
            has_projector=random.choice([True, False]),
            has_computers=random.choice([True, False])
        )
        classrooms.append(classroom)

    semesters = ["Verano", "Primer Semestre", "Segundo Semestre"]
    current_semester = random.choice(semesters)
    assignments = []
    for course in courses:
        for i in range(3):
            assignment = crud.course.assign_professor(
                course_id=course.id,
                professor_id=random.choice(professors).id,
                semester=current_semester,
                is_coordinator=(i == 0)
            )
            assignments.append(assignment)
    

    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    schedules = []
    for course in courses:
        for i in range(2):
            start_hour = random.randint(7, 18)
            schedule = crud.schedule.create_schedule(
                course_id=course.id,
                classroom_id=random.choice(classrooms).id,
                day=random.choice(days),
                start_time=f"{start_hour}:00",
                end_time=f"{start_hour + 2}:00"
            )
            schedules.append(schedule)
    

    grades = ["A", "B", "C", "D", "F", "NP"]
    enrollments = []
    for student in students:
        num_courses = random.randint(5, 8)
        for i in range(num_courses):
            course = random.choice(courses)
            enrollment = crud.student.enroll_student(
                student_id=student.id,
                course_id=course.id,
                semester=current_semester
            )
            

            if random.random() > 0.2:
                enrollment.grade = random.choice(grades)
                session.commit()
            
            enrollments.append(enrollment)
    
 
    books = []
    for i in range(200):
        book = crud.book.create_book(
            title=fake.sentence(nb_words=4),
            author=fake.name(),
            isbn=fake.isbn13(),
            publisher=fake.company(),
            publication_year=random.randint(1990, 2023),
            edition=str(random.randint(1, 5))
        )
        books.append(book)

    loans = []
    for i in range(300):
        student = random.choice(students)
        book = random.choice(books)
        loan_date = fake.date_between(start_date='-1y', end_date='today')
        due_date = loan_date + timedelta(days=14)
        return_date = loan_date + timedelta(days=random.randint(1, 21)) if random.random() > 0.2 else None
        
        loan = BookLoan(
            book_id=book.id,
            student_id=student.id,
            loan_date=loan_date,
            due_date=due_date,
            return_date=return_date,
            fine=random.randint(0, 50) if return_date and return_date > due_date else 0
        )
        session.add(loan)
        loans.append(loan)
    session.commit()
    

    payments = []
    payment_types = ["Matrícula", "Multa", "Donación"]
    for student in students:
        for i in range(5):
            payment = crud.payment.create_payment(
                student_id=student.id,
                amount=random.randint(100, 5000),
                payment_type=random.choice(payment_types),
                description=fake.sentence(),
                reference_number=fake.unique.bothify(text='PAY-########')
            )
            payments.append(payment)

    scholarships = []
    for student in random.sample(students, int(len(students)*0.1)):
        scholarship = Scholarship(
            name=f"Beca {fake.word().title()}",
            percentage=random.choice([25, 50, 75, 100]),
            student_id=student.id,
            start_date=fake.date_between(start_date='-1y', end_date='today'),
            end_date=fake.date_between(start_date='today', end_date='+1y') if random.random() > 0.3 else None,
            requirements=fake.text()
        )
        session.add(scholarship)
        scholarships.append(scholarship)
    session.commit()
    
    theses = []
    thesis_statuses = ["En progreso", "Finalizada", "Aprobada", "Reprobada"]
    for student in random.sample(students, int(len(students)*0.05)):
        thesis = Thesis(
            title=f"Estudio sobre {fake.sentence(nb_words=3)}",
            student_id=student.id,
            advisor_id=random.choice(professors).id,
            status=random.choice(thesis_statuses),
            grade=random.uniform(6, 10) if random.random() > 0.3 else None,
            file_url=fake.url()
        )
        session.add(thesis)
        theses.append(thesis)
    session.commit()
    
    print(f"Datos de prueba generados exitosamente:")
    print(f"- {len(faculties)} facultades")
    print(f"- {len(departments)} departamentos")
    print(f"- {len(majors)} carreras")
    print(f"- {len(professors)} profesores")
    print(f"- {len(students)} estudiantes")
    print(f"- {len(courses)} cursos")
    print(f"- {len(classrooms)} aulas")
    print(f"- {len(books)} libros")
    print(f"- {len(loans)} préstamos de libros")
    print(f"- {len(payments)} pagos")
    print(f"- {len(scholarships)} becas")
    print(f"- {len(theses)} tesis")

if __name__ == "__main__":
    generate_test_data()