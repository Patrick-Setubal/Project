# Databricks notebook source
# MAGIC %md
# MAGIC # 🟤 Camada Bronze – Ingestão de Dados
# MAGIC
# MAGIC Nesta primeira etapa do pipeline ETL, realizamos a ingestão bruta dos dados.
# MAGIC
# MAGIC ## Objetivo
# MAGIC O objetivo da camada Bronze é coletar os dados crus, sem transformações, e armazená-los no formato Delta Lake. Isso garante rastreabilidade, performance de leitura e versionamento dos dados brutos.
# MAGIC
# MAGIC ## Fonte de Dados
# MAGIC - **Origem**: Arquivo CSV (`raw_fraud_detection_dataset.csv`)
# MAGIC - **Formato**: CSV com cabeçalho, tipos de dados inferidos automaticamente
# MAGIC
# MAGIC ## Etapas Realizadas
# MAGIC 1. Iniciar a sessão Spark.
# MAGIC 2. Ler o arquivo CSV e carregar em um DataFrame (`df_bronze`).
# MAGIC 3. Criar o schema `BRONZE` no metastore, se não existir.
# MAGIC 4. Salvar os dados no formato Delta na camada Bronze.
# MAGIC 5. Registrar a tabela no catálogo do Databricks.
# MAGIC
# MAGIC ---
# MAGIC

# COMMAND ----------

# Importações Externas
import pandas as pd
from pyspark.sql import SparkSession

# COMMAND ----------

# Iniciar uma Sessão Spark
spark = SparkSession.builder.appName("ETL_BRONZE").getOrCreate()
# Ler CSV e criar df_bronze
df_bronze = spark.read.option("header", True)\
    .option("inferSchema", True)\
    .csv("dbfs:/FileStore/raw_fraud_detection_dataset.csv")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Criar SCHEMA 
# MAGIC CREATE SCHEMA IF NOT EXISTS BRONZE; 

# COMMAND ----------

# Salvar os dados
df_bronze.write.format("delta").mode("overwrite").save("/mnt/bronze/raw_bronze")
# Registrar no Catálogo
spark.sql("""
  CREATE TABLE bronze.raw_bronze
  USING DELTA
  LOCATION '/mnt/bronze/raw_bronze'
""")

# COMMAND ----------

# MAGIC %sql 
# MAGIC -- Check Dados
# MAGIC select * from bronze.raw_bronze limit 5

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🟤 Bronze
# MAGIC - Ingestão de dados brutos do CSV
# MAGIC - Salvamento como Delta Lake em `/mnt/bronze/raw_bronze`
# MAGIC - Registro da tabela no catálogo com o nome `bronze.raw_bronze`
# MAGIC