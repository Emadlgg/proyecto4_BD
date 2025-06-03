# Sistema de Gestión Universitaria (SGU)

## Descripción
Sistema completo para gestión académica universitaria que integra PostgreSQL con SQLAlchemy ORM. Permite administrar facultades, estudiantes, profesores, cursos y matrículas con validaciones robustas y reportería avanzada.

## Características Principales
- ✅ **20+ tablas** con relaciones 1:N y N:M
- ✅ **ORM exclusivo** con SQLAlchemy (sin SQL crudo)
- ✅ **3 CRUDs completos** (Facultades, Estudiantes, Profesores)
- ✅ **Validaciones** con CHECK constraints, triggers y funciones SQL
- ✅ **5+ tipos personalizados** (ENUMs PostgreSQL)
- ✅ **3 vistas SQL** para consultas complejas
- ✅ **3 reportes** con múltiples filtros y exportación CSV
- ✅ **1000+ registros** de datos de prueba coherentes

## Requisitos del Sistema
- Python 3.8+
- PostgreSQL 12+
- pip (gestor de paquetes de Python)

## Instalación

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd proyecto4_BD
```

### 2. Instalar PostgreSQL
- Descargar desde [postgresql.org](https://www.postgresql.org/download/)
- Recordar usuario y contraseña del superusuario

### 3. Crear base de datos
```bash
# Opción 1: Línea de comandos
createdb -U postgres proyecto4_sgu

# Opción 2: pgAdmin4
# Crear base de datos llamada "proyecto4_sgu"
```

### 4. Ejecutar schema SQL
```bash
# Línea de comandos
psql -U postgres -d proyecto4_sgu -f database/schema.sql

# O usar pgAdmin4:
# 1. Conectar a proyecto4_sgu
# 2. Query Tool > Open File > schema.sql
# 3. Ejecutar (F5)
```

### 5. Instalar dependencias Python
```bash
pip install -r requirements.txt
```

### 6. Configurar variables de entorno
Crear archivo `.env` en la raíz del proyecto:
```env
DATABASE_URL=postgresql://postgres:TU_PASSWORD@localhost:5432/proyecto4_sgu
```

### 7. Ejecutar aplicación
```bash
cd src
python main.py
```

## Estructura del Proyecto
```
proyecto4_BD/
├── database/
│   ├── schema.sql          # Estructura completa de BD
│   └── data.sql            # Datos de prueba (opcional)
├── src/
│   ├── models.py           # Modelos SQLAlchemy ORM
│   ├── cruds.py           # Operaciones CRUD
│   ├── main.py            # Interfaz principal
│   └── reports.py         # Generador de reportes
├── reports/               # Reportes CSV generados
├── docs/                  # Documentación adicional
├── .env                   # Variables de entorno
├── requirements.txt       # Dependencias Python
└── README.md             # Este archivo
```

## Funcionalidades

### 📚 Gestión Académica
- **Facultades**: Crear, listar, buscar, actualizar
- **Estudiantes**: Registro completo con validaciones
- **Profesores**: Gestión de personal académico
- **Cursos**: Catálogo de materias por carrera

### 📊 Reportería
1. **Estudiantes por Carrera** (5 filtros):
   - Carrera específica
   - Estado del estudiante
   - Rango de años de ingreso
   - Edad mínima
   - Facultad

2. **Cursos por Semestre** (5 filtros):
   - Semestre específico
   - Facultad
   - Créditos mínimos
   - Número máximo de estudiantes
   - Profesor asignado

3. **Matrículas Activas** (5 filtros):
   - Estado de matrícula
   - Período académico
   - Curso específico
   - Estudiante específico
   - Fecha de matrícula

### 🛡️ Validaciones Implementadas
- **CHECK constraints**: Salarios positivos, fechas válidas
- **UNIQUE constraints**: Emails únicos, códigos de curso
- **NOT NULL**: Campos obligatorios
- **3 triggers**: Auditoría de cambios
- **2 funciones SQL**: Cálculo de promedios, cursos disponibles

### 🗂️ Tipos de Datos Personalizados
- `tipo_semestre`: Verano, Primer Semestre, Segundo Semestre
- `tipo_calificacion`: A, B, C, D, F, NP
- `tipo_aula`: Teoría, Laboratorio, Auditorio
- `estado_matricula`: Activa, Retirada, Finalizada
- `dia_semana`: Lunes a Viernes

## Uso de la Aplicación

### Menú Principal
```
1. Gestión Académica
   ├── Gestión de Facultades
   ├── Gestión de Estudiantes  
   └── Gestión de Profesores
2. Reportes
   ├── Estudiantes por Carrera
   ├── Cursos por Semestre
   └── Matrículas Activas
3. Salir
```

### Ejemplo de Uso
```bash
# Ejecutar aplicación
python src/main.py

# Crear nueva facultad
Gestión Académica > Gestión de Facultades > Crear Facultad

# Generar reporte
Reportes > Estudiantes por Carrera > [Aplicar filtros] > Exportar CSV
```

## Dependencias (requirements.txt)
```
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

## Base de Datos

### Tablas Principales
- `facultad`: Facultades universitarias
- `departamento`: Departamentos académicos
- `carrera`: Programas académicos
- `estudiante`: Registro estudiantil
- `profesor`: Personal docente
- `curso`: Catálogo de materias
- `matricula`: Inscripciones estudiante-curso
- `aula`: Espacios físicos
- `horario`: Programación de clases

### Vistas SQL
- `vista_cursos_detallados`: Cursos con información completa
- `vista_estudiantes_carreras`: Estudiantes con datos de carrera
- `vista_profesores_departamentos`: Profesores con departamento

### Funciones SQL
- `calcular_promedio_estudiante(id)`: Promedio académico
- `obtener_cursos_disponibles(carrera_id)`: Cursos disponibles
- `actualizar_auditoria()`: Función de trigger

## Autores y Contribuciones

| Integrante | Contribución Principal |
|------------|----------------------|
| **Osman de León** | Desarrollo de CRUDs principales, lógica de negocio |
| **Olivier Viau** | Generación de datos de prueba, validaciones |
| **Milton Polanco** | CRUDs secundarios, integración de reportes, Reflexión |
| **Adrián González** | Diseño de base de datos, arquitectura |

## Decisiones Técnicas

### Normalización
- **1FN**: Todos los atributos son atómicos
- **2FN**: Eliminación de dependencias parciales
- **3FN**: Eliminación de dependencias transitivas

### Tipos Personalizados
- **ENUMs**: Para campos con valores limitados y controlados
- **Validación**: Garantiza integridad referencial
- **Rendimiento**: Índices automáticos en tipos enumerados

### ORM vs SQL Crudo
- **Ventajas ORM**: Portabilidad, seguridad, mantenibilidad
- **Desventajas**: Menor control granular sobre consultas
- **Decisión**: ORM exclusivo según requerimientos del proyecto

## Solución de Problemas

### Error de conexión a BD
```bash
# Verificar que PostgreSQL esté corriendo
sudo service postgresql status

# Verificar credenciales en .env
cat .env
```

### Error de importación
```bash
# Instalar dependencias
pip install -r requirements.txt

# Verificar Python path
python -c "import sys; print(sys.path)"
```


---
*Última actualización: Junio 2025*