# ============================================================
# PROJETO AVALIATIVO - MÓDULO 1
# Arquivo: 2_transformar.py
# ============================================================

"""
Transformar os dados das tabelas Raw para as tabelas Silver

ATENÇÃO:
Antes de executar esse arquivo, deve ser executado o arquivo: 1_extrair.py

Etapas:
    1. Ler e Limpar os dados.
    2. Converter os tipos de dados.
    3. Calcular valor_total e duracao_dias.
    4. Validar chaves e relacionamentos.
    5. Carregar as quatro tabelas Silver em uma transação

A tabela silver_viagem é carregada primeiro para respeitar as chaves
estrangeiras das tabelas relacionadas.

Pode ser executado várias vezes:
    As tabelas são limpas antes de cada nova carga.
"""

# ============================================================
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# ============================================================
import pandas as pd
from psycopg2.extras import execute_values
from PostgreSQL.banco import conectar


# ============================================================
# 2. FUNÇÕES DE LIMPEZA E CONVERSÃO
# ============================================================
def limpar_texto(texto):
    """ Remove espaços extras e converte texto vazio em None """

    if texto is None or pd.isna(texto):
        return None

    texto = str(texto).strip()
    return texto if texto else None

def converter_data(data):
    """ Converte uma data  DD/MM/AAAA para date. """

    data = limpar_texto(data)

    if data is None:
        return None

    try:
        return pd.to_datetime(
            data,
            format="%d/%m/%Y",
            errors="raise",
        ).date()
    except (ValueError, TypeError):
        return None

def converter_decimal(valor):
    """ Converte valores com vírgula decimal para número. """

    valor = limpar_texto(valor)
    if valor is None:
        return None

    try:
        return float(valor.replace(",", "."))
    except (ValueError, TypeError):
        return None

def converter_inteiro(valor):
    """ Converte valor para inteiro. """

    valor = limpar_texto(valor)

    if valor is None:
        return None

    try:
        numero = float(valor.replace(",", "."))
        if numero.is_integer():
            return int(numero)
        return None
    except (ValueError, TypeError):
        return None

def limpar_colunas_texto(df, colunas):
    """Aplica a limpeza de texto às colunas informadas."""

    for coluna in colunas:
        df[coluna] = df[coluna].apply(limpar_texto)
    return df

def converter_colunas_data(df, colunas):
    """Converte as colunas de data informadas."""

    for coluna in colunas:
        df[coluna] = df[coluna].apply(converter_data)
    return df

def converter_colunas_decimal(df, colunas):
    """Converte as colunas numéricas informadas."""

    for coluna in colunas:
        df[coluna] = df[coluna].apply(converter_decimal)
    return df

def validar_valores_nao_negativos(df, colunas, tabela):
    """
    Trata valores negativos como nulos nas colunas submetidas
    a restrições CHECK de não negatividade.

    A tabela Raw permanece inalterada.
    """

    for coluna in colunas:
        negativos = df[coluna].lt(0).fillna(False)
        quantidade = int(negativos.sum())

        if quantidade:
            print(
                f"Aviso: {tabela}.{coluna}: "
                f"{quantidade:,} valores negativos convertidos em NULL."
            )
            df.loc[negativos, coluna] = None

    return df


# ============================================================
# 3. TRANSFORMAÇÃO TABELA VIAGEM
# ============================================================
def transformar_viagem(conexao):
    """ Limpa os dados da tabela viagem e calcula campos derivados """

    df = pd.read_sql("SELECT * FROM raw_viagem",conexao)
    print(f"raw_viagem: {len(df):,} registros lidos.")

    colunas_texto = [
        "id_viagem", "num_proposta", "situacao", "viagem_urgente", "cod_orgao_superior",
        "nome_orgao_superior", "nome_viajante","cargo", "destinos","motivo",
    ]

    limpar_colunas_texto(df, colunas_texto)

    converter_colunas_data(df,["data_inicio", "data_fim"],)

    converter_colunas_decimal(df,[
            "valor_diarias",
            "valor_passagens",
            "valor_devolucao",
            "valor_outros_gastos",
        ],)

    validar_valores_nao_negativos(df,
        ["valor_diarias"],
        "silver_viagem",
    )

    # Soma das despesas menos as devoluções.
    # Valores ausentes são considerados zero neste cálculo.
    df["valor_total"] = (
        df["valor_diarias"].fillna(0)
        + df["valor_passagens"].fillna(0)
        + df["valor_outros_gastos"].fillna(0)
        - df["valor_devolucao"].fillna(0)
    ).round(2)

    # A duração inclui o primeiro e o último dia da viagem.
    inicio = pd.to_datetime(df["data_inicio"])
    fim = pd.to_datetime(df["data_fim"])

    df["duracao_dias"] = (fim - inicio).dt.days + 1
    print("Transformação de silver_viagem concluída.")
    return df


