CREATE DATABASE db_personal_data;

\connect db_personal_data;

CREATE TABLE emails (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);

CREATE TABLE phone_numbers (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(50) NOT NULL
);
