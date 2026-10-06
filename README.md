# 📊 Projeto Avaliativo - Análise de Dados com Python | Módulo 1
**Felipe Busarello**  
**Curso:** Análise de Dados com Python  
**Turma:** 09 - 2026  
**Professores:** Cláudio Neves e Luana Pereira  


## 📌 Sobre o Projeto
Este projeto foi desenvolvido como parte do Projeto Avaliativo do Módulo 1 do curso de **Análise de Dados com Python**.  

O objetivo é desenvolver um pipeline de dados utilizando **Python, PostgreSQL e técnicas de ETL (Extract, Transform, Load)**, desde a extração dos dados até o tratamento, organização e análise das informações.  

O projeto utiliza dados de **viagens, passagens, trechos e pagamentos referentes ao ano de 2025**, disponibilizados em arquivos CSV.  

A solução será desenvolvida utilizando uma arquitetura de dados baseada nas camadas **Raw, Silver e Gold**, permitindo separar os dados brutos, os dados tratados e as informações preparadas para análise.


## 🎯 Objetivos
Os principais objetivos do projeto são:
* Desenvolver um processo de ETL utilizando Python;
* Realizar a extração dos dados a partir dos arquivos disponibilizados;
* Armazenar os dados brutos em uma camada Raw;
* Realizar tratamento e transformação dos dados;
* Armazenar os dados tratados em uma camada Silver;
* Utilizar PostgreSQL para armazenamento e organização dos dados;
* Realizar análises exploratórias sobre os dados;
* Criar consultas e indicadores para responder perguntas de negócio;
* Desenvolver visualizações para apoiar a interpretação dos resultados;
* Documentar o processo e aplicar boas práticas de versionamento utilizando Git e GitHub.


## 📊 Base de Dados
A base de dados utilizada no projeto contém informações relacionadas a viagens realizadas no período analisado.  
Os dados estão distribuídos inicialmente em quatro arquivos CSV:
* `2025_Viagem.csv`
* `2025_Pagamento.csv`
* `2025_Passagem.csv`
* `2025_Trecho.csv`
  
As informações abrangem dados como:
* identificação das viagens;
* propostas de viagem;
* órgãos envolvidos;
* viajantes;
* períodos das viagens;
* destinos;
* valores de diárias;
* valores de passagens;
* pagamentos;
* trechos e deslocamentos.

Os arquivos CSV não são versionados no GitHub. Eles são utilizados localmente durante o processo de extração e carga dos dados.


# 🔎 Processo de ETL
O processo de ETL será dividido em etapas, utilizando uma arquitetura composta pelas camadas **Raw, Silver e Gold**.  
```text
             Arquivos CSV
                  │
                  ▼
          ┌───────────────┐
          │     RAW       │
          │ Dados brutos  │
          └───────┬───────┘
                  │
             Transformação
                  │
                  ▼
          ┌───────────────┐
          │    SILVER     │
          │ Dados tratados│
          └───────┬───────┘
                  │
               Análises
                  │
                  ▼
          ┌───────────────┐
          │     GOLD      │
          │ Dados para    │
          │ análise       │
          └───────────────┘
```


## 1. Extração e Camada Raw
Nesta etapa, os arquivos CSV serão obtidos e carregados no banco de dados PostgreSQL.  

A camada Raw terá como objetivo **preservar os dados recebidos na origem**, evitando alterações de conteúdo durante a etapa de extração.  

As tabelas Raw foram estruturadas utilizando colunas `VARCHAR`, permitindo armazenar os valores conforme disponibilizados nos arquivos de origem.  

O processo de extração foi desenvolvido em Python e possui validações para verificar os arquivos recebidos, realizar a carga em blocos e comparar a quantidade de registros carregados com a quantidade existente nos arquivos de origem.


## 🔎 Análise e Qualidade Dos Dados
Antes da definição das regras de transformação, foi realizada uma análise exploratória das tabelas Raw.  
O objetivo desta etapa foi compreender a estrutura dos dados e identificar possíveis situações que deveriam ser consideradas durante a transformação, como:
* Tipos e formatos dos dados;
* Campos vazios;
* Valores ausentes ou representações de ausência;
* Formatos de datas;
* Formatos de valores numéricos;
* Registros duplicados;
* Identificadores sem duplicidade;
* Valores especiais;
* Relacionamento e repetição dos registros entre as tabelas.

