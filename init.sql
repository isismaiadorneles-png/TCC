CREATE DATABASE IF NOT EXISTS TCC;
CREATE DATABASE TCC;


USE TCC;

CREATE TABLE estoque_almoxarifado (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    quantidade VARCHAR(255),
    estoque_minimo VARCHAR(255),
    descrição VARCHAR(255),
    preço VARCHAR(255),
    categoria VARCHAR(255),
    imagem VARCHAR(255)
);

CREATE TABLE usuario(
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    tipo ENUM('admin', 'usuario')NOT NULL
);
CREATE TABLE movimentaçoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    tipo ENUM('ADICIONAR', 'RETIRAR') NOT NULL,
    quantidade INT NOT NULL,
    responsavel VARCHAR(100),
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES itens(id)
);
INSERT INTO usuario (nome, senha, tipo)
VALUES(
    'administrador'
    '1000'
    'admin'
);
CREATE TABLE historico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    quantidade INT NOT NULL,
    acao VARCHAR(255)
);
SELECT * FROM movimentaçoes;
SELECT * FROM usuario;
SELECT * FROM historico;
SELECT * FROM estoque_almoxarifado;