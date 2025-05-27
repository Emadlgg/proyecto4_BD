DROP DATABASE IF EXISTS proyecto4_sgu
CREATE DATABASE proyecto4_sgu

-- TIPOS DE DATOS PERSONALIZADOS
CREATE TYPE tipo_semestre AS ENUM ('Verano', 'Primer Semestre', 'Segundo Semestre');
CREATE TYPE tipo_calificacion AS ENUM ('A', 'B', 'C', 'D', 'F', 'NP');
CREATE TYPE tipo_aula AS ENUM ('Teoría', 'Laboratorio', 'Auditorio');
CREATE TYPE estado_matricula AS ENUM ('Activa', 'Retirada', 'Finalizada');
CREATE TYPE tipo_pago AS ENUM ('Matrícula', 'Multa', 'Donación');
CREATE TYPE dia_semana AS ENUM ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes');

-- TABLAS PRINCIPALES
-- Facultades
CREATE TABLE facultad (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ubicacion VARCHAR(100) NOT NULL,
    fecha_fundacion DATE
);

-- Departamentos
CREATE TABLE departamento (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    facultad_id INTEGER NOT NULL REFERENCES facultad(id),
    telefono VARCHAR(15),
    presupuesto DECIMAL(10,2)
);

-- Carreras
CREATE TABLE carrera (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    facultad_id INTEGER NOT NULL REFERENCES facultad(id),
    duracion_anos INTEGER NOT NULL CHECK (duracion_anos > 0),
    creditos_totales INTEGER NOT NULL
);

-- Estudiantes
CREATE TABLE estudiante (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    direccion TEXT,
    telefono VARCHAR(15),
    email VARCHAR(100) UNIQUE NOT NULL CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'),
    carrera_id INTEGER REFERENCES carrera(id),
    fecha_ingreso DATE NOT NULL DEFAULT CURRENT_DATE
);

-- Profesores
CREATE TABLE profesor (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    especializacion VARCHAR(100),
    departamento_id INTEGER NOT NULL REFERENCES departamento(id),
    fecha_contratacion DATE NOT NULL,
    salario DECIMAL(10,2) CHECK (salario > 0)
);

-- Cursos
CREATE TABLE curso (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo VARCHAR(10) UNIQUE NOT NULL,
    creditos INTEGER NOT NULL CHECK (creditos > 0),
    descripcion TEXT,
    carrera_id INTEGER NOT NULL REFERENCES carrera(id),
    prerequisito_id INTEGER REFERENCES curso(id)
);

-- Aulas
CREATE TABLE aula (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL,
    edificio VARCHAR(50) NOT NULL,
    capacidad INTEGER NOT NULL CHECK (capacidad > 0),
    tipo tipo_aula NOT NULL,
    tiene_proyector BOOLEAN DEFAULT FALSE
);

-- Matrículas
CREATE TABLE matricula (
    estudiante_id INTEGER NOT NULL REFERENCES estudiante(id),
    curso_id INTEGER NOT NULL REFERENCES curso(id),
    semestre tipo_semestre NOT NULL,
    calificacion tipo_calificacion,
    estado estado_matricula NOT NULL DEFAULT 'Activa',
    fecha_matricula TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (estudiante_id, curso_id, semestre)
);

-- Horarios
CREATE TABLE horario (
    id SERIAL PRIMARY KEY,
    curso_id INTEGER NOT NULL REFERENCES curso(id),
    aula_id INTEGER NOT NULL REFERENCES aula(id),
    dia dia_semana NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    CHECK (hora_fin > hora_inicio)
);

-- Asignación de profesores
CREATE TABLE asignacion_profesor (
    profesor_id INTEGER NOT NULL REFERENCES profesor(id),
    curso_id INTEGER NOT NULL REFERENCES curso(id),
    semestre tipo_semestre NOT NULL,
    es_coordinador BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (profesor_id, curso_id, semestre)
);

-- Libros
CREATE TABLE libro (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    autor VARCHAR(100) NOT NULL,
    isbn VARCHAR(20) UNIQUE NOT NULL,
    editorial VARCHAR(100),
    anio_publicacion INTEGER,
    estado VARCHAR(20) DEFAULT 'Disponible' CHECK (estado IN ('Disponible', 'Prestado', 'En reparación'))
);

