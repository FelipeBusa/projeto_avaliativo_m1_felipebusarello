# 📊 Projeto Avaliativo - Análise de Dados com Python | Módulo 1
**Felipe Busarello**  
**Curso:** Análise de Dados com Python  
**Turma:** 09 - 2026  
**Professor:** Cláudio Neves  


## 📌 Sobre o Projeto
Este projeto foi desenvolvido como parte do Projeto Avaliativo do Módulo 1 do curso de **Análise de Dados com Python**.  

O objetivo é desenvolver um pipeline de dados utilizando Python, PostgreSQL e técnicas de ETL (Extract, Transform, Load), desde a extração dos dados até o tratamento, organização e análise das informações.  

O projeto utiliza dados de viagens, passagens, trechos e pagamentos referentes ao ano de 2025, disponibilizados em arquivos CSV.  

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


## 1. Extração e camada Raw
Nesta etapa, os arquivos CSV serão obtidos e carregados no banco de dados PostgreSQL.  
A camada Raw terá como objetivo preservar os dados recebidos na origem, sem realizar transformações de conteúdo.  
As tabelas Raw foram estruturadas utilizando colunas `VARCHAR`, permitindo receber os dados exatamente como disponibilizados nos arquivos de origem.  


## 2. Transformação e camada Silver
Nesta etapa, os dados armazenados na camada Raw serão tratados e transformados.  
Entre os tratamentos previstos estão:
* conversão de tipos de dados;
* conversão de datas;
* conversão de valores numéricos;
* criação de campos calculados;
* aplicação de regras de integridade;
* relacionamento entre as tabelas.

A camada Silver será composta por tabelas estruturadas e tipadas, com chaves primárias, chaves estrangeiras e constraints para garantir maior consistência dos dados.


## 3. Análise e camada Gold
A camada Gold será utilizada para preparar os dados para análise.  
Nesta etapa serão desenvolvidas consultas SQL, indicadores, tabelas agregadas e visualizações com o objetivo de responder perguntas de negócio relacionadas à base de dados.


# 📈 Análise Exploratória
Esta seção será preenchida após a conclusão das etapas de tratamento e preparação dos dados.  
Serão realizadas análises exploratórias para identificar padrões, distribuições, comportamentos e possíveis inconsistências presentes na base.


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


### Banco de dados
* PostgreSQL


### Bibliotecas e ferramentas
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
├── README.md
└── .gitignore
```

> **Observação:** arquivos contendo credenciais, dados locais e arquivos gerados automaticamente pelo Python não são versionados no GitHub.


# 🚀 Como Executar
## 1. Clonar o repositório
```bash
git clone https://github.com/FelipeBusa/projeto_avaliativo_m1_felipebusarello.git
```

## 2. Acessar a pasta do projeto
```bash
cd projeto_avaliativo_m1_felipebusarello
```

## 3. Configurar o ambiente
É necessário possuir Python e PostgreSQL instalados.  
As credenciais de acesso ao banco de dados devem ser configuradas localmente, utilizando o arquivo `.env`.  
O arquivo `.env.example` apresenta a estrutura das variáveis necessárias sem expor informações sensíveis.  

## 4. Instalar as dependências
As bibliotecas utilizadas pelo projeto serão documentadas conforme o desenvolvimento das etapas.

## 5. Criar o banco de dados
A estrutura inicial do banco de dados é criada utilizando o arquivo:
```text
0_criar_banco.sql
```
Esse arquivo contém a criação do banco `transparencia` e das tabelas das camadas Raw e Silver.

## 6. Executar o processo de extração
A extração e carga dos dados na camada Raw será realizada pelo script:
```text
1_extrair.py
```
As demais etapas de transformação e análise serão documentadas nesta seção conforme o desenvolvimento do projeto.


# 🔮 Melhorias Futuras
Entre as possíveis melhorias para a solução estão:
* automatização periódica da atualização dos dados;
* criação de novas análises e indicadores;
* implementação de novos controles de qualidade dos dados;
* ampliação das validações do pipeline;
* criação de dashboards interativos;
* utilização de ferramentas de orquestração de pipelines;
* implementação de monitoramento das etapas de processamento.


# 👨‍💻 Autor
**Felipe Busarello**  
**Curso:** Análise de Dados com Python  
**Turma:** 09 - 2026  
**Professor:** Cláudio Neves  
**Projeto:** Projeto Avaliativo - Módulo 1  