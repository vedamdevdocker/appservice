-- Create database only if it doesn't exist
CREATE DATABASE IF NOT EXISTS mydb;
USE mydb;

-- Create table only if it doesn't exist
CREATE TABLE IF NOT EXISTS mydb.users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Insert data into the table
INSERT INTO mydb.users (name) VALUES ('Kishore'), ('Vedam'), ('Ramu');



