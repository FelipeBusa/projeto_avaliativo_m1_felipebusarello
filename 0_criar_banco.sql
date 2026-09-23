-- PROJETO AVALIATIVO - MÓDULO 1
-- Arquivo: 0_criar_banco.sql
-- Banco de Dados: transparencia

/* 
Fase 0 - Banco e tabelas (0_criar_banco.sql): 
Criar o database e as 8 tabelas. 
As 4 tabelas Raw têm todas as colunas VARCHAR e sem constraints; 
As 4 tabelas Silver são tipadas e têm PRIMARY KEY, FOREIGN KEY e 
mais 2 constraints por tabela (NOT NULL, CHECK e UNIQUE), declaradas dentro do CREATE TABLE.
*/

-- =======
-- 1. CRIAÇÃO DO BANCO DE DADOS
CREATE DATABASE transparencia;


-- =======
-- 2. TABELAS RAW
CREATE TABLE raw_viagem (
    identificador_processo_viagem VARCHAR,
    numero_proposta_pcdp VARCHAR,
    situacao VARCHAR,
    viagem_urgente VARCHAR,
    justificativa_urgencia_viagem VARCHAR,
    codigo_orgao_superior VARCHAR,
    nome_orgao_superior VARCHAR,
    codigo_orgao_solicitante VARCHAR,
    nome_orgao_solicitante VARCHAR,
    cpf_viajante VARCHAR,
    nome VARCHAR,
    cargo VARCHAR,
    funcao VARCHAR,
    descricao_funcao VARCHAR,
    periodo_data_inicio VARCHAR,
    periodo_data_fim VARCHAR,
    destinos VARCHAR,
    motivo VARCHAR,
    valor_diarias VARCHAR,
    valor_passagens VARCHAR,
    valor_devolucao VARCHAR,
    valor_outros_gastos VARCHAR
);


CREATE TABLE raw_pagamento (
    identificador_processo_viagem VARCHAR,
    numero_proposta_pcdp VARCHAR,
    codigo_orgao_superior VARCHAR,
    nome_orgao_superior VARCHAR,
    codigo_orgao_pagador VARCHAR,
    nome_orgao_pagador VARCHAR,
    codigo_unidade_gestora_pagadora VARCHAR,
    nome_unidade_gestora_pagadora VARCHAR,
    tipo_pagamento VARCHAR,
    valor VARCHAR
);


CREATE TABLE raw_passagem (
    identificador_processo_viagem VARCHAR,
    numero_proposta_pcdp VARCHAR,
    meio_transporte VARCHAR,
    pais_origem_ida VARCHAR,
    uf_origem_ida VARCHAR,
    cidade_origem_ida VARCHAR,
    pais_destino_ida VARCHAR,
    uf_destino_ida VARCHAR,
    cidade_destino_ida VARCHAR,
    pais_origem_volta VARCHAR,
    uf_origem_volta VARCHAR,
    cidade_origem_volta VARCHAR,
    pais_destino_volta VARCHAR,
    uf_destino_volta VARCHAR,
    cidade_destino_volta VARCHAR,
    valor_passagem VARCHAR,
    taxa_servico VARCHAR,
    data_emissao_compra VARCHAR,
    hora_emissao_compra VARCHAR
);


CREATE TABLE raw_trecho (
    identificador_processo_viagem VARCHAR,
    numero_proposta_pcdp VARCHAR,
    sequencia_trecho VARCHAR,
    origem_data VARCHAR,
    origem_pais VARCHAR,
    origem_uf VARCHAR,
    origem_cidade VARCHAR,
    destino_data VARCHAR,
    destino_pais VARCHAR,
    destino_uf VARCHAR,
    destino_cidade VARCHAR,
    meio_transporte VARCHAR,
    numero_diarias VARCHAR,
    missao VARCHAR
);




-- =======
-- 3. TABELAS SILVER
CREATE TABLE silver_viagem (
    id_viagem VARCHAR(20) PRIMARY KEY,
    num_proposta VARCHAR(20),
    situacao VARCHAR(50),
    viagem_urgente VARCHAR(5),
    cod_orgao_superior VARCHAR(20),
    nome_orgao_superior VARCHAR(255) NOT NULL,
    nome_viajante VARCHAR(255),
    cargo VARCHAR(255),
    data_inicio DATE,
    data_fim DATE,
    destinos VARCHAR(4000),
    motivo VARCHAR(4000),
    valor_diarias DECIMAL(10,2) CHECK (valor_diarias >= 0),
    valor_passagens DECIMAL(10,2),
    valor_devolucao DECIMAL(10,2),
    valor_outros_gastos DECIMAL(10,2),
    valor_total DECIMAL(12,2),
    duracao_dias INT
);


CREATE TABLE silver_passagem (
    id_passagem INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL,
    meio_transporte VARCHAR(50),
    pais_origem_ida VARCHAR(60),
    uf_origem_ida VARCHAR(40),
    cidade_origem_ida VARCHAR(80),
    pais_destino_ida VARCHAR(60),
    uf_destino_ida VARCHAR(40),
    cidade_destino_ida VARCHAR(80),
    valor_passagem DECIMAL(10,2) CHECK (valor_passagem >= 0),
    taxa_servico DECIMAL(10,2) CHECK (taxa_servico >= 0),
    data_emissao DATE,
    CONSTRAINT fk_passagem_viagem
        FOREIGN KEY (id_viagem)
        REFERENCES silver_viagem(id_viagem)
);


CREATE TABLE silver_pagamento (
    id_pagamento INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL,
    num_proposta VARCHAR(20),
    nome_orgao_pagador VARCHAR(255),
    nome_ug_pagadora VARCHAR(255),
    tipo_pagamento VARCHAR(50) NOT NULL,
    valor DECIMAL(10,2) CHECK (valor >= 0),
    CONSTRAINT fk_pagamento_viagem
        FOREIGN KEY (id_viagem)
        REFERENCES silver_viagem(id_viagem)
);


CREATE TABLE silver_trecho (
    id_trecho INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL,
    sequencia_trecho INT,
    origem_data DATE,
    origem_uf VARCHAR(40),
    origem_cidade VARCHAR(80),
    destino_data DATE,
    destino_uf VARCHAR(40),
    destino_cidade VARCHAR(80),
    meio_transporte VARCHAR(50),
    numero_diarias DECIMAL(10,2) CHECK (numero_diarias >= 0),
    CONSTRAINT fk_trecho_viagem
        FOREIGN KEY (id_viagem)
        REFERENCES silver_viagem(id_viagem),
    CONSTRAINT uq_trecho_viagem_sequencia
        UNIQUE (id_viagem, sequencia_trecho)
);



-- =======
-- 4. VALIDAÇÃO CRIAÇÃO DAS TABELAS RAW E SILVER
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;


-- =======
-- 5. VALIDAÇÃO ESTRUTURAS DAS COLUNAS
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


-- =======
-- 6. VALIDAÇÃO DAS CONSTRAINTS
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
	

-- =======
-- 7. VALIDAÇÃO RELACIONAMENTOS
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