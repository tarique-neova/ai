import boto3
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import json
import getpass
import re


class AWSAIManager:
    def __init__(self, model_name="./fine_tuned_gpt2"):
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
        self.model = GPT2LMHeadModel.from_pretrained(model_name)

    def generate_response(self, prompt):
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, padding='max_length',
                                          truncation=True)
        attention_mask = input_ids.ne(self.tokenizer.pad_token_id)
        output = self.model.generate(input_ids, attention_mask=attention_mask, max_new_tokens=100,
                                     num_return_sequences=1, temperature=0.7)
        decoded_output = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return decoded_output

    def create_iam_user(self, username, s3_permissions):
        iam = boto3.client('iam')

        response = iam.create_user(UserName=username)
        user_arn = response['User']['Arn']

        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": s3_permissions,
                    "Resource": "arn:aws:s3:::*"
                }
            ]
        }

        iam.put_user_policy(
            UserName=username,
            PolicyName=f"{username}-s3-policy",
            PolicyDocument=json.dumps(policy_document)
        )

        return user_arn

    def update_user_permissions(self, username, new_permissions):
        iam = boto3.client('iam')

        try:
            existing_policy_response = iam.get_user_policy(UserName=username, PolicyName=f"{username}-s3-policy")
            existing_policy_document = existing_policy_response['PolicyDocument']

            # Update the permissions in the existing policy document
            existing_policy_document['Statement'][0]['Action'] = new_permissions

            # Update the policy with the new permissions
            iam.put_user_policy(
                UserName=username,
                PolicyName=f"{username}-s3-policy",
                PolicyDocument=json.dumps(existing_policy_document)
            )

            return f"Permissions updated for user {username}. New permissions: {', '.join(new_permissions)}"
        except Exception as e:
            return f"An error occurred: {e}"

    def parse_command(self, command):
        # Extract username and permissions from the command
        username_match = re.search(r'username\s+"([^"]+)"', command)
        username = username_match.group(1) if username_match else None

        permissions_match = re.search(r'with\s+s3\s+(read|write|none)\s+permissions', command)
        permissions = permissions_match.group(1) if permissions_match else None

        # Extract action
        action = None
        if 'create user' in command or 'create new user' in command:
            action = 'create_user'
        elif 'update' in command and 'permissions' in command:
            action = 'update_permissions'

        # Debugging print statements
        print(f"Parsed action: {action}")
        print(f"Parsed username: {username}")
        print(f"Parsed permissions: {permissions}")

        return action, username, permissions

    def main(self):
        system_user = getpass.getuser()
        print("Welcome to the AWS AI!")

        while True:
            command = input(f"Hello {system_user}. How can I help you? ").strip().lower()

            action, username, permissions = self.parse_command(command)

            if action == 'create_user':
                if username and permissions:
                    s3_permissions = {
                        'read': ['s3:GetObject'],
                        'write': ['s3:PutObject'],
                        'none': []
                    }.get(permissions, [])

                    user_arn = self.create_iam_user(username, s3_permissions)
                    print(f"User {username} created with S3 permissions: {permissions}")
                    print(f"User ARN: {user_arn}")

                    prompt = (
                        f"I have created a new IAM user named {username} with {permissions} permissions for S3. The "
                        f"user ARN is {user_arn}.")
                    bot_response = self.generate_response(prompt)
                    print("Response: " + bot_response)
                else:
                    print("Invalid command. Please provide a valid username and permissions.")

            elif action == 'update_permissions':
                if username and permissions:
                    new_permissions = {
                        'read': ['s3:GetObject'],
                        'write': ['s3:PutObject'],
                        'none': []
                    }.get(permissions, [])

                    if new_permissions:
                        response = self.update_user_permissions(username, new_permissions)
                        print(response)

                        prompt = f"Updated permissions for user {username}. New permissions: {', '.join(new_permissions)}"
                        bot_response = self.generate_response(prompt)
                        print("Response: " + bot_response)
                    else:
                        print("Invalid permissions specified.")
                else:
                    print("Invalid command. Please provide a valid username and permissions.")

            elif command == "exit":
                print("Exiting...")
                break

            else:
                bot_response = self.generate_response(command)
                print("Generated Code: \n" + bot_response)


if __name__ == "__main__":
    manager = AWSAIManager(model_name="./fine_tuned_gpt2")
    manager.main()
