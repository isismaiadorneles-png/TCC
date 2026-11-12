CREATE DATABASE IF NOT EXISTS TCC;
USE TCC;

CREATE TABLE IF NOT EXISTS estoque_almoxarifado (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    quantidade INT NOT NULL DEFAULT 0,
    estoque_minimo INT NOT NULL DEFAULT 0,
    descrição TEXT,
    preço DECIMAL(10,2) DEFAULT 0.00,
    categoria VARCHAR(255),
    imagem VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    tipo ENUM('admin', 'usuario') NOT NULL
);

CREATE TABLE IF NOT EXISTS movimentaçoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    tipo ENUM('ADICIONAR', 'RETIRAR') NOT NULL,
    quantidade INT NOT NULL,
    responsavel VARCHAR(100),
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES estoque_almoxarifado(id)
);

CREATE TABLE IF NOT EXISTS historico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    quantidade INT NOT NULL,
    acao VARCHAR(255)
);

INSERT IGNORE INTO usuario (nome, senha, tipo) 
VALUES ('administrador', '$2b$12$KdBbc/SscvNn7x2mZ8zLGe7L.5HwR6Zisb3R5V2w7ZtIBy73oQp2i', 'admin');
