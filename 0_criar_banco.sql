-- ============================================================
-- PROJETO AVALIATIVO - MÓDULO 1
-- Arquivo: 0_criar_banco.sql
-- Banco de Dados: transparencia
-- ============================================================

/*
Criação do banco de dados e das tabelas Raw e Silver.

ATENÇÃO:
O banco de dados deve ser criado primeiro.
Após a criação, é necessário conectar-se ao banco "transparencia" para executar as demais etapas.

O que este script faz:
  1. Cria o banco de dados.
  2. Remove tabelas e objetos existentes.
  3. Cria as tabelas Raw.
  4. Cria as tabelas Silver.
  5. Define PK, FK e constraints das tabelas Silver.
  6. Executa consultas para validação da estrutura.
*/


-- ============================================================
-- 1. CRIAÇÃO DO BANCO DE DADOS
-- ============================================================
CREATE DATABASE transparencia;


-- ============================================================
-- 2. LIMPEZA DOS OBJETOS EXISTENTES
-- ============================================================
/* Execute esta etapa já conectado ao banco "transparencia".
Serão apagados todas as tabelas/informações das estapas silver e gols, se existir. */
DROP VIEW IF EXISTS vw_gold_pagamento_resumo;
DROP VIEW IF EXISTS vw_gold_trecho_resumo;

DROP TABLE IF EXISTS gold_pagamento_resumo;
DROP TABLE IF EXISTS gold_trecho_resumo;

DROP TABLE IF EXISTS silver_pagamento;
DROP TABLE IF EXISTS silver_passagem;
DROP TABLE IF EXISTS silver_trecho;
DROP TABLE IF EXISTS silver_viagem;

DROP TABLE IF EXISTS raw_pagamento;
DROP TABLE IF EXISTS raw_passagem;
DROP TABLE IF EXISTS raw_trecho;
DROP TABLE IF EXISTS raw_viagem;


-- ============================================================
-- 3. CRIAÇÃO DAS TABELAS RAW
-- ============================================================
CREATE TABLE raw_viagem (
    id_viagem              VARCHAR(255),
    num_proposta           VARCHAR(255),
    situacao               VARCHAR(255),
    viagem_urgente         VARCHAR(255),
    justificativa_urgencia VARCHAR(4000),
    cod_orgao_superior     VARCHAR(255),
    nome_orgao_superior    VARCHAR(255),
    cod_orgao_solicitante  VARCHAR(255),
    nome_orgao_solicitante VARCHAR(255),
    cpf_viajante           VARCHAR(255),
    nome_viajante          VARCHAR(255),
    cargo                  VARCHAR(255),
    funcao                 VARCHAR(255),
    descricao_funcao       VARCHAR(255),
    data_inicio            VARCHAR(255),
    data_fim               VARCHAR(255),
    destinos               VARCHAR(4000),
    motivo                 VARCHAR(4000),
    valor_diarias          VARCHAR(255),
    valor_passagens        VARCHAR(255),
    valor_devolucao        VARCHAR(255),
    valor_outros_gastos    VARCHAR(255)
);

CREATE TABLE raw_pagamento (
    id_viagem           VARCHAR(255),
    num_proposta        VARCHAR(255),
    cod_orgao_superior  VARCHAR(255),
    nome_orgao_superior VARCHAR(255),
    cod_orgao_pagador   VARCHAR(255),
    nome_orgao_pagador  VARCHAR(255),
    cod_ug_pagadora     VARCHAR(255),
    nome_ug_pagadora    VARCHAR(255),
    tipo_pagamento      VARCHAR(255),
    valor               VARCHAR(255)
);

CREATE TABLE raw_passagem (
    id_viagem            VARCHAR(255),
    num_proposta         VARCHAR(255),
    meio_transporte      VARCHAR(255),
    pais_origem_ida      VARCHAR(255),
    uf_origem_ida        VARCHAR(255),
    cidade_origem_ida    VARCHAR(255),
    pais_destino_ida     VARCHAR(255),
    uf_destino_ida       VARCHAR(255),
    cidade_destino_ida   VARCHAR(255),
    pais_origem_volta    VARCHAR(255),
    uf_origem_volta      VARCHAR(255),
    cidade_origem_volta  VARCHAR(255),
    pais_destino_volta   VARCHAR(255),
    uf_destino_volta     VARCHAR(255),
    cidade_destino_volta VARCHAR(255),
    valor_passagem       VARCHAR(255),
    taxa_servico         VARCHAR(255),
    data_emissao         VARCHAR(255),
    hora_emissao         VARCHAR(255)
);

CREATE TABLE raw_trecho (
    id_viagem        VARCHAR(255),
    num_proposta     VARCHAR(255),
    sequencia_trecho VARCHAR(255),
    origem_data      VARCHAR(255),
    origem_pais      VARCHAR(255),
    origem_uf        VARCHAR(255),
    origem_cidade    VARCHAR(255),
    destino_data     VARCHAR(255),
    destino_pais     VARCHAR(255),
    destino_uf       VARCHAR(255),
    destino_cidade   VARCHAR(255),
    meio_transporte  VARCHAR(255),
    numero_diarias   VARCHAR(255),
    missao           VARCHAR(255)
);


