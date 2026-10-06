# AWS deployment

This Terraform baseline creates:

- encrypted/versioned private S3 bucket
- VPC and two database subnets
- private PostgreSQL RDS instance
- Secrets Manager database credentials
- CloudWatch log group

It deliberately creates **no public database ingress**.

Deployment is intentionally not automatic because AWS resources can create
charges.

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

Destroy when no longer needed:

```bash
terraform destroy
```
