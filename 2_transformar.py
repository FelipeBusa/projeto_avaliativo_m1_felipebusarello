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
    """ Remove espaços extras e converte texto vazio em None """

    if texto is None:
        return None

    texto = str(texto).strip()

    if texto == "":
        return None

    return texto


def converter_data(data):
    """ Converte uma data  DD/MM/AAAA para date. """

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
    """ Converte valores com vírgula decimal para número. """

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
# 3.1. TRANSFORMAÇÃO DOS DADOS
# ============================================================
def transformar_viagem(conexao):
    """ Limpa os dados da raw_viagem e calcula campos derivados """

# Leitura da tabela Raw
    df = pd.read_sql("SELECT * FROM raw_viagem",conexao)
    print(f"raw_viagem: {len(df):,} registros lidos.")

# Limpeza dos campos de texto
    colunas_texto = [
        "id_viagem", "num_proposta", "situacao", "viagem_urgente", "cod_orgao_superior",
        "nome_orgao_superior", "nome_viajante","cargo", "destinos","motivo",
    ]

    for coluna in colunas_texto:
        df[coluna] = df[coluna].apply(limpar_texto)

# Conversão das datas
    df["data_inicio"] = df["data_inicio"].apply(converter_data)
    df["data_fim"] = df["data_fim"].apply(converter_data)

#  Conversão dos valores financeiros
    colunas_valores = ["valor_diarias", "valor_passagens", "valor_devolucao","valor_outros_gastos",]

    for coluna in colunas_valores:
        df[coluna] = df[coluna].apply(converter_decimal)

# Cálculo do valor total
    df["valor_total"] = (
        df["valor_diarias"].fillna(0)
        + df["valor_passagens"].fillna(0)
        + df["valor_outros_gastos"].fillna(0)
        - df["valor_devolucao"].fillna(0)
    ).round(2)


# Cálculo da duração da viagem
    df["duracao_dias"] = (
        pd.to_datetime(df["data_fim"])
        - pd.to_datetime(df["data_inicio"])
    ).dt.days + 1

    print("Transformação da silver_viagem concluída.")
    return df

# ============================================================
# 3.2. PREPARAÇÃO CARGA DOS DADOS
# ============================================================
def preparar_tabela(df, colunas):
    """ Seleciona e organiza as colunas para a carga no PostgreSQL."""
    return df[colunas].copy()


# ============================================================
# 3.3. LIMPEZA DAS TABELAS SILVER 
# ============================================================
def limpar_tabelas_silver(conexao): 
    """Limpa as tabelas Silver antes de uma nova carga completa.""" 
    
    executar( 
             conexao, 
             """ 
             TRUNCATE TABLE 
                silver_pagamento, 
                silver_passagem, 
                silver_trecho, 
                silver_viagem 
            """, 
        ) 
    
    print("Tabelas Silver limpas para nova carga.")


# ============================================================
# 3.4 CARGA DOS DADOS 
# ============================================================
def carregar_tabela(conexao, tabela, df):
    """ Carrega os dados preparados na tabela 'silver'."""

# Tabelas permitidas para a carga
    tabelas_permitidas = [
        "silver_viagem",
        "silver_pagamento",
        "silver_passagem",
        "silver_trecho",
    ]

    if tabela not in tabelas_permitidas:
        raise ValueError(f"Tabela não permitida: {tabela}")

# Organiza os nomes das colunas e os parâmetros SQL
    colunas = list(df.columns)
    nomes_colunas = ", ".join(colunas)
    parametros = ", ".join(["%s"] * len(colunas))

    sql_insert = f"""
        INSERT INTO {tabela} ({nomes_colunas})
        VALUES ({parametros})
    """
    
# Converte o DataFrame em lista de tuplas
    linhas = [
        tuple(
            None if pd.isna(valor) else valor
            for valor in linha
        )
        for linha in df.itertuples(index=False,name=None)
    ]

# Insere os dados em lote
    inserir_em_lote(conexao,sql_insert,linhas)
    print(f"{tabela}: {len(linhas):,} registros carregados.")


# ============================================================ 
# 4. EXECUÇÃO PRINCIPAL 
# ============================================================ 
def main(): 
    """Executa a transformação e a carga da silver_viagem.""" 
    conexao = conectar() 
    try: 
        # Transformação 
        df_viagem = transformar_viagem(conexao) 
        
        # Preparação 
        colunas_viagem = [ 
            "id_viagem", "num_proposta", "situacao", "viagem_urgente", "cod_orgao_superior", 
            "nome_orgao_superior", "nome_viajante", "cargo", "data_inicio", "data_fim", 
            "destinos", "motivo", "valor_diarias", "valor_passagens", "valor_devolucao", 
            "valor_outros_gastos", "valor_total", "duracao_dias", 
            ] 
        
        df_viagem = preparar_tabela(df_viagem, colunas_viagem) 
        
        # Limpeza das tabelas antes da carga completa
        limpar_tabelas_silver(conexao)

        # Carga da tabela Viagem
        carregar_tabela(conexao, "silver_viagem", df_viagem)
        
        # Confirma as alterações no banco 
        conexao.commit() 
        
        print("Carga da silver_viagem concluída com sucesso.") 
    
    except Exception as erro: 
        conexao.rollback() 
        print(f"Erro no processo: {erro}") 
        raise 
    
    finally: 
        conexao.close() 

if __name__ == "__main__": 
    main()