-- ============================================================
-- 4. CRIAÇÃO DAS TABELAS SILVER
-- ============================================================
CREATE TABLE silver_viagem (
    id_viagem            VARCHAR(20)  NOT NULL,
    num_proposta         VARCHAR(20),
    situacao             VARCHAR(50),
    viagem_urgente       VARCHAR(5),
    cod_orgao_superior   VARCHAR(20),
    nome_orgao_superior  VARCHAR(255) NOT NULL,
    nome_viajante        VARCHAR(255),
    cargo                VARCHAR(255),
    data_inicio          DATE,
    data_fim             DATE,
    destinos             VARCHAR(4000),
    motivo               VARCHAR(4000),
    valor_diarias        DECIMAL(10,2),
    valor_passagens      DECIMAL(10,2),
    valor_devolucao      DECIMAL(10,2),
    valor_outros_gastos  DECIMAL(10,2),
    valor_total          DECIMAL(12,2),
    duracao_dias         INT,
    PRIMARY KEY (id_viagem),
    CONSTRAINT ck_viagem_valor_diarias 
		CHECK (valor_diarias >= 0)
);

CREATE TABLE silver_pagamento (
    id_pagamento       SERIAL,
    id_viagem          VARCHAR(20)  NOT NULL,
    num_proposta       VARCHAR(20),
    nome_orgao_pagador VARCHAR(255),
    nome_ug_pagadora   VARCHAR(255),
    tipo_pagamento     VARCHAR(50)  NOT NULL,
    valor              DECIMAL(10,2),
    PRIMARY KEY (id_pagamento),
    CONSTRAINT fk_pagamento_viagem 
		FOREIGN KEY (id_viagem) 
		REFERENCES silver_viagem (id_viagem),
    CONSTRAINT ck_pagamento_valor 
		CHECK (valor >= 0)
);

CREATE TABLE silver_passagem (
    id_passagem        SERIAL,
    id_viagem          VARCHAR(20)  NOT NULL,
    meio_transporte    VARCHAR(50),
    pais_origem_ida    VARCHAR(60),
    uf_origem_ida      VARCHAR(40),
    cidade_origem_ida  VARCHAR(80),
    pais_destino_ida   VARCHAR(60),
    uf_destino_ida     VARCHAR(40),
    cidade_destino_ida VARCHAR(80),
    valor_passagem     DECIMAL(10,2),
    taxa_servico       DECIMAL(10,2),
    data_emissao       DATE,
    PRIMARY KEY (id_passagem),
    CONSTRAINT fk_passagem_viagem 
		FOREIGN KEY (id_viagem) 
		REFERENCES silver_viagem (id_viagem),
    CONSTRAINT ck_passagem_valor 
		CHECK (valor_passagem >= 0),
    CONSTRAINT ck_passagem_taxa 
		CHECK (taxa_servico >= 0)
);

CREATE TABLE silver_trecho (
    id_trecho        SERIAL,
    id_viagem        VARCHAR(20)  NOT NULL,
    sequencia_trecho INT,
    origem_data      DATE,
    origem_uf        VARCHAR(40),
    origem_cidade    VARCHAR(80),
    destino_data     DATE,
    destino_uf       VARCHAR(40),
    destino_cidade   VARCHAR(80),
    meio_transporte  VARCHAR(50),
    numero_diarias   DECIMAL(10,2),
    PRIMARY KEY (id_trecho),
    CONSTRAINT fk_trecho_viagem 
		FOREIGN KEY (id_viagem) 
		REFERENCES silver_viagem (id_viagem),
    CONSTRAINT ck_trecho_diarias 
		CHECK (numero_diarias >= 0),
    CONSTRAINT uq_trecho_viagem_sequencia 
		UNIQUE (id_viagem, sequencia_trecho)
);


-- ============================================================
-- 5. VALIDAÇÃO DAS TABELAS
-- ============================================================
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;


-- ============================================================
-- 6. VALIDAÇÃO DAS COLUNAS
-- ============================================================
SELECT
    table_name,
    ordinal_position,
    column_name,
    data_type,
    character_maximum_length,
    numeric_precision,
    numeric_scale,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN (
      'silver_viagem',
      'silver_passagem',
      'silver_pagamento',
      'silver_trecho'
  )
ORDER BY
    table_name,
    ordinal_position;


-- ============================================================
-- 7. VALIDAÇÃO DAS CONSTRAINTS
-- ============================================================
SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
    AND tc.table_name = kcu.table_name
WHERE tc.table_schema = 'public'
  AND tc.table_name IN (
      'silver_viagem',
      'silver_passagem',
      'silver_pagamento',
      'silver_trecho'
  )
ORDER BY
    tc.table_name,
    tc.constraint_type,
    tc.constraint_name;
	

-- ============================================================
-- 8. VALIDAÇÃO DOS RELACIONAMENTOS
-- ============================================================
SELECT
    tc.table_name AS tabela,
    kcu.column_name AS coluna,
    ccu.table_name AS tabela_referenciada,
    ccu.column_name AS coluna_referenciada
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
  AND tc.table_name IN (
      'silver_viagem',
      'silver_passagem',
      'silver_pagamento',
      'silver_trecho'
  )
ORDER BY tc.table_name;