### Volume Inicial Dos Dados
|**Tabela**|**Registros**|**Colunas**|
|--|--|--|
|`raw_viagem` | 341.860 | 22 |
| `raw_pagamento` | 606.916 | 10 |
| `raw_passagem` | 167.260 | 19 |
| `raw_trecho` | 763.349 | 14 | 
| **Total** | **1.879.385** | **-** |

### Principais Resultados da Análise
* A tabela `raw_viagem` possui **341.860 registros** e o campo `id_viagem` é único em todos os registros;
* A tabela `raw_pagamento` possui **606.916 registros** e apresenta registros completamente duplicados;
* A tabela `raw_passagem` possui **50 registros** completamente duplicados;
* A tabela `raw_trecho` não apresentou registros completamente duplicados;
* A repetição de `id_viagem` nas tabelas `raw_pagamento`, `raw_passagem` e `raw_trecho` é esperada, pois essas tabelas podem possuir vários registros relacionados a uma mesma viagem;
* As datas identificadas estão no formato `DD/MM/AAAA`;
* Os valores monetários estão representados originalmente utilizando **vírgula como separador decimal**;
* O campo `sequencia_trecho` apresenta valores inteiros;
* O campo `numero_diarias` apresenta valores numéricos com casas decimais;
* Foram encontrados valores como `Sem informação`, `Sigiloso`, `Informações protegidas por sigilo` e `Inválido`;
* Também foram identificados códigos de origem como `-1` e `-11`, utilizados pela própria fonte para representar situações específicas;
* Foram encontrados campos vazios que deverão ser tratados durante a transformação.

### Considerações Sobre os Dados
A análise demonstrou que nem todo valor que representa ausência de informação deve ser automaticamente convertido para `NULL`.

Valores como `Sem informação`, `Sigiloso`, `Informações protegidas por sigilo` e `Inválido` fazem parte dos dados disponibilizados pela fonte e possuem significado próprio.

Por esse motivo, as regras de transformação serão definidas considerando a **origem e o significado dos dados**, evitando alterações que possam causar perda de informação.

A repetição de `id_viagem` também não será utilizada isoladamente como critério para exclusão de registros, pois representa um relacionamento esperado entre uma viagem e seus respectivos pagamentos, passagens e trechos.


## 2. Transformação e Camada Silver
Nesta etapa, os dados armazenados na camada Raw serão tratados e transformados.  

As regras de transformação serão definidas a partir dos resultados da análise dos dados de origem.

Entre os tratamentos previstos estão:
* conversão de tipos de dados;
* conversão de datas;
* conversão de valores numéricos;
* criação de campos calculados;
* aplicação de regras de integridade;
* relacionamento entre as tabelas.

A camada Silver será composta por tabelas estruturadas e tipadas, com **chaves primárias, chaves estrangeiras e constraints** para garantir maior consistência dos dados.

As regras definitivas de transformação e os resultados da carga serão documentados após a execução desta etapa.


## 3. Análise e Camada Gold
A camada Gold será utilizada para preparar os dados para análise.  

Nesta etapa serão desenvolvidas consultas SQL, indicadores, tabelas agregadas e visualizações com o objetivo de responder perguntas de negócio relacionadas à base de dados.

As estruturas e análises da camada Gold serão documentadas após a conclusão da transformação da camada Silver.


# 📈 Análise Exploratória
Após a conclusão do tratamento e preparação dos dados, serão realizadas análises exploratórias para identificar:
* Padrões;
* Distribuições;
* Comportamentos;
* Relações entre variáveis;
* Possíveis inconsistências;
* Indicadores relevantes para o negócio.

As análises serão desenvolvidas utilizando SQL e Python.


# 📊 Visualizações
As visualizações serão desenvolvidas após a preparação da camada Gold.
 
Os gráficos serão utilizados para facilitar a interpretação dos dados e apoiar a apresentação dos resultados das análises.


# 💡 Principais Insights
Esta seção será preenchida após a conclusão das análises.  

Serão apresentados os principais insights identificados a partir dos dados e das perguntas de negócio definidas para o projeto.