# ============================================================
# 4. TRANSFORMAÇÃO DA TABELA PAGAMENTO
# ============================================================
def transformar_pagamento(conexao):
    """Limpa os pagamentos e converte seus valores."""

    df = pd.read_sql("SELECT * FROM raw_pagamento", conexao)
    print(f"raw_pagamento: {len(df):,} registros lidos.")

    total_inicial = len(df)
    df = df.drop_duplicates().copy()

    print(
        "Duplicatas exatas removidas de raw_pagamento: "
        f"{total_inicial - len(df):,}"
    )

    colunas_texto = ["id_viagem", "num_proposta", "nome_orgao_pagador", "nome_ug_pagadora",
        "tipo_pagamento",]

    limpar_colunas_texto(df, colunas_texto)

    df["valor"] = df["valor"].apply(converter_decimal)

    validar_valores_nao_negativos(
        df,
        ["valor"],
        "silver_pagamento",
    )

    print("Transformação de silver_pagamento concluída.")
    return df


# ============================================================
# 5. TRANSFORMAÇÃO DA TABELA PASSAGEM
# ============================================================
def transformar_passagem(conexao):
    """Limpa as passagens e converte valores e datas."""

    df = pd.read_sql("SELECT * FROM raw_passagem", conexao)
    print(f"raw_passagem: {len(df):,} registros lidos.")

    total_inicial = len(df)
    df = df.drop_duplicates().copy()

    print(
        "Duplicatas exatas removidas de raw_passagem: "
        f"{total_inicial - len(df):,}"
    )

    colunas_texto = ["id_viagem", "meio_transporte", "pais_origem_ida", "uf_origem_ida",
        "cidade_origem_ida", "pais_destino_ida", "uf_destino_ida", "cidade_destino_ida",
    ]

    limpar_colunas_texto(df, colunas_texto)

    converter_colunas_decimal(
        df,
        ["valor_passagem", "taxa_servico"],
    )

    converter_colunas_data(
        df,
        ["data_emissao"],
    )

    validar_valores_nao_negativos(
        df,
        ["valor_passagem", "taxa_servico"],
        "silver_passagem",
    )

    print("Transformação de silver_passagem concluída.")
    return df


# ============================================================
# 6. TRANSFORMAÇÃO DA TABELA TRECHO
# ============================================================
def transformar_trecho(conexao):
    """Limpa os trechos e converte seus tipos de dados."""

    df = pd.read_sql("SELECT * FROM raw_trecho", conexao)
    print(f"raw_trecho: {len(df):,} registros lidos.")

    colunas_texto = ["id_viagem", "origem_uf", "origem_cidade", "destino_uf",
        "destino_cidade", "meio_transporte",]

    limpar_colunas_texto(df, colunas_texto)

    df["sequencia_trecho"] = (
        df["sequencia_trecho"].apply(converter_inteiro)
    )

    converter_colunas_data(
        df,
        ["origem_data", "destino_data"],
    )

    df["numero_diarias"] = (
        df["numero_diarias"].apply(converter_decimal)
    )

    validar_valores_nao_negativos(
        df,
        ["numero_diarias"],
        "silver_trecho",
    )

    print("Transformação de silver_trecho concluída.")
    return df