-- Préstamos de libros
CREATE TABLE prestamo_libro (
    id SERIAL PRIMARY KEY,
    libro_id INTEGER NOT NULL REFERENCES libro(id),
    estudiante_id INTEGER NOT NULL REFERENCES estudiante(id),
    fecha_prestamo DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_devolucion DATE NOT NULL,
    fecha_devolucion_real DATE,
    multa DECIMAL(8,2) DEFAULT 0.00,
    CHECK (fecha_devolucion > fecha_prestamo),
    CHECK (fecha_devolucion_real IS NULL OR fecha_devolucion_real >= fecha_prestamo)
);

-- Pagos
CREATE TABLE pago (
    id SERIAL PRIMARY KEY,
    estudiante_id INTEGER NOT NULL REFERENCES estudiante(id),
    monto DECIMAL(10,2) NOT NULL CHECK (monto > 0),
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo tipo_pago NOT NULL,
    descripcion TEXT,
    referencia VARCHAR(50) UNIQUE
);

-- Becas
CREATE TABLE beca (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    porcentaje DECIMAL(5,2) NOT NULL CHECK (porcentaje > 0 AND porcentaje <= 100),
    estudiante_id INTEGER NOT NULL REFERENCES estudiante(id),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    CHECK (fecha_fin IS NULL OR fecha_fin > fecha_inicio)
);

-- Eventos académicos
CREATE TABLE evento_academico (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    fecha DATE NOT NULL,
    hora_inicio TIME,
    hora_fin TIME,
    responsable_id INTEGER NOT NULL REFERENCES profesor(id),
    ubicacion VARCHAR(100) NOT NULL,
    costo DECIMAL(8,2) DEFAULT 0.00
);

-- Evaluaciones
CREATE TABLE evaluacion (
    id SERIAL PRIMARY KEY,
    curso_id INTEGER NOT NULL REFERENCES curso(id),
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('Parcial', 'Examen Final', 'Proyecto', 'Tarea')),
    fecha DATE NOT NULL,
    porcentaje DECIMAL(5,2) NOT NULL CHECK (porcentaje > 0 AND porcentaje <= 100),
    descripcion TEXT
);

-- Asistencias
CREATE TABLE asistencia (
    id SERIAL PRIMARY KEY,
    estudiante_id INTEGER NOT NULL REFERENCES estudiante(id),
    curso_id INTEGER NOT NULL REFERENCES curso(id),
    fecha DATE NOT NULL,
    presente BOOLEAN NOT NULL DEFAULT FALSE,
    justificacion TEXT,
    UNIQUE (estudiante_id, curso_id, fecha)
);

-- Laboratorios
CREATE TABLE laboratorio (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ubicacion VARCHAR(100) NOT NULL,
    responsable_id INTEGER NOT NULL REFERENCES profesor(id),
    capacidad INTEGER NOT NULL CHECK (capacidad > 0),
    equipamiento TEXT,
    horario_atencion TEXT
);

-- Tesis
CREATE TABLE tesis (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    estudiante_id INTEGER NOT NULL REFERENCES estudiante(id),
    asesor_id INTEGER NOT NULL REFERENCES profesor(id),
    fecha_inicio DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_entrega DATE,
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('En progreso', 'Finalizada', 'Aprobada', 'Reprobada')),
    calificacion DECIMAL(3,1) CHECK (calificacion >= 0 AND calificacion <= 10),
    archivo_url TEXT
);

-- Auditoría de cambios
CREATE TABLE auditoria_cambios (
    id SERIAL PRIMARY KEY,
    tabla_afectada VARCHAR(50) NOT NULL,
    id_registro INTEGER NOT NULL,
    tipo_operacion VARCHAR(10) NOT NULL CHECK (tipo_operacion IN ('INSERT', 'UPDATE', 'DELETE')),
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usuario VARCHAR(50) NOT NULL,
    valores_anteriores JSONB,
    valores_nuevos JSONB
);

