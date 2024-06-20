
resource "aws_s3_bucket" "example" {
  bucket = "ai-test-new"
  acl    = "private"

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  LifecycleConfigurationBlock {
    rules = [
      {
        id     = "rule1"
        prefix = ""
        status = "Enabled"

        transition {
          days          = 30
          storage_class = "INTELLIGENT_TIERING"
        }

        expiration {
          days         = 60
          date         = ""
        }
      }
    ]
  }

  tags = {
    Created_by = "Terraform"
  }
}
