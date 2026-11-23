# Databricks notebook source
# MAGIC %md
# MAGIC # CoverWise AI - Property & Casualty Insurance Pipeline (Medallion Architecture)
# MAGIC 
# MAGIC This PySpark pipeline processes Property & Casualty (P&C) insurance policy data through the **Medallion Architecture**:
# MAGIC 1. **Bronze Layer**: Ingests raw CSV data into a raw Delta table with audit metadata.
# MAGIC 2. **Silver Layer**: Cleanses, standardizes data types, validates property boundary rules, and filters anomalies.
# MAGIC 3. **Gold Layer**: Feature engineering (Property Coverage-to-Premium Ratio, Casualty Liability Index, CSR Tiers) and analytical aggregations for recommendation models.

# COMMAND ----------
# MAGIC %md
# MAGIC ### 0. Configuration & Spark Session Setup

# COMMAND ----------
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, current_timestamp, lit, trim, round as spark_round, when,
    avg, min as spark_min, max as spark_max, count
)
from pyspark.sql.types import IntegerType, DoubleType, LongType

# Initialize Spark session
spark = SparkSession.builder \
    .appName("CoverWise_PC_Medallion_Pipeline") \
    .getOrCreate()

print(f"Spark version: {spark.version}")

CSV_PATH = "/FileStore/tables/insurance_policies.csv"
BRONZE_TABLE_PATH = "/FileStore/delta/bronze_pc_policies"
SILVER_TABLE_PATH = "/FileStore/delta/silver_pc_policies"
GOLD_FEATURES_PATH = "/FileStore/delta/gold_pc_features"
GOLD_SUMMARY_PATH = "/FileStore/delta/gold_pc_summary"

# COMMAND ----------
# MAGIC %md
# MAGIC ### 1. Bronze Layer: Raw Data Ingestion & Delta Storage

# COMMAND ----------
raw_df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "false") \
    .csv(CSV_PATH)

bronze_df = raw_df \
    .withColumn("ingestion_timestamp", current_timestamp()) \
    .withColumn("source_file", lit("insurance_policies.csv"))

print(f"Bronze Records Ingested: {bronze_df.count()}")
bronze_df.printSchema()
bronze_df.show(5, truncate=False)

try:
    bronze_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(BRONZE_TABLE_PATH)
    print("Bronze Delta table written successfully.")
except Exception as e:
    print(f"Delta write note: {e}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### 2. Silver Layer: Cleansing, Type Casting & Quality Checks

# COMMAND ----------
silver_df = bronze_df \
    .withColumn("policy_id", trim(col("policy_id"))) \
    .withColumn("policy_name", trim(col("policy_name"))) \
    .withColumn("policy_type", trim(col("policy_type"))) \
    .withColumn("company_name", trim(col("company_name"))) \
    .withColumn("min_property_age", col("min_property_age").cast(IntegerType())) \
    .withColumn("max_property_age", col("max_property_age").cast(IntegerType())) \
    .withColumn("min_property_value", col("min_property_value").cast(LongType())) \
    .withColumn("max_property_value", col("max_property_value").cast(LongType())) \
    .withColumn("coverage_amount", col("coverage_amount").cast(LongType())) \
    .withColumn("annual_premium", col("annual_premium").cast(DoubleType())) \
    .withColumn("claim_settlement_ratio", col("claim_settlement_ratio").cast(DoubleType())) \
    .withColumn("third_party_liability", col("third_party_liability").cast(LongType())) \
    .withColumn("deductible_amount", col("deductible_amount").cast(IntegerType()))

# Data quality boundary constraints
silver_cleaned_df = silver_df.filter(
    (col("annual_premium") > 0) &
    (col("coverage_amount") > 0) &
    (col("claim_settlement_ratio") >= 70.0) &
    (col("claim_settlement_ratio") <= 100.0)
)

print(f"Silver Records Validated: {silver_cleaned_df.count()}")
silver_cleaned_df.select("policy_id", "policy_name", "policy_type", "annual_premium", "coverage_amount", "third_party_liability").show(5)

try:
    silver_cleaned_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(SILVER_TABLE_PATH)
    print("Silver Delta table written successfully.")
except Exception as e:
    print(f"Silver write note: {e}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### 3. Gold Layer: Feature Engineering & Analytical Aggregations

# COMMAND ----------
gold_features_df = silver_cleaned_df \
    .withColumn("coverage_per_rupee", spark_round(col("coverage_amount") / col("annual_premium"), 2)) \
    .withColumn("liability_ratio", spark_round(col("third_party_liability") / col("coverage_amount"), 2)) \
    .withColumn("affordability_tier",
        when(col("annual_premium") < 5000, "Economy / Budget Friendly")
        .when(col("annual_premium") <= 12000, "Standard Protection")
        .otherwise("High-Value Commercial / Villa")) \
    .withColumn("csr_tier",
        when(col("claim_settlement_ratio") >= 97.0, "Outstanding Track Record (>=97%)")
        .otherwise("Standard Claim Settler (<97%)"))

print("Gold Features Table Preview:")
gold_features_df.select(
    "policy_name", "policy_type", "annual_premium", "coverage_per_rupee", "liability_ratio", "affordability_tier"
).show(10, truncate=False)

# Category Aggregation Summary
gold_summary_df = gold_features_df.groupBy("policy_type").agg(
    count("policy_id").alias("total_policies"),
    spark_round(avg("annual_premium"), 2).alias("avg_premium"),
    spark_round(avg("coverage_amount"), 2).alias("avg_coverage"),
    spark_round(avg("third_party_liability"), 2).alias("avg_liability"),
    spark_round(avg("claim_settlement_ratio"), 2).alias("avg_csr"),
    spark_min("annual_premium").alias("min_premium"),
    spark_max("annual_premium").alias("max_premium")
)

print("Gold Category Aggregation Summary:")
gold_summary_df.show(truncate=False)

try:
    gold_features_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(GOLD_FEATURES_PATH)
    gold_summary_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(GOLD_SUMMARY_PATH)
    print("Gold Delta tables written successfully.")
except Exception as e:
    print(f"Gold write note: {e}")
