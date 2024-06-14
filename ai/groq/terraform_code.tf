
resource "aws_iam_user" "example" {
  name = "testai${formatdate("yy", timestamp())}"
}