# 🧠 Reflexão sobre ETL e Qualidade dos Dados
Ao final do projeto será apresentada uma reflexão sobre:
* qualidade dos dados de origem;
* dificuldades encontradas durante o processo de ETL;
* tratamentos necessários;
* importância da validação dos dados;
* integridade e consistência das informações;
* benefícios da separação das camadas Raw, Silver e Gold.


# 🛠️ Tecnologias e Técnicas Utilizadas
### Linguagens
* Python
* SQL


### Banco de Dados
* PostgreSQL


### Bibliotecas e Ferramentas
* Pandas
* Psycopg2
* VS Code
* Git
* GitHub
* Jupyter Notebook


### Técnicas
* ETL
* Manipulação de dados
* Limpeza e transformação de dados
* SQL
* Modelagem de banco de dados
* Arquitetura Medallion (Raw, Silver e Gold)
* Análise exploratória de dados
* Visualização de dados
* Controle de versão
* Validação de dados


# 📁 Estrutura do Projeto
```text
projeto_avaliativo_m1_felipebusarello/
│
├── Arquivos base/
│   └── arquivos compactados disponibilizados para o projeto
│
├── data/
│   ├── 2025_Pagamento.csv
│   ├── 2025_Passagem.csv
│   ├── 2025_Trecho.csv
│   └── 2025_Viagem.csv
│
├── PostgreSQL/
│   ├── banco.py
│   ├── .env.example
│   └── config.py
│
├── 0_criar_banco.sql
├── 1_extrair.py
├── 2_transformar.py
├── README.md
└── .gitignore
```

> **Observação:** arquivos contendo credenciais, dados locais e arquivos gerados automaticamente pelo Python não são versionados no GitHub.


# 🚀 Como Executar
## 1. Clonar o Repositório
```bash
git clone https://github.com/FelipeBusa/projeto_avaliativo_m1_felipebusarello.git
```


## 2. Acessar a Pasta do Projeto
```bash
cd projeto_avaliativo_m1_felipebusarello
```


## 3. Configurar o Ambiente
É necessário possuir Python e PostgreSQL instalados. 

As credenciais de acesso ao banco de dados devem ser configuradas localmente, utilizando o arquivo `.env`.  

O arquivo `.env.example` apresenta a estrutura das variáveis necessárias sem expor informações sensíveis.  


## 4. Instalar as Dependências
As principais bibliotecas utilizadas pelo projeto são:

pandas  
psycopg2  
requests  
beautifulsoup4  

A instalação pode ser realizada com:

```bash
pip install pandas psycopg2-binary requests beautifulsoup4
```


## 5. Criar o Banco de Dados
A estrutura inicial do banco de dados é criada utilizando o arquivo:

```bash
0_criar_banco.sql
```

Esse arquivo contém a criação do banco `transparencia` e das tabelas das camadas Raw e Silver.


## 6. Executar o Processo de Extração
A extração e carga dos dados na camada Raw será realizada pelo script:

```bash
1_extrair.py
```
O processo realiza:

1. download dos arquivos;
2. validação do arquivo compactado;
3. leitura dos arquivos CSV;
4. carga dos dados nas tabelas Raw;
5. validação da quantidade de registros carregados.


## 7. Executar o Processo de Transformação
Após a conclusão da extração, o processo de transformação será executado pelo script:

```bash
2_transformar.py
```

Esse processo será responsável pelo tratamento dos dados da camada Raw e pela carga das tabelas Silver.

As regras detalhadas de transformação serão documentadas após a conclusão e validação desta etapa.


# 🔮 Melhorias Futuras
Entre as possíveis melhorias para a solução estão:
* automatização periódica da atualização dos dados;
* criação de novas análises e indicadores;
* implementação de novos controles de qualidade dos dados;
* ampliação das validações do pipeline;
* criação de dashboards interativos;
* utilização de ferramentas de orquestração de pipelines;
* implementação de monitoramento das etapas de processamento;
* criação de testes automatizados para validação do pipeline.


# 👨‍💻 Autor
**Felipe Busarello**  
**Curso:** Análise de Dados com Python  
**Turma:** 09 - 2026  
**Professores:** Cláudio Neves e Luana Pereira  
**Projeto:** Projeto Avaliativo - Módulo 1  