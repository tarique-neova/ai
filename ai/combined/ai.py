import subprocess
import json
import pandas as pd
import re
from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
import os
import getpass
import spacy

# Initialize the Hugging Face model for text classification
nlu_model = pipeline("zero-shot-classification")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")


class DockerManager:
    @staticmethod
    def docker_login(username, password):
        try:
            subprocess.run(["sudo", "docker", "login", "--username", username, "--password", password], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while logging in to Docker Hub: {e}")
            return False
        return True

    @staticmethod
    def scan_docker_image(image_name):
        try:
            subprocess.run(["sudo", "docker", "pull", image_name], check=True)
            result = subprocess.run(["sudo", "trivy", "image", "--format", "json", image_name], capture_output=True,
                                    text=True)
            vulnerabilities = json.loads(result.stdout)
            return vulnerabilities
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while pulling or scanning the Docker image: {e}")
            return None

    @staticmethod
    def parse_vulnerabilities(vulnerabilities):
        vulnerability_list = []
        for vuln in vulnerabilities.get('Results', []):
            for vulnerability in vuln.get('Vulnerabilities', []):
                vuln_info = {
                    "Target": vuln.get("Target"),
                    "VulnerabilityID": vulnerability.get("VulnerabilityID"),
                    "PkgName": vulnerability.get("PkgName"),
                    "InstalledVersion": vulnerability.get("InstalledVersion"),
                    "FixedVersion": vulnerability.get("FixedVersion"),
                    "Severity": vulnerability.get("Severity"),
                    "Description": vulnerability.get("Description")
                }
                vulnerability_list.append(vuln_info)
        return vulnerability_list

    @staticmethod
    def vulnerabilities_to_table(vulnerability_list):
        df = pd.DataFrame(vulnerability_list)
        return df

    @staticmethod
    def format_vulnerabilities_table_sql(df):
        if df.empty:
            return "No vulnerabilities found. Image is clean."
        col_widths = {col: max(len(col), df[col].astype(str).map(len).max()) for col in df.columns}
        headers = df.columns.tolist()
        header_line = "| " + " | ".join(f"{header:{col_widths[header]}}" for header in headers) + " |"
        separator_line = "|" + "|".join("-" * (col_widths[header] + 2) for header in headers) + "|"
        rows = []
        for _, row in df.iterrows():
            rows.append(
                "| " + " | ".join(f"{str(cell):{col_widths[header]}}" for cell, header in zip(row, headers)) + " |")
        table = "\n".join([header_line, separator_line] + rows)
        return table

    @staticmethod
    def extract_docker_image_name(command):
        match = re.search(r'image\s+([\w\-:./]+)', command, re.IGNORECASE)
        if not match:
            match = re.search(r'vulnerabilities\s+for\s+([\w\-:./]+)', command, re.IGNORECASE)
        if match:
            return match.group(1)
        else:
            return None


class AWSAIManager:
    def __init__(self, model_name="gpt2"):
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.nlp = spacy.load("en_core_web_sm")

    def generate_code(self, prompt):
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, padding='max_length',
                                          truncation=True)
        attention_mask = input_ids.ne(self.tokenizer.pad_token_id)
        output = self.model.generate(input_ids, attention_mask=attention_mask, max_new_tokens=150,
                                     num_return_sequences=1, temperature=0.7)
        decoded_output = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return decoded_output

    def parse_command(self, command):
        doc = self.nlp(command)
        action = None
        username = None
        permissions_desc = None

        for token in doc:
            if token.lemma_ in ["create", "update", "delete"] and token.dep_ == "ROOT":
                action = token.lemma_ + "_user"
            elif token.lemma_ == "user" or token.lemma_ == "username" or token.lemma_ == "name":
                username_index = token.i + 1
                if username_index < len(doc):
                    username = doc[username_index].text
            elif token.dep_ == "pobj" and token.head.lemma_ == "with":
                permissions_desc = token.text

        if not permissions_desc:
            for chunk in doc.noun_chunks:
                if 'permissions' in chunk.text or 'permission' in chunk.text:
                    permissions_desc = chunk.text

        permissions_keywords = ["s3 read", "s3 write", "read s3", "write s3", "least privileged"]
        for keyword in permissions_keywords:
            if keyword in command:
                permissions_desc = keyword
                break

        permissions = permissions_desc  # Directly use the permissions description for code generation
        return action, username, permissions

    def handle_command(self, command):
        action, username, permissions = self.parse_command(command)
        if action and username and (action == 'delete_user' or permissions):
            prompt = f"Write a Python script to {action.replace('_', ' ')} named {username}"
            if permissions:
                prompt += f" with {permissions} permissions"
            prompt += " in AWS."

            print(f"Generated prompt for code generation: {prompt}")  # Debugging print

            code = self.generate_code(prompt)
            print(f"Generated code:\n{code}")  # Debugging print

            try:
                exec(code)
                print(f"Successfully executed the generated code for {action} {username}.")
            except Exception as e:
                print(f"Error executing generated code: {e}")
        else:
            print("Invalid IAM command or missing parameters.")

    def main(self):
        system_user = getpass.getuser()
        print("Welcome to the AWS AI!")

        while True:
            command = input(f"Hello {system_user}. How can I help you? \n").strip().lower()
            if "add" in command:
                command = command.replace("add", "create")
            print("Sure, I will try my best to help you with your request")

            if "vulnerability" in command:
                classification = nlu_model(command, candidate_labels=["vulnerabilities"])
                if classification["labels"][0] == "vulnerabilities":
                    image_name = DockerManager.extract_docker_image_name(command)
                    image_name = image_name.rstrip('.') if image_name else None

                    if not image_name:
                        print("Unable to extract Docker image name from the command.")
                        continue

                    if not DockerManager.docker_login(os.getenv('DOCKER_USERNAME'), os.getenv('DOCKER_PASSWORD')):
                        print("Docker login failed. Exiting.")
                        continue

                    vulnerabilities = DockerManager.scan_docker_image(image_name)
                    if vulnerabilities:
                        vulnerability_list = DockerManager.parse_vulnerabilities(vulnerabilities)
                        if vulnerability_list:
                            vulnerability_table = DockerManager.vulnerabilities_to_table(vulnerability_list)
                            formatted_table = DockerManager.format_vulnerabilities_table_sql(vulnerability_table)
                            print(formatted_table)
                        else:
                            print("No vulnerabilities found. Image is clean.")
                    else:
                        print("No vulnerabilities found or an error occurred.")
                else:
                    print("The command does not seem to be related to vulnerabilities.")
            else:
                self.handle_command(command)

            if command == "exit":
                print("Exiting...")
                break


if __name__ == "__main__":
    manager = AWSAIManager(model_name="gpt2")
    manager.main()
