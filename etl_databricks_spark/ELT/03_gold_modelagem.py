# Databricks notebook source
# MAGIC %md
# MAGIC # 🟡 Camada Gold – Modelagem Dimensional e Enriquecimento
# MAGIC
# MAGIC Nesta terceira e última etapa do pipeline ETL, os dados limpos da camada Silver são transformados em uma estrutura dimensional, com tabelas fato e dimensão, otimizadas para análises e consumo por ferramentas de BI.
# MAGIC
# MAGIC ## Objetivo
# MAGIC Transformar os dados transacionais tratados em um modelo dimensional, incluindo enriquecimento geográfico, padronização com IDs, e separação entre tabelas fato e dimensões.
# MAGIC
# MAGIC ## Operações Realizadas
# MAGIC 1. Leitura dos dados da tabela `silver.stg_transaction`
# MAGIC 2. Criação de dimensões com IDs únicos:
# MAGIC    - `dim_payment_method` com métodos de pagamento
# MAGIC    - `dim_device_used` com tipos de dispositivos
# MAGIC    - `dim_transaction_type` com tipos de transações
# MAGIC    - `dim_location` com latitude e longitude usando a API do *geopy*
# MAGIC 3. Criação de tabela fato:
# MAGIC    - `fato_transaction`, contendo os campos principais relacionados à transação
# MAGIC 4. Separação dos dados de fraude em uma tabela fato específica (`fato_fraudulent`)
# MAGIC 5. Escrita de todas as tabelas no formato Delta em diretórios distintos no `/mnt/gold/`
# MAGIC 6. Registro das tabelas no catálogo Databricks no schema `GOLD`
# MAGIC
# MAGIC ## Estrutura Criada
# MAGIC - Fatos:
# MAGIC   - `GOLD.FATO_TRANSACTION`
# MAGIC   - `GOLD.FATO_FRAUDULENT`
# MAGIC - Dimensões:
# MAGIC   - `GOLD.DIM_DEVICE_USED`
# MAGIC   - `GOLD.DIM_PAYMENT_METHOD`
# MAGIC   - `GOLD.DIM_TRANSACTION_TYPE`
# MAGIC   - `GOLD.DIM_LOCATION`
# MAGIC
# MAGIC ---
# MAGIC

# COMMAND ----------

# DBTITLE 1,PIP
pip install geopy

# COMMAND ----------

# DBTITLE 1,Import
# Importações Externas
import pandas as pd

from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StringType

from geopy.geocoders import Nominatim
import time

# COMMAND ----------

# DBTITLE 1,Get_CSV
# Iniciar uma Sessão Spark e ler dados da SILVER
spark = SparkSession.builder.appName("ETL_RAW").getOrCreate()
df = spark.read.table("SILVER.STG_TRANSACTION")
df.limit(5).display()

# COMMAND ----------

# DBTITLE 1,df_device_used
# Criar DF_Device_Used com seu ID
df_device_used = df.select("DEVICE_USED").distinct()
df_device_used = df_device_used.withColumn("ID_DEVICE_USED",F.row_number().over(Window.orderBy("DEVICE_USED")))
df_device_used = df_device_used.select("ID_DEVICE_USED","DEVICE_USED")
df_device_used.limit(5).display()


# COMMAND ----------

# DBTITLE 1,df_payment_method
# Criar DF_PAYMENT_METHOD com seu ID
df_payment_method = df.select("PAYMENT_METHOD").distinct()
df_payment_method = df_payment_method.withColumn("ID_PAYMENT_METHOD",F.row_number().over(Window.orderBy("PAYMENT_METHOD")))
df_payment_method = df_payment_method.select("ID_PAYMENT_METHOD","PAYMENT_METHOD")
df_payment_method.limit(5).display()

# COMMAND ----------

# DBTITLE 1,df_fraudulent
# Criar DF_FRAUDULENT
df_fraudulent = df.select("ID_TRANSACTION","FRAUDULENT", "PREVIOUS_FRAUDULENT_TRANSACTIONS")
df_fraudulent.limit(5).display()

# COMMAND ----------

# DBTITLE 1,df_transaction_type
# Criar DF_TRANSACTION_TYPE com seu ID
df_transaction_type = df.select("TRANSACTION_TYPE").distinct()
df_transaction_type = df_transaction_type.withColumn("ID_TRANSACTION_TYPE",F.row_number().over(Window.orderBy("TRANSACTION_TYPE")))
df_transaction_type = df_transaction_type.select("ID_TRANSACTION_TYPE","TRANSACTION_TYPE")
df_transaction_type.limit(5).display()

# COMMAND ----------

# DBTITLE 1,df_location
# Coletar nomes distintos das cidades
cities = sorted([row["LOCATION"] for row in df.select("LOCATION").distinct().collect()])

# Iniciar Objeto Geo da Lib geopy
geolocator = Nominatim(user_agent="my_geocoder")
location_dict = {}

# Percorrer Cada Cidade coletando Latitude e Longitude 
for city in cities:
    try:
        location = geolocator.geocode(city)
        if location:
            location_dict[city] = (location.latitude, location.longitude)
        else:
            location_dict[city] = (None, None)
        time.sleep(1)  # Dar Tempo p/ API, evita rate limit
    except:
        location_dict[city] = (None, None)

