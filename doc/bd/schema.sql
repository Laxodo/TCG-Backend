CREATE TABLE usuario(
    id INT NOT NULL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    contrasenya VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    dinero DECIMAL(10, 2) NOT NULL,
    direccion VARCHAR(50) NOT NULL,
    intercambios INT NOT NULL
);

CREATE TABLE carta(
    id INT NOT NULL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    psa DECIMAL(3,1),
    rareza VARCHAR(50) NOT NULL,
    frontcard VARCHAR(50) NOT NULL,
    backcard VARCHAR(50) NOT NULL,
    venta BOOLEAN NOT NULL
);

CREATE TABLE carta_usuario(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_carta INT NOT NULL,
    id_usuario INT NOT NULL,
    FOREIGN KEY (id_carta) REFERENCES carta(id),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id),
    CONSTRAINT U_CARTA_USUARIO UNIQUE (id_carta, id_usuario)
);

CREATE TABLE expansion(
    id INT NOT NULL PRIMARY KEY,
    id_carta INT,
    nombre VARCHAR(50) NOT NULL,
    año YEAR NOT NULL,
    FOREIGN KEY (id_carta) REFERENCES carta(id),
    CONSTRAINT U_EXPANSION UNIQUE (id_carta)
);

CREATE TABLE generacion(
    id INT NOT NULL PRIMARY KEY,
    id_expansion INT,
    nombre VARCHAR(50) NOT NULL,
    año YEAR NOT NULL,
    FOREIGN KEY (id_expansion) REFERENCES expansion(id),
    CONSTRAINT U_GENERACION UNIQUE (id_expansion)
);

CREATE TABLE transaccion(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_carta INT,
    fecha DATE NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_carta) REFERENCES carta(id),
    CONSTRAINT U_TRANSACCION UNIQUE (id_carta)
);

CREATE TABLE se_intercambia(    
    id_carta INT NOT NULL,
    id_usuario INT NOT NULL,
    id_transaccion INT NOT NULL,
    PRIMARY KEY (id_carta, id_usuario, id_transaccion),
    FOREIGN KEY (id_carta) REFERENCES carta(id),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id),
    FOREIGN KEY (id_transaccion) REFERENCES transaccion(id),
    CONSTRAINT U_SE_INTERCAMBIA UNIQUE (id_carta, id_usuario, id_transaccion)
);