# ============================================================
# 7. PREPARAÇÃO DAS TABELAS SILVER
# ============================================================
def preparar_tabela(df, colunas):
    """Seleciona e organiza somente as colunas da tabela Silver."""

    return df[colunas].copy()

COLUNAS_SILVER = {
    "silver_viagem": [
        "id_viagem", "num_proposta", "situacao", "viagem_urgente",
        "cod_orgao_superior", "nome_orgao_superior", "nome_viajante", "cargo", "data_inicio",
        "data_fim", "destinos", "motivo", "valor_diarias", "valor_passagens", "valor_devolucao",
        "valor_outros_gastos", "valor_total", "duracao_dias",],

    "silver_pagamento": [
        "id_viagem","num_proposta","nome_orgao_pagador",
        "nome_ug_pagadora","tipo_pagamento","valor",],

    "silver_passagem": [
        "id_viagem", "meio_transporte", "pais_origem_ida", "uf_origem_ida",
        "cidade_origem_ida", "pais_destino_ida", "uf_destino_ida", "cidade_destino_ida",
        "valor_passagem", "taxa_servico", "data_emissao",],

    "silver_trecho": [
        "id_viagem", "sequencia_trecho", "origem_data", "origem_uf", "origem_cidade",
        "destino_data", "destino_uf", "destino_cidade", "meio_transporte", "numero_diarias",],
}


# ============================================================
# 8. VALIDAÇÃO DOS DADOS ANTES DA CARGA
# ============================================================
def validar_dados(df_viagem, df_pagamento, df_passagem, df_trecho):
    """Verifica campos obrigatórios e relacionamentos."""

    # Viagem: chave primária e nome obrigatório.
    if df_viagem["id_viagem"].isna().any():
        raise ValueError(
            "silver_viagem: existem registros sem id_viagem."
        )

    if df_viagem["id_viagem"].duplicated().any():
        raise ValueError(
            "silver_viagem: existem id_viagem duplicados."
        )

    if df_viagem["nome_orgao_superior"].isna().any():
        raise ValueError(
            "silver_viagem: nome_orgao_superior é obrigatório."
        )

    # Valores obrigatórios em pagamento.
    if df_pagamento["tipo_pagamento"].isna().any():
        raise ValueError(
            "silver_pagamento: existem tipos de pagamento vazios."
        )

    # Todos os registros filhos devem possuir uma viagem válida.
    ids_viagem = set(df_viagem["id_viagem"])

    tabelas_filhas = {
        "silver_pagamento": df_pagamento,
        "silver_passagem": df_passagem,
        "silver_trecho": df_trecho,
    }

    for tabela, df in tabelas_filhas.items():
        if df["id_viagem"].isna().any():
            raise ValueError(
                f"{tabela}: existem registros sem id_viagem."
            )

        ids_invalidos = ~df["id_viagem"].isin(ids_viagem)

        if ids_invalidos.any():
            quantidade = int(ids_invalidos.sum())

            raise ValueError(
                f"{tabela}: {quantidade:,} registros referenciam "
                "id_viagem inexistente em silver_viagem."
            )

    # Restrição UNIQUE (id_viagem, sequencia_trecho).
    chaves_trecho = df_trecho[
        ["id_viagem", "sequencia_trecho"]
    ]

    duplicados = chaves_trecho.duplicated(keep=False)

    if duplicados.any():
        quantidade = int(duplicados.sum())

        raise ValueError(
            "silver_trecho: foram encontrados "
            f"{quantidade:,} registros com combinação "
            "(id_viagem, sequencia_trecho) duplicada. "
            "Verifique os dados antes de carregar."
        )

    print("Validações de integridade concluídas.")


# ============================================================
# 9. LIMPEZA E CARGA DAS TABELAS SILVER
# ============================================================
def limpar_tabelas_silver(conexao):
    """Limpa as quatro tabelas sem confirmar a transação."""

    with conexao.cursor() as cursor:
        cursor.execute(
            """
            TRUNCATE TABLE
                silver_pagamento,
                silver_passagem,
                silver_trecho,
                silver_viagem
            RESTART IDENTITY
            """
        )

    print("Tabelas Silver preparadas para nova carga.")

