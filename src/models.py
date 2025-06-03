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

# Cambiar esta línea para usar SQLite por defecto si no hay PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///university.db')

# Cambiar la configuración para NO crear tablas automáticamente
# Solo conectarse a la base de datos existente
try:
    if DATABASE_URL.startswith('postgresql'):
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
    else:
        engine = create_engine(DATABASE_URL, echo=False)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    print(f"Conectado a la base de datos existente: {DATABASE_URL}")
    
except Exception as e:
    print(f"Error conectando a la base de datos: {e}")

# Definir SOLO las clases que vas a usar para ORM
class Faculty(Base):
    __tablename__ = 'facultad'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    ubicacion = Column(String(100), nullable=False)
    fecha_fundacion = Column(Date)
    telefono = Column(String(15))
    decano = Column(String(100))
    
    # Relationships
    departments = relationship("Department", back_populates="faculty")
    majors = relationship("Major", back_populates="faculty")

class Department(Base):
    __tablename__ = 'departamento'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    facultad_id = Column(Integer, ForeignKey('facultad.id'), nullable=False)
    email = Column(String(100))
    
    # Relationships
    faculty = relationship("Faculty", back_populates="departments")
    professors = relationship("Professor", back_populates="department")

class Major(Base):
    __tablename__ = 'carrera'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    facultad_id = Column(Integer, ForeignKey('facultad.id'), nullable=False)
    titulo = Column(String(50))
    
    # Relationships
    faculty = relationship("Faculty", back_populates="majors")
    students = relationship("Student", back_populates="major")
    courses = relationship("Course", back_populates="major")

class Student(Base):
    __tablename__ = 'estudiante'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    direccion = Column(Text)
    telefono = Column(String(15))
    email = Column(String(100), unique=True, nullable=False)
    carrera_id = Column(Integer, ForeignKey('carrera.id'))
    fecha_ingreso = Column(Date, default=datetime.now().date())
    estado = Column(String(20), default='Activo')
    
    # Relationships
    major = relationship("Major", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student")

class Professor(Base):
    __tablename__ = 'profesor'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    especializacion = Column(String(100))
    departamento_id = Column(Integer, ForeignKey('departamento.id'), nullable=False)
    fecha_contratacion = Column(Date, nullable=False)
    salario = Column(Numeric(10, 2))
    email = Column(String(100), unique=True)
    activo = Column(Boolean, default=True)
    
    # Relationships
    department = relationship("Department", back_populates="professors")

class Course(Base):
    __tablename__ = 'curso'
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(10), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    creditos = Column(Integer, nullable=False)
    descripcion = Column(Text)
    carrera_id = Column(Integer, ForeignKey('carrera.id'), nullable=False)
    prerequisito_id = Column(Integer, ForeignKey('curso.id'))
    departamento_id = Column(Integer, ForeignKey('departamento.id'))
    
    # Relationships
    major = relationship("Major", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course")

class Enrollment(Base):
    __tablename__ = 'matricula'
    
    estudiante_id = Column(Integer, ForeignKey('estudiante.id'), primary_key=True)
    curso_id = Column(Integer, ForeignKey('curso.id'), primary_key=True)
    semestre = Column(String(20), primary_key=True)  # tipo_semestre enum
    calificacion = Column(String(2))  # tipo_calificacion enum
    estado = Column(String(20), default='Activa')
    fecha_matricula = Column(DateTime, default=datetime.now)
    
    # Relationships
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

# NO CREAR TABLAS - Solo mapear las existentes
# NO usar Base.metadata.create_all(engine)

# Al final del archivo, asegurar que todas las clases estén disponibles para importar
__all__ = ['Base', 'session', 'engine', 'Faculty', 'Department', 'Major', 'Student', 'Professor', 'Course', 'Enrollment']