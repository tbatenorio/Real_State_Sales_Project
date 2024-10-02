resource "aws_glue_catalog_database" "glue_database" {
  name = "real_state_sales_db"  # Nome do seu database no Glue
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

}