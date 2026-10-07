# ============================================================
# PROJETO AVALIATIVO - MÓDULO 1
# Arquivo: 2_transformar.py
# ============================================================

"""
Transformação dos dados: Tabela Raw para Tabela Silver


ATENÇÃO: 
Antes de executar esse arquivo, deve ser executado o arquivo: 1_extrair.py


O que este script faz:
  1. Lê as tabelas Raw.
  2. Ajusta os campos conforme funções específicas.
  3. Calcula novas colunas.
  4. Grava as tabelas Silver. A tabela silver_viagem deve ser carregada PRIMEIRO.

Pode ser executado várias vezes: 
    As tabelas sempre são limpadas antes da nova carga.
"""

# ============================================================
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# ============================================================
import warnings
import pandas as pd
from psycopg2.extras import execute_values
from datetime import datetime
from PostgreSQL.banco import conectar, executar, inserir_em_lote
from PostgreSQL.config import TAMANHO_BLOCO


# ============================================================
# 2. FUNÇÕES DE LIMPEZA E CONVERSÃO
# ============================================================
def limpar_texto(texto):
    """
    Remove espaços no início e no final do texto.
    Valores vazios são convertidos para None.
    Valores especiais da fonte serão preservados, como:
        - Sem informação
        - Sigiloso
        - Informações protegidas por sigilo
        - Inválido
    """

    if texto is None:
        return None

    texto = str(texto).strip()

    if texto == "":
        return None

    return texto


def converter_data(data):
    """ Converte uma data no formato DD/MM/AAAA para date. """

    if data is None:
        return None

    data = str(data).strip()

    if data == "":
        return None

    try:
        return pd.to_datetime(
            data,
            format="%d/%m/%Y",
        ).date()
    except (ValueError, TypeError):
        return None


def converter_decimal(valor):
    """ Converte valores numéricos com vírgula decimal para Decimal. """

    if valor is None:
        return None

    valor = str(valor).strip()

    if valor == "":
        return None

    try:
        return float(valor.replace(",", "."))
    except (ValueError, TypeError):
        return None


def converter_inteiro(valor):
    """ Converte valor para inteiro. """

    if valor is None:
        return None

    valor = str(valor).strip()

    if valor == "":
        return None

    try:
        return int(valor)
    except (ValueError, TypeError):
        return None


# ============================================================
# 3.1. TRANSFORMAÇÃO DOS DADOS - Tabela Viagem
# ============================================================
def transformar_viagem(conexao):
    """ Lê a tabela 'raw_viagem', realiza a limpeza e calcula os campos derivados. """

# --------------------------------------------------------
# Leitura da tabela Raw
    df = pd.read_sql("SELECT * FROM raw_viagem",conexao)
    print(f"raw_viagem: {len(df):,} registros lidos.")

# --------------------------------------------------------
# Limpeza dos campos de texto
    colunas_texto = [
        "id_viagem", "num_proposta", "situacao", "viagem_urgente", "cod_orgao_superior",
        "nome_orgao_superior", "nome_viajante","cargo", "destinos","motivo",
    ]

    for coluna in colunas_texto:
        df[coluna] = df[coluna].apply(limpar_texto)

# --------------------------------------------------------
# Conversão das datas
    df["data_inicio"] = df["data_inicio"].apply(converter_data)
    df["data_fim"] = df["data_fim"].apply(converter_data)

# --------------------------------------------------------
#  Conversão dos valores financeiros
    colunas_valores = ["valor_diarias", "valor_passagens", "valor_devolucao","valor_outros_gastos",]

    for coluna in colunas_valores:
        df[coluna] = df[coluna].apply(converter_decimal)

# --------------------------------------------------------
# Cálculo do valor total
    df["valor_total"] = (
        df["valor_diarias"].fillna(0)
        + df["valor_passagens"].fillna(0)
        + df["valor_outros_gastos"].fillna(0)
        - df["valor_devolucao"].fillna(0)
    ).round(2)


# --------------------------------------------------------
# Cálculo da duração da viagem
    df["duracao_dias"] = (
        pd.to_datetime(df["data_fim"])
        - pd.to_datetime(df["data_inicio"])
    ).dt.days + 1

    print("Transformação da silver_viagem concluída.")
    return df

# ============================================================
# 3.2. PREPARAÇÃO CARGA DOS DADOS - Tabela Viagem
# ============================================================
def preparar_viagem(df):
    """ Seleciona as colunas da 'silver_viagem' e organiza os dados na mesma ordem da tabela PostgreSQL."""

    colunas_silver = ["id_viagem", "num_proposta", "situacao", "viagem_urgente", "cod_orgao_superior",
        "nome_orgao_superior", "nome_viajante", "cargo", "data_inicio", "data_fim", "destinos",
        "motivo", "valor_diarias", "valor_passagens", "valor_devolucao", "valor_outros_gastos", "valor_total",
        "duracao_dias",]

    df = df[colunas_silver].copy()
    return df


# ============================================================
# 3.3 CARGA DOS DADOS - Tabela Silver 
# ============================================================
def carregar_viagem(conexao, df):
    """ Carrega os dados preparados na tabela 'silver_viagem'."""

# --------------------------------------------------------
# Limpa a tabela antes da nova carga
    executar( conexao, """ TRUNCATE TABLE silver_pagamento, silver_passagem, silver_trecho, silver_viagem """ )

# --------------------------------------------------------
# Inserção dos dados
    sql_insert = """
        INSERT INTO silver_viagem (id_viagem, num_proposta, situacao, viagem_urgente, cod_orgao_superior,
            nome_orgao_superior, nome_viajante, cargo, data_inicio, data_fim, destinos, motivo,
            valor_diarias, valor_passagens, valor_devolucao, valor_outros_gastos, valor_total, duracao_dias)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

# --------------------------------------------------------
# Converte o DataFrame em lista de tuplas
    linhas = [
        tuple(
            None if pd.isna(valor) else valor
            for valor in linha
        )
        for linha in df.itertuples(index=False,name=None)
    ]

# --------------------------------------------------------
# Insere os dados em lote
    inserir_em_lote(conexao,sql_insert,linhas)
    print(f"silver_viagem: {len(linhas):,} registros carregados.")

