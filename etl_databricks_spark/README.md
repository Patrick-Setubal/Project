# 🚀 Projeto Prático: ETL e Pipeline no Databricks com Delta Lake

![Visão Geral do Projeto](https://github.com/Patrick-Setubal/Project/blob/main/etl_databricks_spark/elt_databricks_spark.png?raw=true)

## 🎯 Objetivo

Este projeto tem como principal objetivo **praticar e demonstrar o uso prático da plataforma Databricks**, explorando a criação de pipelines de dados com armazenamento em Delta Lake, utilizando a arquitetura em camadas **Bronze, Silver e Gold**.

Mais do que dominar a linguagem PySpark ou SQL, a ênfase está em:

- Compreender a **estrutura e o funcionamento do Databricks**;
- Aplicar conceitos de **arquitetura de dados moderna** na prática;
- Criar pipelines com **Delta Lake** e controle de versionamento;
- Utilizar o **notebook do Databricks** para todo o ciclo ETL.

---

## 🧱 Etapas do Projeto

### 🔹 1. Camada Bronze – Ingestão

- Leitura de um arquivo CSV com dados de transações financeiras.
- Escrita dos dados brutos no Databricks como uma tabela Delta.

### ⚪ 2. Camada Silver – Transformação

- Limpeza e padronização de colunas.
- Remoção de nulos e duplicatas.
- Escrita como uma tabela intermediária Silver.

### 🟡 3. Camada Gold – Modelagem Analítica

- Criação de dimensões e fatos com chaves substitutas.
- Inclusão de coordenadas geográficas com a biblioteca `geopy`.
- Escrita final em formato Delta, pronta para consumo analítico.

---

## 🧪 Dataset Utilizado

Utilizou-se um dataset fictício de transações com fraudes para simular um pipeline real de dados, contendo atributos como valor, localização, tipo de transação e método de pagamento.

---

## 🧰 Tecnologias e Recursos

- **Databricks (Community Edition ou Enterprise)**
- **Delta Lake**
- **PySpark / Spark SQL**
- **Geopy** para geocodificação
- **Notebooks interativos**

---

## 👨‍💻 Autor

**[Patrick Setubal]**  
Entusiasta de dados, praticando soluções no Databricks.  
[LinkedIn]([https://www.linkedin.com/](https://www.linkedin.com/in/patrick-setubal-2b502b115/))

---

