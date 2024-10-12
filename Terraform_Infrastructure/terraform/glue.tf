# Cria um Database no AWS Glue Catalog
resource "aws_glue_catalog_database" "glue_database" {
  name = "real_state_sales_db"  # Nome do seu database no Glue
}

# Faz o upload do arquivo glue-etl.py para o bucket S3
resource "aws_s3_object" "glue_script" {
  bucket = local.glue_bucket
  key    = "job/glue-etl.py"  # Caminho onde o arquivo será salvo no bucket
  source = "${path.module}/../app/job/glue-etl.py"  # Caminho local para o arquivo glue-etl.py
  acl    = "private"
  
  depends_on = [aws_s3_bucket.buckets]
}

resource "aws_glue_job" "glue_job" {
  name              = "glue_script"
  role_arn          = "arn:aws:iam::386283720018:role/tcc-glue-job-role"
  glue_version      = "3.0"
  worker_type       = "Standard"
  number_of_workers = 2
  timeout           = 5

  # Configuração do comando que será executado pelo Glue Job
  command {
    script_location = "s3://${local.glue_bucket}/job/glue-etl.py"
    python_version  = "3"
  }
  # Adiciona a referência ao Database que criamos
  default_arguments = {
    "--database-name" = aws_glue_catalog_database.glue_database.name
  }
  
  depends_on = [aws_s3_object.glue_script]

}

resource "aws_glue_crawler" "my_crawler" {
  name         = "real-state-sales-crawler"
  role         = "arn:aws:iam::386283720018:role/tcc-glue-job-role"  # Substitua pela role com permissões adequadas
  database_name = aws_glue_catalog_database.glue_database.name
  description   = "Crawler para catalogar dados de vendas de imóveis"
  
  s3_target {
    path = "s3://tbat-processed-386283720018/"  # Caminho S3 a ser catalogado
  }
  
  #Comando para agendar execuções do Crawler
  #schedule = "cron(0 12 * * ? *)"  # Executa diariamente ao meio-dia (UTC)
  
  depends_on = [aws_glue_catalog_database.glue_database]
}