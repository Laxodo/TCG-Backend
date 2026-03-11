CREATE TABLE user(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    money DECIMAL(10, 2) NOT NULL DEFAULT 0,
    opened_boosters INT NOT NULL DEFAULT 0,
    exchanges INT DEFAULT 0,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE generation(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    year YEAR NOT NULL
);

CREATE TABLE expansion(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_generation INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    year YEAR NOT NULL,
    FOREIGN KEY (id_generation) REFERENCES generation(id)
);

CREATE TABLE card(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_expansion INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    rarity VARCHAR(50) NOT NULL,
    frontcard VARCHAR(255) NOT NULL,
    backcard VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_expansion) REFERENCES expansion(id)
);

CREATE TABLE user_card(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_card INT NOT NULL,
    id_user INT NOT NULL,
    price DECIMAL(10, 2),
    psa DECIMAL(3,1),
    sold BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_card) REFERENCES card(id),
    FOREIGN KEY (id_user) REFERENCES user(id)
);

CREATE TABLE deck(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_user INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_user) REFERENCES user(id)
);

CREATE TABLE deck_card(
    id_deck INT NOT NULL,
    id_card INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    PRIMARY KEY (id_deck, id_card),
    FOREIGN KEY (id_deck) REFERENCES deck(id) ON DELETE CASCADE,
    FOREIGN KEY (id_card) REFERENCES card(id) ON DELETE CASCADE
);

CREATE TABLE trade(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_user_card_offer INT NOT NULL,
    id_user_card_demand INT NOT NULL,
    id_user_offer INT NOT NULL,
    id_user_demand INT NOT NULL,
    date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_user_card_offer) REFERENCES user_card(id),
    FOREIGN KEY (id_user_card_demand) REFERENCES user_card(id),
    FOREIGN KEY (id_user_offer) REFERENCES user(id),
    FOREIGN KEY (id_user_demand) REFERENCES user(id)
);

CREATE TABLE transaction(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_user_card INT,
    id_from INT NOT NULL,
    id_to INT NOT NULL,
    id_trade INT,
    date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    price DECIMAL(10, 2),
    type VARCHAR(20) NOT NULL,
    FOREIGN KEY (id_user_card) REFERENCES user_card(id),
    FOREIGN KEY (id_from) REFERENCES user(id),
    FOREIGN KEY (id_to) REFERENCES user(id),
    FOREIGN KEY (id_trade) REFERENCES trade(id)
);
