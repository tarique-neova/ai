
resource "aws_iam_user" "test" {
  name = "test${replace(local.username, ".", "")}345"
}
