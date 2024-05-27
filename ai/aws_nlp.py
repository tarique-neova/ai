import boto3
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import json
import getpass
import spacy


class AWSAIManager:
    def __init__(self, model_name="./fine_tuned_gpt2"):
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.nlp = spacy.load("en_core_web_sm")

    def generate_response(self, prompt):
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, padding='max_length',
                                          truncation=True)
        attention_mask = input_ids.ne(self.tokenizer.pad_token_id)
        output = self.model.generate(input_ids, attention_mask=attention_mask, max_new_tokens=100,
                                     num_return_sequences=1, temperature=0.7)
        decoded_output = self.tokenizer.decode(output[0], skip_special_tokens=True)
        decoded_output = decoded_output.replace("//", "").replace("/", "")
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

    def map_permissions(self, permission_desc):
        # Map natural language descriptions to S3 permissions
        if 'least privileged' in permission_desc:
            return ['s3:ListBucket', 's3:GetObject']  # Example of least privileged permissions for S3
        elif 'read' in permission_desc:
            return ['s3:GetObject']
        elif 'write' in permission_desc:
            return ['s3:PutObject']
        elif 'none' in permission_desc:
            return []
        else:
            return []

    def parse_command(self, command):
        doc = self.nlp(command)

        # Extract entities and determine the action, username, and permissions
        action = None
        username = None
        permissions_desc = None

        for token in doc:
            if token.lemma_ in ["create", "update"] and token.dep_ == "ROOT":
                action = "create_user" if token.lemma_ == "create" else "update_permissions"
            elif token.lemma_ == "user" or token.lemma_ == "username":
                username_index = token.i + 1
                if username_index < len(doc):
                    username = doc[username_index].text
            elif token.dep_ == "pobj" and token.head.lemma_ == "with":
                permissions_desc = token.text

        # Handle permissions extraction from noun chunks if not directly found
        if not permissions_desc:
            for chunk in doc.noun_chunks:
                if 'permissions' in chunk.text or 'permission' in chunk.text:
                    permissions_desc = chunk.text

        # Additional logic to handle different permissions descriptions
        permissions_keywords = ["s3 read", "s3 write", "read s3", "write s3", "least privileged"]
        for keyword in permissions_keywords:
            if keyword in command:
                permissions_desc = keyword
                break

        # Map permissions description to actual permissions
        permissions = self.map_permissions(permissions_desc) if permissions_desc else None

        # Debugging print statements
        print("The parsing is printed for testing purpose only")
        print("-------------------------------------------------------------------------------------------------")
        print(f"Parsed action: {action}")
        print(f"Parsed username: {username}")
        print(f"Parsed permissions: {permissions}")
        print("-------------------------------------------------------------------------------------------------")

        return action, username, permissions

    def main(self):
        system_user = getpass.getuser()
        print("-------------------------------------------------------------------------------------------------")
        print("Welcome to the AWS AI!")

        while True:
            command = input(f"Hello {system_user}. How can I help you? \n").strip().lower()
            if "add" in command:
                command = command.replace("add", "create")

            print("Sure, will try my best to help you out with your ask \n")

            action, username, permissions = self.parse_command(command)
            if action == 'create_user':
                if username and permissions:
                    user_arn = self.create_iam_user(username, permissions)
                    print(f"User {username} created with S3 permissions: {permissions}")
                    print(f"User ARN: {user_arn}")

                    prompt = (f"I have created a new IAM user named {username} with specified S3 permissions. The "
                              f"user ARN is {user_arn}.")
                    bot_response = self.generate_response(prompt)
                    print("Response: " + bot_response)
                    print(
                        "-------------------------------------------------------------------------------------------------")
                else:
                    print("Invalid command. Please provide a valid username and permissions.")

            elif action == 'update_permissions':
                if username and permissions:
                    response = self.update_user_permissions(username, permissions)
                    print(response)

                    prompt = f"Updated permissions for user {username}. New permissions: {', '.join(permissions)}"
                    bot_response = self.generate_response(prompt)
                    print("Response: " + bot_response)
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
