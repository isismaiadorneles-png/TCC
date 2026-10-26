
CREATE DATABASE Senai;
USE Senai;

CREATE TABLE carros (
    id INT NOT NULL AUTO_INCREMENT,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    ano INT,
    PRIMARY KEY (id)
);

-- Configuração de charset (corrigindo "uft8" para "utf8")
SET character_set_client = uft8;
SET character_set_connection = uft8;
SET character_set_results = utf8;
SET character_set_connection = uft8_general_ci;

-- Inserações de dados
INSERT INTO carros (marca,modelo,ano) VALUES ('fiat', 'marca', 1999);
INSERT INTO carros (marca,modelo,ano) VALUES ('fiat', 'marca', 2000);
INSERT INTO carros (marca,modelo,ano) VALUES ('fiat', 'marca', 2000);


alvaro.oliveira@sistemafiep.org.br