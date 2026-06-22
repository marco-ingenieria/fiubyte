CREATE TABLE MATERIAS
(
    ID              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    NOMBRE_MATERIA  VARCHAR(80),
    CUATRIMESTRE    TINYINT,
    ANIO            YEAR,
    ELIMINADO       BOOL DEFAULT 0,

    CONSTRAINT CK_CUATRIMESTRE_VALIDO CHECK (CUATRIMESTRE IN (1, 2)),
    CONSTRAINT COMBINACION_UNICA_MATERIAS unique (NOMBRE_MATERIA, CUATRIMESTRE, ANIO),
    FECHA_CREACION DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ALUMNOS
(
    PADRON          NUMERIC(10) NOT NULL PRIMARY KEY ,
    NOMBRE          VARCHAR(30),
    APELLIDO        VARCHAR(30),
    MAIL            VARCHAR(100),
    ID_CURSO        INT NOT NULL,
    ABANDONO        BOOL NOT NULL,
    FECHA_CREACION  DATETIME DEFAULT CURRENT_TIMESTAMP,
    APROBO          BOOL NOT NULL DEFAULT 0,
    ELIMINADO       BOOL DEFAULT 0,

    CONSTRAINT FK_CURSO_ALUMNO FOREIGN KEY (ID_CURSO)
        REFERENCES MATERIAS(ID),
    CONSTRAINT APROBO_ABANDONO CHECK (NOT (ABANDONO AND APROBO))
);

CREATE TABLE EVALUACIONES
(
    ID              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    TIPO            ENUM("Parcial", "Oral", "Final", "TP", "Recuperatorio"),
    NOMBRE          VARCHAR(100),
    ID_MATERIA      INT,
    FECHA_CREACION  DATETIME DEFAULT CURRENT_TIMESTAMP,
    ELIMINADO       BOOL DEFAULT 0,

    CONSTRAINT FK_ID_MATERIA FOREIGN KEY (ID_MATERIA)
        REFERENCES MATERIAS(ID),
    CONSTRAINT COMBINACION_UNICA_EVALUACIONES UNIQUE (TIPO, NOMBRE, ID_MATERIA)

);


CREATE TABLE NOTAS
(
    ID              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    ID_EVALUACION   INT,
    PADRON_ALUMNO   NUMERIC(10),
    NOTA            NUMERIC(2),
    FECHA_CREACION  DATETIME DEFAULT CURRENT_TIMESTAMP,
    ELIMINADO       BOOL DEFAULT 0,

    CONSTRAINT FK_PADRON_ALUMNO FOREIGN KEY (PADRON_ALUMNO)
        REFERENCES ALUMNOS(PADRON),
    CONSTRAINT FK_ID_EVALUACION FOREIGN KEY (ID_EVALUACION)
        REFERENCES EVALUACIONES(ID),
    CONSTRAINT COMBINACION_UNICA_NOTAS UNIQUE (ID_EVALUACION, PADRON_ALUMNO)
);

CREATE TABLE CLASES
(
    ID              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    PROFESORES      JSON,
    FECHA           DATE,
    HORARIO         TIME,
    TEMA            VARCHAR(200),
    ELIMINADO       BOOL DEFAULT 0
);

CREATE TABLE ASISTENCIAS
(
    ID              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    ID_CLASE        INT,
    PADRON_ALUMNO   NUMERIC(10,0),
    FECHA_CREACION  DATETIME DEFAULT CURRENT_TIMESTAMP,
    ELIMINADO       BOOL DEFAULT 0,

    CONSTRAINT FK_PADRON FOREIGN KEY (PADRON_ALUMNO)
    	REFERENCES ALUMNOS(PADRON),
    CONSTRAINT FK_CLASE FOREIGN KEY (ID_CLASE)
    	REFERENCES CLASES(ID),
    CONSTRAINT COMBINACION_UNICA_ASISTENCIAS UNIQUE (ID_CLASE, PADRON_ALUMNO)
);


CREATE TABLE GRUPOS
(
    ID              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    NOMBRE          VARCHAR(50) NOT NULL,
    ID_CURSO        INT NOT NULL,
    FECHA_CREACION  DATETIME DEFAULT CURRENT_TIMESTAMP,
    ELIMINADO       BOOL DEFAULT 0,

    CONSTRAINT FK_CURSO_GRUPO FOREIGN KEY (ID_CURSO)
        REFERENCES MATERIAS(ID)
);


CREATE TABLE GRUPO_ALUMNO
(
    ID_GRUPO        INT ,
    PADRON_ALUMNO   NUMERIC(10),
    FECHA_CREACION  DATETIME DEFAULT CURRENT_TIMESTAMP,
    ELIMINADO       BOOL DEFAULT 0,

    PRIMARY KEY(ID_GRUPO, PADRON_ALUMNO),
    CONSTRAINT FK_ID_GRUPO FOREIGN KEY (ID_GRUPO)
    	REFERENCES GRUPOS(ID),
    CONSTRAINT FK_PADRON_ALUMNOS FOREIGN KEY (PADRON_ALUMNO)
    	REFERENCES ALUMNOS(PADRON)
);


CREATE TABLE GRUPOS_TP (

    ID_EQUIPO       INT NOT NULL,
    ID_INSTANCIA    INT NOT NULL,
    FECHA_CREACION  DATETIME DEFAULT CURRENT_TIMESTAMP,
    ELIMINADO       BOOL DEFAULT 0,

    PRIMARY KEY (ID_EQUIPO, ID_INSTANCIA),
    CONSTRAINT FK_EQUIPO FOREIGN KEY (ID_EQUIPO)
        REFERENCES GRUPOS(ID),
    CONSTRAINT FK_INSTANCIA FOREIGN KEY (ID_INSTANCIA)
        REFERENCES EVALUACIONES(ID)
);

CREATE TABLE USUARIOS (
    ID_USUARIO      INT AUTO_INCREMENT PRIMARY KEY,
    NOMBRE          VARCHAR(50) NOT NULL UNIQUE,
    PASS            VARCHAR(50) NOT NULL,
    FECHA_CREACION  DATETIME DEFAULT CURRENT_TIMESTAMP,
    ELIMINADO       BOOL DEFAULT 0
);

CREATE TABLE HISTORIAL (
    ID_REGISTRO     INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    ACCION          VARCHAR(50) NOT NULL,
    DESCRIPCION     VARCHAR(100),
    ID_USUARIO      INT NOT NULL,
    ELIMINADO       BOOL DEFAULT 0,

    CONSTRAINT FK_USUARIO FOREIGN KEY (ID_USUARIO)
        REFERENCES USUARIOS(ID_USUARIO)
);

-- =========================
-- MATERIAS
-- =========================

INSERT INTO MATERIAS (NOMBRE_MATERIA, CUATRIMESTRE, ANIO) VALUES
('Algoritmos y Programacion III', 1, 2025),
('Bases de Datos', 1, 2025),
('Ingenieria de Software I', 2, 2025);

-- =========================
-- ALUMNOS
-- =========================

INSERT INTO ALUMNOS
(PADRON, NOMBRE, APELLIDO, MAIL, ID_CURSO, ABANDONO, APROBO)
VALUES
(100001,'Ana','Garcia','mleanza@fi.uba.ar',1,0,1),
(100002,'Juan','Perez','juan.perez@fiubyte.edu.ar',1,0,1),
(100003,'Lucia','Fernandez','lucia.fernandez@fiubyte.edu.ar',1,0,1),
(100004,'Martin','Rodriguez','martin.rodriguez@fiubyte.edu.ar',1,0,0),
(100005,'Sofia','Lopez','sofia.lopez@fiubyte.edu.ar',1,1,0),
(100006,'Diego','Martinez','diego.martinez@fiubyte.edu.ar',1,0,0),

(100007,'Valentina','Suarez','valentina.suarez@fiubyte.edu.ar',2,0,1),
(100008,'Tomas','Diaz','tomas.diaz@fiubyte.edu.ar',2,0,1),
(100009,'Camila','Gomez','camila.gomez@fiubyte.edu.ar',2,0,0),
(100010,'Mateo','Ruiz','mateo.ruiz@fiubyte.edu.ar',2,0,1),
(100011,'Julieta','Torres','julieta.torres@fiubyte.edu.ar',2,1,0),
(100012,'Franco','Vega','franco.vega@fiubyte.edu.ar',2,0,0),

(100013,'Agustina','Castro','agustina.castro@fiubyte.edu.ar',3,0,1),
(100014,'Nicolas','Herrera','nicolas.herrera@fiubyte.edu.ar',3,0,1),
(100015,'Micaela','Romero','micaela.romero@fiubyte.edu.ar',3,0,0),
(100016,'Federico','Silva','federico.silva@fiubyte.edu.ar',3,0,1),
(100017,'Carla','Navarro','carla.navarro@fiubyte.edu.ar',3,1,0),
(100018,'Joaquin','Acosta','joaquin.acosta@fiubyte.edu.ar',3,0,0);

-- =========================
-- EVALUACIONES
-- =========================

INSERT INTO EVALUACIONES
(TIPO, NOMBRE, ID_MATERIA)
VALUES
('Parcial','Parcial 1',1),
('Parcial','Parcial 2',1),
('TP','TP Integrador',1),
('Final','Final Regular',1),

('Parcial','Parcial SQL',2),
('TP','TP Modelado',2),
('Final','Final Bases',2),

('Parcial','Parcial UML',3),
('TP','TP Scrum',3),
('Oral','Coloquio Final',3);

-- =========================
-- NOTAS
-- =========================

INSERT INTO NOTAS (ID_EVALUACION, PADRON_ALUMNO, NOTA) VALUES

(1,100001,9),
(1,100002,8),
(1,100003,10),
(1,100004,5),
(1,100006,4),

(2,100001,8),
(2,100002,7),
(2,100003,9),
(2,100004,6),
(2,100006,3),

(3,100001,10),
(3,100002,8),
(3,100003,9),
(3,100004,7),
(3,100006,6),

(5,100007,9),
(5,100008,8),
(5,100009,4),
(5,100010,10),
(5,100012,6),

(6,100007,10),
(6,100008,9),
(6,100009,5),
(6,100010,10),
(6,100012,7),

(8,100013,8),
(8,100014,9),
(8,100015,5),
(8,100016,10),
(8,100018,6);

-- =========================
-- CLASES
-- =========================

INSERT INTO CLASES
(PROFESORES, FECHA, HORARIO, TEMA)
VALUES
('["Juan Perez","Maria Lopez"]','2025-03-10','19:00:00','Introduccion'),
('["Juan Perez"]','2025-03-17','19:00:00','Funciones'),
('["Maria Lopez"]','2025-03-24','19:00:00','POO'),
('["Carlos Gomez"]','2025-04-01','18:00:00','Modelo Relacional'),
('["Carlos Gomez"]','2025-04-08','18:00:00','SQL'),
('["Laura Diaz"]','2025-08-10','18:00:00','Metodologias Agiles');

-- =========================
-- ASISTENCIAS
-- =========================

INSERT INTO ASISTENCIAS (ID_CLASE, PADRON_ALUMNO) VALUES
(1,100001),
(1,100002),
(1,100003),
(1,100004),

(2,100001),
(2,100002),
(2,100003),

(3,100001),
(3,100003),
(3,100004),

(4,100007),
(4,100008),
(4,100010),

(5,100007),
(5,100008),
(5,100009),

(6,100013),
(6,100014),
(6,100016);

-- =========================
-- GRUPOS
-- =========================

INSERT INTO GRUPOS (NOMBRE, ID_CURSO) VALUES
('Grupo A',1),
('Grupo B',1),
('Grupo C',2),
('Grupo D',2),
('Grupo E',3),
('Grupo F',3);

-- =========================
-- GRUPO_ALUMNO
-- =========================

INSERT INTO GRUPO_ALUMNO VALUES
(1,100001,NOW(),0),
(1,100002,NOW(),0),
(1,100003,NOW(),0),

(2,100004,NOW(),0),
(2,100005,NOW(),0),
(2,100006,NOW(),0),

(3,100007,NOW(),0),
(3,100008,NOW(),0),
(3,100009,NOW(),0),

(4,100010,NOW(),0),
(4,100011,NOW(),0),
(4,100012,NOW(),0),

(5,100013,NOW(),0),
(5,100014,NOW(),0),
(5,100015,NOW(),0),

(6,100016,NOW(),0),
(6,100017,NOW(),0),
(6,100018,NOW(),0);

-- =========================
-- GRUPOS_TP
-- =========================

INSERT INTO GRUPOS_TP
(ID_EQUIPO, ID_INSTANCIA)
VALUES
(1,3),
(2,3),
(3,6),
(4,6),
(5,9),
(6,9);

-- =========================
-- USUARIOS
-- =========================

INSERT INTO USUARIOS
(NOMBRE, PASS)
VALUES
('admin','admin123'),
('profesor1','prof123'),
('ayudante1','ayud123');



INSERT INTO USUARIOS (NOMBRE, PASS) VALUES ('BrunoLanzillota', 'linustorvaldsroot');

INSERT INTO MATERIAS (NOMBRE_MATERIA, CUATRIMESTRE, ANIO) VALUES ('Introduccion al Desarrollo', 1, 2026);

INSERT INTO ALUMNOS (PADRON, NOMBRE, APELLIDO, MAIL, ABANDONO, ID_CURSO) VALUES (115599, 'Agustin', 'Maseda', 'amaseda@fi.uba.ar', 0, 1);