# ============================================================
# PROJETO AVALIATIVO - MÓDULO 1
# Arquivo: 1_extrair.py
# ============================================================


"""
Extração dos dados: Arquivos CSV para Tabelas Raw

ATENÇÃO:
Antes de executar este arquivo, deve ser executado o arquivo: 0_criar_banco.sql

O que este script faz:
  1. Baixa os arquivos de dados.
  2. Extrai os arquivos CSV.
  3. Lê os arquivos CSV.
  4. Grava os dados nas tabelas Raw.
  5. Pode ser executado várias vezes, pois as tabelas Raw são limpas antes de uma nova carga.
"""

# ============================================================
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# ============================================================
import io
import zipfile
import pandas as pd
import requests
from bs4 import BeautifulSoup

from PostgreSQL.banco import conectar
from PostgreSQL.config import (
    ARQUIVOS,
    CSV_ENCODING,
    CSV_SEPARADOR,
    DRIVE_FILE_ID,
    TAMANHO_BLOCO,
)


# ============================================================
# 2. CONFIGURAÇÃO DO DOWNLOAD
# ============================================================
if not DRIVE_FILE_ID:
    raise RuntimeError(
        "Cole o ID do arquivo do Drive na variável "
        "DRIVE_FILE_ID do config.py."
    )

URL_DOWNLOAD = (
    f"https://drive.google.com/uc?export=download&id={DRIVE_FILE_ID}"
)


# ============================================================
# 3. DOWNLOAD E VALIDAÇÃO DO ARQUIVO
# ============================================================
def baixar_arquivo(url):
    """Baixa o arquivo ZIP do Google Drive."""

    try:
        sessao = requests.Session()
        resposta = sessao.get(url, timeout=60)
        resposta.raise_for_status()

        if "text/html" in resposta.headers.get("Content-Type", ""):
            soup = BeautifulSoup(resposta.text, "html.parser")
            formulario = soup.find("form")

            if formulario:
                dados = {
                    campo.get("name"): campo.get("value", "")
                    for campo in formulario.find_all("input")
                    if campo.get("name")
                }
                resposta = sessao.get(
                    formulario.get("action"),
                    params=dados,
                    timeout=60,
                )
                resposta.raise_for_status()

        return resposta.content

    except Exception as erro:
        print(
            f"ERRO ao obter os dados: "
            f"{type(erro).__name__}: {erro}"
        )
        raise

def verificar_conteudo_zip(arquivo_zip):
    """Valida o ZIP e retorna os arquivos encontrados."""

    try:
        with zipfile.ZipFile(io.BytesIO(arquivo_zip)) as zip_arquivo:
            arquivos = zip_arquivo.namelist()

            print("Arquivos encontrados no ZIP:")
            for arquivo in arquivos:
                print(f"    {arquivo}")

            return arquivos

    except zipfile.BadZipFile as erro:
        raise RuntimeError(
            "O arquivo baixado não é um .zip. Confira se o link do Drive "
            "está compartilhado como 'Qualquer pessoa com o link'."
        ) from erro


# ============================================================
# 4. COMANDOS DE INSERT
# ============================================================
sql_insert_viagem = """
    INSERT INTO raw_viagem (id_viagem,num_proposta,situacao,viagem_urgente,justificativa_urgencia,cod_orgao_superior,
        nome_orgao_superior,cod_orgao_solicitante,nome_orgao_solicitante,cpf_viajante,nome_viajante,
        cargo,funcao,descricao_funcao,data_inicio,data_fim,destinos,motivo,valor_diarias,
        valor_passagens,valor_devolucao,valor_outros_gastos)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

sql_insert_pagamento = """
    INSERT INTO raw_pagamento (id_viagem,num_proposta,cod_orgao_superior,nome_orgao_superior,cod_orgao_pagador,
        nome_orgao_pagador,cod_ug_pagadora,nome_ug_pagadora,tipo_pagamento,valor)
    VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s)
"""

sql_insert_passagem = """
    INSERT INTO raw_passagem (id_viagem,num_proposta,meio_transporte,pais_origem_ida,uf_origem_ida,
        cidade_origem_ida, pais_destino_ida,uf_destino_ida,cidade_destino_ida,pais_origem_volta,
        uf_origem_volta,cidade_origem_volta,pais_destino_volta,uf_destino_volta, cidade_destino_volta,
        valor_passagem,taxa_servico,data_emissao,hora_emissao)
    VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

sql_insert_trecho = """
    INSERT INTO raw_trecho (id_viagem,num_proposta,sequencia_trecho,origem_data,origem_pais,
        origem_uf,origem_cidade,destino_data,destino_pais,destino_uf,destino_cidade,
        meio_transporte,numero_diarias,missao)
    VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)
"""

COMANDOS_INSERT = {
    "2025_Viagem.csv": sql_insert_viagem,
    "2025_Pagamento.csv": sql_insert_pagamento,
    "2025_Passagem.csv": sql_insert_passagem,
    "2025_Trecho.csv": sql_insert_trecho,
}


# ============================================================
# 5. LIMPEZA DAS TABELAS RAW
# ============================================================
def limpar_tabelas_raw(conexao):
    """Remove os dados existentes das tabelas Raw."""

    cursor = conexao.cursor()
    try:
        for configuracao in ARQUIVOS.values():
            tabela = configuracao["tabela_raw"]
            cursor.execute(f"TRUNCATE TABLE {tabela}")
            print(f"Tabela {tabela} limpa com sucesso.")
    finally:
        cursor.close()


