output "data_bucket" {
  value = aws_s3_bucket.data.bucket
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.address
}

output "database_secret_arn" {
  value     = aws_secretsmanager_secret.database.arn
  sensitive = true
}
