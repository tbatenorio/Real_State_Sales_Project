resource "aws_iam_policy" "glue_job" {
  name        = "${local.prefix}-glue-job-policy"
  path        = "/"
  description = "Provides write permissions to CloudWatch Logs and S3 Full Access"
  policy      = file("./permissions/Policy_GlueJobs.json")
}
