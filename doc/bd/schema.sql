CREATE TABLE user(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    money INT NOT NULL DEFAULT 0,
    opened_boosters INT NOT NULL DEFAULT 0,
    exchanges INT NOT NULL DEFAULT 0,
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
    price INT NOT NULL DEFAULT 0,
    year YEAR NOT NULL,
    FOREIGN KEY (id_generation) REFERENCES generation(id) ON DELETE CASCADE
);

CREATE TABLE card(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_expansion INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    rarity VARCHAR(50) NOT NULL,
    price INT NOT NULL DEFAULT 100,
    card_number INT NOT NULL,
    frontcard VARCHAR(255) NOT NULL,
    backcard VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_expansion) REFERENCES expansion(id) ON DELETE CASCADE
);

CREATE TABLE user_card(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_card INT NOT NULL,
    id_user INT NOT NULL,
    price INT NOT NULL,
    psa INT,
    sold BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_card) REFERENCES card(id),
    FOREIGN KEY (id_user) REFERENCES user(id) ON DELETE CASCADE
);

CREATE TABLE card_market(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_user INT NOT NULL,
    id_card INT,
    id_user_card INT NOT NULL,
    price INT,
    psa INT,
    exchange_type VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_user) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (id_card) REFERENCES card(id),
    FOREIGN KEY (id_user_card) REFERENCES user_card(id) ON DELETE CASCADE
);

CREATE TABLE log_history(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_user INT NOT NULL,
    id_user_interacted INT,
    description VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    money_exchange INT NOT NULL,
    date DATETIME NOT NULL,
    FOREIGN KEY (id_user) REFERENCES user(id),
    FOREIGN KEY (id_user_interacted) REFERENCES user(id)
);

CREATE TABLE log_activity(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_user INT NOT NULL,
    id_card INT NOT NULL,
    id_log_history INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    price INT NOT NULL,
    psa INT,
    FOREIGN KEY (id_user) REFERENCES user(id),
    FOREIGN KEY (id_card) REFERENCES card(id),
    FOREIGN KEY (id_log_history) REFERENCES log_history(id)
);