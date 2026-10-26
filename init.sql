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

SELECT * FROM estoque_almoxarifado;

CREATE TABLE funcionario(
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    funcao VARCHAR(255),
    SENHA VARCHAR(255)
);

INSERT INTO funcionario (nome,funcao,senha)
VALUES ('vampeta','gogoboy','123');

SELECT * FROM funcionario

CREATE TABLE historico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    quantidade INT NOT NULL,
    acao VARCHAR(255)
);

SELECT * FROM historico