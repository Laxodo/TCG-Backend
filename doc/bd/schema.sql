CREATE TABLE user(
    id INT NOT NULL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    money DECIMAL(10, 2) NOT NULL,
    address VARCHAR(50) NOT NULL,
    exanges INT NOT NULL
);

CREATE TABLE card(
    id INT NOT NULL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    psa DECIMAL(3,1),
    rarity VARCHAR(50) NOT NULL,
    frontcard VARCHAR(50) NOT NULL,
    backcard VARCHAR(50) NOT NULL,
    saled BOOLEAN NOT NULL
);

CREATE TABLE user_card(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_card INT NOT NULL,
    id_user INT NOT NULL,
    FOREIGN KEY (id_card) REFERENCES card(id),
    FOREIGN KEY (id_user) REFERENCES user(id),
    CONSTRAINT U_USER_CARD UNIQUE (id_card, id_user)
);

CREATE TABLE expansion(
    id INT NOT NULL PRIMARY KEY,
    id_card INT,
    name VARCHAR(50) NOT NULL,
    year YEAR NOT NULL,
    FOREIGN KEY (id_card) REFERENCES card(id),
    CONSTRAINT U_EXPANSION UNIQUE (id_card)
);

CREATE TABLE generation(
    id INT NOT NULL PRIMARY KEY,
    id_expansion INT,
    name VARCHAR(50) NOT NULL,
    year YEAR NOT NULL,
    FOREIGN KEY (id_expansion) REFERENCES expansion(id),
    CONSTRAINT U_GENERATION UNIQUE (id_expansion)
);

CREATE TABLE transaction(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_card INT,
    date DATE NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_card) REFERENCES card(id),
    CONSTRAINT U_TRANSACTION UNIQUE (id_card)
);

CREATE TABLE se_intercambia(    
    id_card INT NOT NULL,
    id_user INT NOT NULL,
    id_transaction INT NOT NULL,
    PRIMARY KEY (id_card, id_user, id_transaction),
    FOREIGN KEY (id_card) REFERENCES card(id),
    FOREIGN KEY (id_user) REFERENCES user(id),
    FOREIGN KEY (id_transaction) REFERENCES transaction(id),
    CONSTRAINT U_SE_INTERCAMBIA UNIQUE (id_card, id_user, id_transaction)
);
