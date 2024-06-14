terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.65.0"  # Specify the desired version here
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = "ap-south-1"
}
