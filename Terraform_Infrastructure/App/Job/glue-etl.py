from pyspark.sql import SparkSession
import pyspark.sql.functions as F


def create_spark_session():
    spark = SparkSession.builder.getOrCreate()
    return spark


def process_sales_data(spark, input_data, output_data):
    # get filepath to sales data file
    monthly_sales = input_data + "monthly-data/*/"

    # read sales data file
    df = spark.read.csv(monthly_sales, header=True, inferSchema=True)

    # extract columns to create sales table
    sales = df.select(
        ['Date', 'Suburb', 'Rooms', 'Type', 'Price', 'Bathroom', 'Car', 'Landsize', 'BuildingArea', 'Regionname'])

    sales = sales['Landsize'].dropna()
    sales = sales.dropna(subset=['Car'])

    sales = sales.withColumn("Type", F.when(F.col("Type") == "br", "b").when(F.col(
        "Type") == "dev site", "d").when(F.col("Type") == "o res", "r").otherwise(F.col("Type")))
    # Convert Date column to a proper Date format and extract Year and Month
    sales = sales.withColumn("Date", F.to_date(F.col("Date"), "d/M/yyyy"))
    sales = sales.withColumn("Year", F.year(F.col("Date")))
    sales = sales.withColumn("Month", F.month(F.col("Date")))

    # Write the sales table to parquet files partitioned by Year and Month
    sales.write.partitionBy("Year", "Month").mode(
        "overwrite").parquet(output_data)


def main():
    spark = create_spark_session()
    input_data = "s3://tbat-raw-386283720018/"
    output_data = "s3://tbat-processed-386283720018/"

    process_sales_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