def carregar_tabela(conexao, tabela, df):
    """Insere os dados em lotes, sem confirmar a transação."""

    if tabela not in COLUNAS_SILVER:
        raise ValueError(f"Tabela não permitida: {tabela}")

    if df.empty:
        print(f"{tabela}: nenhum registro para carregar.")
        return

    colunas = list(df.columns)
    nomes_colunas = ", ".join(colunas)

    sql_insert = f"""
        INSERT INTO {tabela} ({nomes_colunas})
        VALUES %s
    """

    tamanho_lote = 5000

    with conexao.cursor() as cursor:
        for inicio in range(0, len(df), tamanho_lote):
            lote = df.iloc[inicio:inicio + tamanho_lote]

            linhas = [
                tuple(
                    None if pd.isna(valor) else valor
                    for valor in linha
                )
                for linha in lote.itertuples(
                    index=False,
                    name=None,
                )
            ]

            execute_values(
                cursor,
                sql_insert,
                linhas,
                page_size=tamanho_lote,
            )

    print(f"{tabela}: {len(df):,} registros carregados.")

def conferir_tabelas_silver(conexao):
    """Consulta e exibe a quantidade de registros de cada tabela Silver."""

    sql = """
        SELECT 'silver_viagem' AS tabela, COUNT(*) AS registros
        FROM silver_viagem

        UNION ALL

        SELECT 'silver_pagamento', COUNT(*)
        FROM silver_pagamento

        UNION ALL

        SELECT 'silver_passagem', COUNT(*)
        FROM silver_passagem

        UNION ALL

        SELECT 'silver_trecho', COUNT(*)
        FROM silver_trecho;
    """

    cursor = conexao.cursor()

    try:
        cursor.execute(sql)
        resultados = cursor.fetchall()

        print("\nConferência dos registros das tabelas Silver:")
        print("-" * 45)

        for tabela, registros in resultados:
            print(f"{tabela}: {registros:,} registros encontrados")

        print("-" * 45)

    finally:
        cursor.close()


# ============================================================
# 10. EXECUÇÃO PRINCIPAL
# ============================================================
def main():
    """Executa a transformação e a carga completa das Silver."""

    conexao = conectar()

    try:
        # 1. Transformação de todas as tabelas.
        df_viagem = transformar_viagem(conexao)
        df_pagamento = transformar_pagamento(conexao)
        df_passagem = transformar_passagem(conexao)
        df_trecho = transformar_trecho(conexao)

        # 2. Preparação das colunas.
        df_viagem = preparar_tabela(
            df_viagem,
            COLUNAS_SILVER["silver_viagem"],
        )

        df_pagamento = preparar_tabela(
            df_pagamento,
            COLUNAS_SILVER["silver_pagamento"],
        )

        df_passagem = preparar_tabela(
            df_passagem,
            COLUNAS_SILVER["silver_passagem"],
        )

        df_trecho = preparar_tabela(
            df_trecho,
            COLUNAS_SILVER["silver_trecho"],
        )

        # 3. Validação antes de limpar as tabelas atuais.
        validar_dados(df_viagem, df_pagamento, df_passagem,df_trecho,)

        # 4. Limpeza e carga na ordem dos relacionamentos.
        limpar_tabelas_silver(conexao)
        carregar_tabela(conexao, "silver_viagem", df_viagem)
        carregar_tabela(conexao, "silver_pagamento", df_pagamento)
        carregar_tabela(conexao, "silver_passagem", df_passagem)
        carregar_tabela(conexao, "silver_trecho", df_trecho)

        # 5. Confere os dados antes de confirmar a transação.
        conferir_tabelas_silver(conexao)

        # 6. Confirma a carga completa.
        conexao.commit()
        print("\nCarga completa das quatro tabelas Silver concluída.")

    except Exception as erro:
        conexao.rollback()
        print(f"\nErro no processo. Alterações revertidas: {erro}")
        raise

    finally:
        conexao.close()

if __name__ == "__main__":
    main()