# Criar DF_LOCATION
data = [(i, city, lat, lon) for i, (city, (lat, lon)) in enumerate(location_dict.items(),1)]
df_location = spark.createDataFrame(data, ["ID_LOCATION", "LOCATION", "LATITUDE", "LONGITUDE"])
df_location.display() 

# COMMAND ----------

# DBTITLE 1,df_transaction
# Criar Tabela principal df_transaction utilizando ID's 
df_transaction = None
df_transaction = (
    df
    .join(df_device_used, on="DEVICE_USED", how="left")
    .join(df_payment_method, on="PAYMENT_METHOD", how="left")
    .join(df_transaction_type, on="TRANSACTION_TYPE", how="left")
    .join(df_location, on="LOCATION", how="left")
    .drop("DEVICE_USED", "PAYMENT_METHOD", "TRANSACTION_TYPE", "LOCATION", "FRAUDULENT", "PREVIOUS_FRAUDULENT_TRANSACTIONS", "LATITUDE", "LONGITUDE")
    .select(
        "ID_TRANSACTION", "TRANSACTION_AMOUNT", "TIME_OF_TRANSACTION", 
        "ID_USER", "ACCOUNT_AGE", "ID_LOCATION",
        "ID_DEVICE_USED", "ID_PAYMENT_METHOD", "ID_TRANSACTION_TYPE",
        "NUMBER_OF_TRANSACTIONS_LAST_24H",     
    )
)

df_transaction.limit(5).display()

# COMMAND ----------

# DBTITLE 1,Database Create
# MAGIC %sql
# MAGIC -- Criar Databese
# MAGIC CREATE DATABASE IF NOT EXISTS OURO;

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS OURO.TRANSACTION;
# MAGIC DROP TABLE IF EXISTS OURO.DEVICE_USED;
# MAGIC DROP TABLE IF EXISTS OURO.PAYMENT_METHOD;
# MAGIC DROP TABLE IF EXISTS OURO.TRANSACTION_TYPE;
# MAGIC DROP TABLE IF EXISTS OURO.FRAUDULENT;
# MAGIC DROP TABLE IF EXISTS OURO.LOCATION

# COMMAND ----------

# DBTITLE 1,Create Tables
# Diretórios de destinos
paths = {
    "FATO_TRANSACTION":      "/mnt/gold/fato_transaction",
    "DIM_DEVICE_USED":      "/mnt/gold/dim_device_used",
    "DIM_PAYMENT_METHOD":   "/mnt/gold/dim_payment_method",
    "DIM_TRANSACTION_TYPE": "/mnt/gold/dim_transaction_type",
    "FATO_FRAUDULENT":       "/mnt/gold/fato_fraudulent",
    "DIM_LOCATION":         "/mnt/gold/dim_location"
}

# Escrita dos dados no formato Delta
df_transaction.write.format("delta").mode("overwrite").save(paths["FATO_TRANSACTION"])
df_device_used.write.format("delta").mode("overwrite").save(paths["DIM_DEVICE_USED"])
df_payment_method.write.format("delta").mode("overwrite").save(paths["DIM_PAYMENT_METHOD"])
df_transaction_type.write.format("delta").mode("overwrite").save(paths["DIM_TRANSACTION_TYPE"])
df_fraudulent.write.format("delta").mode("overwrite").save(paths["FATO_FRAUDULENT"])
df_location.write.format("delta").mode("overwrite").save(paths["DIM_LOCATION"])

# Registro no metastore do Databricks
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS GOLD.FATO_TRANSACTION
    USING DELTA
    LOCATION '{paths["FATO_TRANSACTION"]}'
""")

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS GOLD.DIM_DEVICE_USED
    USING DELTA
    LOCATION '{paths["DIM_DEVICE_USED"]}'
""")

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS GOLD.DIM_PAYMENT_METHOD
    USING DELTA
    LOCATION '{paths["DIM_PAYMENT_METHOD"]}'
""")

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS GOLD.DIM_TRANSACTION_TYPE
    USING DELTA
    LOCATION '{paths["DIM_TRANSACTION_TYPE"]}'
""")

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS GOLD.FATO_FRAUDULENT
    USING DELTA
    LOCATION '{paths["FATO_FRAUDULENT"]}'
""")

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS GOLD.DIM_LOCATION
    USING DELTA
    LOCATION '{paths["DIM_LOCATION"]}'
""")


# COMMAND ----------


spark.sql("DROP DATABASE IF EXISTS `OURO` CASCADE")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🟡 Gold
# MAGIC - Modelagem dimensional com criação de tabelas fato e dimensão
# MAGIC - Geração de IDs únicos para métodos de pagamento, dispositivos, tipos de transação e localização
# MAGIC - Enriquecimento com latitude e longitude via API `geopy`
# MAGIC - Criação das tabelas `GOLD.FATO_TRANSACTION`, `GOLD.FATO_FRAUDULENT`, `GOLD.DIM_*`
# MAGIC - Armazenamento em Delta Lake no diretório `/mnt/gold/`
# MAGIC