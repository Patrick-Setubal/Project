-- Databricks notebook source
-- MAGIC
-- MAGIC %md
-- MAGIC # ⚪ Camada Silver – Limpeza e Padronização
-- MAGIC
-- MAGIC Nesta segunda etapa do pipeline ETL, os dados brutos da camada Bronze passam por um processo de limpeza, deduplicação e padronização, sendo armazenados em uma estrutura mais tratada e confiável.
-- MAGIC
-- MAGIC ## Objetivo
-- MAGIC O objetivo da camada Silver é transformar os dados crus da Bronze em um formato mais limpo e estruturado, corrigindo inconsistências e preparando-os para análises ou enriquecimentos futuros.
-- MAGIC
-- MAGIC ## Operações Realizadas
-- MAGIC 1. Criação do schema `SILVER`, se ainda não existir.
-- MAGIC 2. Seleção dos dados da tabela `bronze.raw_bronze`.
-- MAGIC 3. Aplicação de transformações e regras de limpeza:
-- MAGIC    - Remoção de duplicidades com `SELECT DISTINCT`
-- MAGIC    - Padronização textual com `TRIM` e `UPPER`
-- MAGIC    - Substituição de valores nulos ou inconsistentes por `'UNKNOWN'` com `NVL`
-- MAGIC    - Renomeação de colunas para uma nomenclatura mais padronizada
-- MAGIC 4. Criação e salvamento da tabela `silver.stg_transaction` no formato Delta
-- MAGIC 5. Visualização amostral dos dados resultantes
-- MAGIC
-- MAGIC ## Local de Armazenamento
-- MAGIC - Delta Lake: `/mnt/silver/stg_transaction`
-- MAGIC - Catálogo: `silver.stg_transaction`
-- MAGIC
-- MAGIC ---
-- MAGIC

-- COMMAND ----------

-- Criar SCHEMA 
CREATE SCHEMA IF NOT EXISTS SILVER;

-- COMMAND ----------

-- Criar Tabela realizando limpeza dos dados
CREATE OR REPLACE TABLE SILVER.STG_TRANSACTION
USING DELTA
LOCATION '/mnt/silver/stg_transaction'
AS
SELECT DISTINCT 
  TRANSACTION_ID AS ID_TRANSACTION,
  USER_ID AS ID_USER,
  TRANSACTION_AMOUNT,
  NVL(TRIM(UPPER(TRANSACTION_TYPE)),'UNKNOWN') AS TRANSACTION_TYPE,
  TIME_OF_TRANSACTION,
  CASE 
    WHEN TRIM(UPPER(DEVICE_USED)) = 'UNKNOWN DEVICE' THEN 'UNKNOWN'
    ELSE NVL(TRIM(UPPER(DEVICE_USED)), 'UNKNOWN')
  END AS DEVICE_USED,
  NVL(TRIM(UPPER(`LOCATION`)),'UNKNOWN') AS `LOCATION`,
  PREVIOUS_FRAUDULENT_TRANSACTIONS,
  ACCOUNT_AGE,
  NUMBER_OF_TRANSACTIONS_LAST_24H,
  NVL(TRIM(UPPER(PAYMENT_METHOD)),'UNKNOWN') AS PAYMENT_METHOD,
  FRAUDULENT
FROM BRONZE.RAW_BRONZE

;
-- Visualizar Resultado
SELECT * FROM SILVER.STG_TRANSACTION LIMIT 5

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## ⚪ Silver
-- MAGIC - Aplicação de limpeza e padronização dos dados vindos da camada Bronze
-- MAGIC - Remoção de duplicidades e padronização de texto (`TRIM`, `UPPER`, `NVL`)
-- MAGIC - Criação da tabela `silver.stg_transaction` com os dados tratados
-- MAGIC - Salvamento como Delta Lake em `/mnt/silver/stg_transaction`
-- MAGIC