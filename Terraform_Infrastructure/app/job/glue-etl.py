import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Script gerado para leitura do S3
AmazonS3_node = glueContext.create_dynamic_frame.from_options(
    format_options={"quoteChar": "\"", "withHeader": True, "separator": ",", "optimizePerformance": False},
    connection_type="s3",
    format="csv",
    connection_options={"paths": ["s3://tbat-raw-386283720018"], "recurse": True},
    transformation_ctx="AmazonS3_node"
)

# Mudança de esquema usando ApplyMapping
ChangeSchema_node = ApplyMapping.apply(
    frame=AmazonS3_node,
    mappings=[
        ("Suburb", "string", "Suburb", "string"),
        ("Rooms", "string", "Rooms", "string"),
        ("Price", "string", "Price", "string"),
        ("Date", "string", "Date", "string"),
        ("Bathroom", "string", "Bathroom", "string"),
        ("Car", "string", "Car", "string"),
        ("Landsize", "string", "Landsize", "string"),
        ("Lattitude", "string", "Lattitude", "string"),
        ("Longtitude", "string", "Longtitude", "string"),
        ("Regionname", "string", "Regionname", "string")
    ],
    transformation_ctx="ChangeSchema_node"
)

# Conversão para DataFrame para aplicar o fillna em 'Car'
sales_df = ChangeSchema_node.toDF()
sales_df = sales_df.fillna(0, subset=['Car'])  # Preenche valores nulos na coluna 'Car' com 0

# Converte de volta para DynamicFrame para salvar no Glue Catalog
sales_dynamic_frame = DynamicFrame.fromDF(sales_df, glueContext, "sales_dynamic_frame")

# Configura o sink para salvar no S3 e no Glue Catalog
AmazonS3_sink = glueContext.getSink(
    path="s3://tbat-processed-386283720018",
    connection_type="s3",
    updateBehavior="LOG",
    partitionKeys=[],
    enableUpdateCatalog=True,
    transformation_ctx="AmazonS3_sink"
)
AmazonS3_sink.setCatalogInfo(catalogDatabase="real_state_sales_db", catalogTableName="real_state_sales_table")
AmazonS3_sink.setFormat("glueparquet", compression="gzip")
AmazonS3_sink.writeFrame(sales_dynamic_frame)

job.commit()
