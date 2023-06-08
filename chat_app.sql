CREATE DATABASE chat_app;

USE chat_app;

-- Crear tabla de usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL,
    contrasena VARCHAR(50) NOT NULL,
    nombreUsuario VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    edad INT NOT NULL,
    genero VARCHAR(10) NOT NULL
);

-- Crear tabla de salas
CREATE TABLE salas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    creador_id INT NOT NULL,
    FOREIGN KEY (creador_id) REFERENCES usuarios(id)
);

-- Crear tabla de participantes de sala
CREATE TABLE participantes (
    sala_id INT NOT NULL,
    usuario_id INT NOT NULL,
    FOREIGN KEY (sala_id) REFERENCES salas(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    PRIMARY KEY (sala_id, usuario_id)
);
