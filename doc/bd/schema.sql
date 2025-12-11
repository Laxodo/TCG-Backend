CREATE TABLE user(
    id CHAR(64) NOT NULL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    money DECIMAL(10, 2) NOT NULL DEFAULT 0,
    address VARCHAR(100),
    exchanges INT DEFAULT 0
);

CREATE TABLE card(
    id CHAR(64) NOT NULL PRIMARY KEY,
    id_expansion CHAR(64) NOT NULL,
    name VARCHAR(50) NOT NULL,
    rarity VARCHAR(50) NOT NULL,
    frontcard VARCHAR(255) NOT NULL,
    backcard VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_expansion) REFERENCES expansion(id)
);

CREATE TABLE user_card(
    id CHAR(64) NOT NULL PRIMARY KEY,
    id_card CHAR(64) NOT NULL,
    id_user CHAR(64) NOT NULL,
    price DECIMAL(10, 2),
    psa DECIMAL(3,1),
    sold BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_card) REFERENCES card(id),
    FOREIGN KEY (id_user) REFERENCES user(id)
);

CREATE TABLE expansion(
    id CHAR(64) NOT NULL PRIMARY KEY,
    id_generation CHAR(64) NOT NULL,
    name VARCHAR(50) NOT NULL,
    year YEAR NOT NULL,
    FOREIGN KEY (id_generation) REFERENCES generation(id)
);

CREATE TABLE generation(
    id CHAR(64) NOT NULL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    year YEAR NOT NULL
);

CREATE TABLE transaction(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_user_card CHAR(64) NOT NULL,
    id_from CHAR(64) NOT NULL,
    id_to CHAR(64) NOT NULL,
    date DATETIME NOT NULL,
    price DECIMAL(10, 2),
    type VARCHAR(20) NOT NULL,
    FOREIGN KEY (id_user_card) REFERENCES user_card(id),
    FOREIGN KEY (id_from) REFERENCES user(id),
    FOREIGN KEY (id_to) REFERENCES user(id)
);

CREATE TABLE trade(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_user_card_offer CHAR(64) NOT NULL,
    id_user_card_demand CHAR(64) NOT NULL,
    id_user_offer CHAR(64) NOT NULL,
    id_user_demand CHAR(64) NOT NULL,
    id_transaction_offer INT NOT NULL,
    id_transaction_demand INT NOT NULL,
    date DATETIME NOT NULL,
    FOREIGN KEY (id_user_card_offer) REFERENCES user_card(id),
    FOREIGN KEY (id_user_card_demand) REFERENCES user_card(id),
    FOREIGN KEY (id_user_offer) REFERENCES user(id),
    FOREIGN KEY (id_user_demand) REFERENCES user(id),
    FOREIGN KEY (id_transaction_offer) REFERENCES transaction(id),
    FOREIGN KEY (id_transaction_demand) REFERENCES transaction(id)
);
