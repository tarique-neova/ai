resource "aws_iam_user" "example" {
  name = "test-ai"
}

resource "aws_iam_user_delete" "example" {
  user_name = aws_iam_user.example.name
}