-- VISTAS
-- Vista 1: Estudiantes con sus cursos y promedios
CREATE VIEW vista_estudiantes_cursos_promedio AS
SELECT 
    e.id AS estudiante_id,
    e.nombre || ' ' || e.apellido AS estudiante,
    c.nombre AS carrera,
    COUNT(m.curso_id) AS cursos_inscritos,
    AVG(CASE 
        WHEN m.calificacion = 'A' THEN 4.0
        WHEN m.calificacion = 'B' THEN 3.0
        WHEN m.calificacion = 'C' THEN 2.0
        WHEN m.calificacion = 'D' THEN 1.0
        WHEN m.calificacion = 'F' THEN 0.0
        ELSE NULL
    END) AS promedio,
    SUM(cr.creditos) AS creditos_aprobados
FROM 
    estudiante e
JOIN 
    carrera c ON e.carrera_id = c.id
LEFT JOIN 
    matricula m ON e.id = m.estudiante_id AND m.calificacion IS NOT NULL AND m.calificacion != 'NP'
LEFT JOIN 
    curso cr ON m.curso_id = cr.id
GROUP BY 
    e.id, e.nombre, e.apellido, c.nombre;

-- Vista 2: Cursos con información detallada
CREATE VIEW vista_cursos_detallados AS
SELECT 
    c.id,
    c.codigo,
    c.nombre AS curso,
    cr.nombre AS carrera,
    f.nombre AS facultad,
    COUNT(DISTINCT m.estudiante_id) AS estudiantes_inscritos,
    COUNT(DISTINCT ap.profesor_id) AS profesores_asignados,
    STRING_AGG(DISTINCT p.nombre || ' ' || p.apellido, ', ') AS profesores,
    c.creditos,
    c.descripcion
FROM 
    curso c
JOIN 
    carrera cr ON c.carrera_id = cr.id
JOIN 
    facultad f ON cr.facultad_id = f.id
LEFT JOIN 
    matricula m ON c.id = m.curso_id AND m.estado = 'Activa'
LEFT JOIN 
    asignacion_profesor ap ON c.id = ap.curso_id
LEFT JOIN 
    profesor p ON ap.profesor_id = p.id
GROUP BY 
    c.id, c.codigo, c.nombre, cr.nombre, f.nombre, c.creditos, c.descripcion;

-- FUNCIONES (3+ REQUERIDAS)
-- Función 1: Calcular promedio de un estudiante
CREATE OR REPLACE FUNCTION calcular_promedio_estudiante(est_id INTEGER)
RETURNS DECIMAL(3,2) AS $$
DECLARE
    promedio DECIMAL(3,2);
BEGIN
    SELECT AVG(CASE 
        WHEN calificacion = 'A' THEN 4.0
        WHEN calificacion = 'B' THEN 3.0
        WHEN calificacion = 'C' THEN 2.0
        WHEN calificacion = 'D' THEN 1.0
        WHEN calificacion = 'F' THEN 0.0
        ELSE NULL
    END) INTO promedio
    FROM matricula
    WHERE estudiante_id = est_id AND calificacion IS NOT NULL AND calificacion != 'NP';
    
    RETURN promedio;
END;
$$ LANGUAGE plpgsql;

-- Función 2: Verificar disponibilidad de aula
CREATE OR REPLACE FUNCTION verificar_disponibilidad_aula(
    aula_id INTEGER,
    dia_verificar dia_semana,
    hora_inicio_verificar TIME,
    hora_fin_verificar TIME
) RETURNS BOOLEAN AS $$
DECLARE
    esta_ocupada BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM horario
        WHERE aula_id = verificar_disponibilidad_aula.aula_id
        AND dia = dia_verificar
        AND (
            (hora_inicio_verificar BETWEEN hora_inicio AND hora_fin)
            OR (hora_fin_verificar BETWEEN hora_inicio AND hora_fin)
            OR (hora_inicio BETWEEN hora_inicio_verificar AND hora_fin_verificar)
        )
    ) INTO esta_ocupada;
    
    RETURN NOT esta_ocupada;
END;
$$ LANGUAGE plpgsql;