# ============================================================
# 6. LEITURA E CARGA DOS DADOS
# ============================================================
def carregar_dados(conexao, arquivo_zip):
    """Lê os CSVs em blocos e carrega as tabelas Raw."""

    quantidades_lidas = {}
    cursor = conexao.cursor()

    try:
        with zipfile.ZipFile(io.BytesIO(arquivo_zip)) as zip_arquivo:

            for nome_arquivo, configuracao in ARQUIVOS.items():
                arquivo_csv = configuracao["csv"]
                tabela_raw = configuracao["tabela_raw"]
                sql_insert = COMANDOS_INSERT[arquivo_csv]

                print(f"\nLendo arquivo: {arquivo_csv}")
                quantidade_total = 0

                with zip_arquivo.open(arquivo_csv) as arquivo:
                    leitor = pd.read_csv(
                        arquivo,
                        sep=CSV_SEPARADOR,
                        encoding=CSV_ENCODING,
                        dtype=str,
                        keep_default_na=False,
                        chunksize=TAMANHO_BLOCO,
                    )

                    for numero_bloco, bloco in enumerate(leitor, start=1):
                        quantidade_total += len(bloco)

                        linhas = [
                            tuple(linha)
                            for linha in bloco.itertuples(
                                index=False,
                                name=None,
                            )
                        ]

                        cursor.executemany(sql_insert, linhas)

                        print(
                            f"  Bloco {numero_bloco}: "
                            f"{len(bloco)} registros inseridos "
                            f"na {tabela_raw}."
                        )

                quantidades_lidas[arquivo_csv] = {
                    "tabela_raw": tabela_raw,
                    "quantidade": quantidade_total,
                }

        return quantidades_lidas

    finally:
        cursor.close()


# ============================================================
# 7. VALIDAÇÃO DA CARGA
# ============================================================
def validar_quantidade(
    arquivo_csv,
    tabela_raw,
    quantidade_esperada,
    quantidade_banco,
):
    """Compara os registros do CSV com os registros do banco."""

    print(
        f"\nArquivo: {arquivo_csv} possui "
        f"{quantidade_esperada} registros."
    )
    print(
        f"Tabela {tabela_raw} possui "
        f"{quantidade_banco} registros."
    )

    if quantidade_banco != quantidade_esperada:
        raise RuntimeError(
            f"ERRO: quantidade de registros divergente "
            f"para a tabela {tabela_raw}. "
            f"Esperado: {quantidade_esperada}. "
            f"Encontrado: {quantidade_banco}."
        )

    print("OK: carga correta.")


def validar_cargas(conexao, quantidades_lidas):
    """Valida a quantidade carregada em cada tabela Raw."""

    cursor = conexao.cursor()

    try:
        for arquivo_csv, dados in quantidades_lidas.items():
            tabela_raw = dados["tabela_raw"]

            cursor.execute(
                f"SELECT COUNT(*) FROM {tabela_raw}"
            )
            quantidade_banco = cursor.fetchone()[0]

            validar_quantidade(
                arquivo_csv,
                tabela_raw,
                dados["quantidade"],
                quantidade_banco,
            )

    finally:
        cursor.close()


# ============================================================
# 8. EXECUÇÃO PRINCIPAL
# ============================================================
def main():
    """Executa o processo completo de extração e carga Raw."""

    conexao = None

    try:
        print("\nConectando ao PostgreSQL...")
        conexao = conectar()
        print("Conexão com PostgreSQL estabelecida.")

        print("\nBaixando arquivo ZIP...")
        arquivo_zip = baixar_arquivo(URL_DOWNLOAD)
        print(f"Arquivo ZIP baixado: {len(arquivo_zip)} bytes.")

        arquivos_zip = verificar_conteudo_zip(arquivo_zip)

        arquivos_esperados = {
            configuracao["csv"]
            for configuracao in ARQUIVOS.values()
        }

        arquivos_faltantes = (
            arquivos_esperados - set(arquivos_zip)
        )

        if arquivos_faltantes:
            raise RuntimeError(
                "O arquivo ZIP não contém todos os CSVs esperados. "
                f"Arquivos faltantes: {sorted(arquivos_faltantes)}"
            )

        print("\nLimpando tabelas Raw...")
        limpar_tabelas_raw(conexao)

        print("\nIniciando leitura e carga dos CSVs...")
        quantidades_lidas = carregar_dados(
            conexao,
            arquivo_zip,
        )

        print("\nValidando quantidade de registros...")
        validar_cargas(
            conexao,
            quantidades_lidas,
        )

        conexao.commit()

        print(
            "\nTodos os dados foram carregados e validados com sucesso."
        )
        print("\nProcesso de extração e carga finalizado com sucesso.")

    except Exception as erro:
        if conexao:
            conexao.rollback()

        print(
            f"\nERRO na carga da camada Raw: "
            f"{type(erro).__name__}: {erro}"
        )
        raise

    finally:
        if conexao is not None:
            conexao.close()
            print("Conexão com PostgreSQL encerrada.")

if __name__ == "__main__":
    main()