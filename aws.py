import boto3
import json
import getpass
import re
from nlp_iam import NLP_IAM

class AWSAIManager(NLP_IAM):
    def create_iam_user(self, username, iam_permissions):
        iam = boto3.client('iam')

        try:
            response = iam.create_user(UserName=username)
            user_arn = response['User']['Arn']

            # Assuming a naming convention where the user's S3 bucket is "bucket-{username}"
            resource_arn = f"arn:aws:s3:::bucket-{username}/*"

            policy_document = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": iam_permissions,
                        "Resource": resource_arn
                    }
                ]
            }

            iam.put_user_policy(
                UserName=username,
                PolicyName=f"{username}-s3-policy",
                PolicyDocument=json.dumps(policy_document)
            )

            print(f"IAM user {username} created with ARN: {user_arn}")
            return user_arn

        except Exception as e:
            print(f"Error creating IAM user or attaching policy: {e}")
            return None

    def main(self):
        system_user = getpass.getuser()
        print("Welcome to the AWS AI!")

        while True:
            command = input(f"Hello {system_user}. How can I help you? \n").strip().lower()

            # Normalize the command to ensure "add new user" is treated as "create user"
            if "add" in command:
                command = command.replace("add", "create")

            response = NLP_IAM.extract_info(nlp=NLP_IAM.nlp, prompt=command)
            action, username, permission = response["action"], response["username"], response["permissions"]

            print(f"Action: {action}, Username: {username}, Permissions: {permission}")

            permissions = permission[0] if permission else 'none'

            iam_permissions = {
                "s3": {
                    'read': ['s3:GetObject'],
                    'write': ['s3:PutObject'],
                    'none': []
                }
            }["s3"].get(permissions, [])

            if username and action and iam_permissions is not None:
                if action == "create":
                    self.create_iam_user(username, iam_permissions)
                else:
                    print("Unsupported action. Currently, only 'create' action is supported.")
            else:
                print("Invalid input or permissions provided.")

if __name__ == "__main__":
    iam = AWSAIManager()
    iam.main()