-- Función 3: Generar reporte de pagos pendientes
CREATE OR REPLACE FUNCTION reporte_pagos_pendientes()
RETURNS TABLE (
    estudiante_id INTEGER,
    nombre_completo TEXT,
    email VARCHAR(100),
    total_pendiente DECIMAL(10,2),
    pagos_atrasados INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.nombre || ' ' || e.apellido,
        e.email,
        COALESCE(SUM(p.monto), 0) AS total_pendiente,
        COUNT(p.id) AS pagos_atrasados
    FROM 
        estudiante e
    LEFT JOIN 
        pago p ON e.id = p.estudiante_id AND p.fecha < CURRENT_DATE - INTERVAL '30 days'
    GROUP BY 
        e.id, e.nombre, e.apellido, e.email
    HAVING 
        COALESCE(SUM(p.monto), 0) > 0
    ORDER BY 
        total_pendiente DESC;
END;
$$ LANGUAGE plpgsql;


-- TRIGGERS (3+ REQUERIDAS)
-- Trigger 1: Auditoría de cambios en estudiantes
CREATE OR REPLACE FUNCTION auditoria_estudiantes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO auditoria_cambios (
            tabla_afectada, 
            id_registro, 
            tipo_operacion, 
            usuario,
            valores_anteriores
        ) VALUES (
            'estudiante', 
            OLD.id, 
            'DELETE', 
            current_user,
            to_jsonb(OLD)
        );
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO auditoria_cambios (
            tabla_afectada, 
            id_registro, 
            tipo_operacion, 
            usuario,
            valores_anteriores,
            valores_nuevos
        ) VALUES (
            'estudiante', 
            NEW.id, 
            'UPDATE', 
            current_user,
            to_jsonb(OLD),
            to_jsonb(NEW)
        );
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO auditoria_cambios (
            tabla_afectada, 
            id_registro, 
            tipo_operacion, 
            usuario,
            valores_nuevos
        ) VALUES (
            'estudiante', 
            NEW.id, 
            'INSERT', 
            current_user,
            to_jsonb(NEW)
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auditoria_estudiantes
AFTER INSERT OR UPDATE OR DELETE ON estudiante
FOR EACH ROW EXECUTE FUNCTION auditoria_estudiantes();

-- Trigger 2: Validar cupo de aula al asignar horario
CREATE OR REPLACE FUNCTION validar_cupo_aula()
RETURNS TRIGGER AS $$
DECLARE
    capacidad_aula INTEGER;
    estudiantes_inscritos INTEGER;
BEGIN
    -- Obtener capacidad del aula
    SELECT capacidad INTO capacidad_aula FROM aula WHERE id = NEW.aula_id;
    
    -- Contar estudiantes inscritos en el curso
    SELECT COUNT(*) INTO estudiantes_inscritos 
    FROM matricula 
    WHERE curso_id = NEW.curso_id AND estado = 'Activa';
    
    -- Verificar capacidad
    IF estudiantes_inscritos > capacidad_aula THEN
        RAISE EXCEPTION 'El aula % no tiene capacidad para % estudiantes (capacidad: %)', 
            NEW.aula_id, estudiantes_inscritos, capacidad_aula;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validar_cupo_aula
BEFORE INSERT OR UPDATE ON horario
FOR EACH ROW EXECUTE FUNCTION validar_cupo_aula();

-- Trigger 3: Actualizar estado de libro al prestar/devolver
CREATE OR REPLACE FUNCTION actualizar_estado_libro()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE libro SET estado = 'Prestado' WHERE id = NEW.libro_id;
    ELSIF TG_OP = 'UPDATE' AND NEW.fecha_devolucion_real IS NOT NULL THEN
        UPDATE libro SET estado = 'Disponible' WHERE id = NEW.libro_id;
        
        -- Calcular multa si hay retraso
        IF NEW.fecha_devolucion_real > NEW.fecha_devolucion THEN
            NEW.multa = (NEW.fecha_devolucion_real - NEW.fecha_devolucion) * 5.00; -- $5 por día de retraso
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_estado_libro
AFTER INSERT OR UPDATE ON prestamo_libro
FOR EACH ROW EXECUTE FUNCTION actualizar_estado_libro();

-- ÍNDICES PARA MEJORAR RENDIMIENTO
CREATE INDEX idx_matricula_estudiante ON matricula(estudiante_id);
CREATE INDEX idx_matricula_curso ON matricula(curso_id);
CREATE INDEX idx_horario_curso ON horario(curso_id);
CREATE INDEX idx_horario_aula ON horario(aula_id);
CREATE INDEX idx_estudiante_carrera ON estudiante(carrera_id);
CREATE INDEX idx_curso_carrera ON curso(carrera_id);