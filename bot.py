import os
from groq import Groq
import subprocess
import sys

client = Groq(api_key="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")

def run_terraform_command(command, working_dir):
    print(f"Running command: {command} in directory: {working_dir}")
    try:
        result = subprocess.run(command, cwd=working_dir, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode()}", file=sys.stderr)
        sys.exit(1)

def chat_with_user(prompt):
    while True:
        # prompt = input("Enter your prompt (or 'exit' to quit): ")
        prompt_end = ".Only provide the Terraform code, nothing else. Do not include deprecated attributes. Do not create providers"

        if prompt.lower() == 'exit':
            print("Exiting...")
            break

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}+{prompt_end}",
                }
            ],
            model="llama3-8b-8192",
        )

        if chat_completion.choices:
            with open("aws/main.tf", 'a') as file:
                file.write(f'\n{(chat_completion.choices[0].message.content).replace("```terraform","").replace("```","")}\n')
            try:
                # run_terraform_command("terraform init", "aws")
                # run_terraform_command("terraform apply --auto-approve", "aws")
                return (chat_completion.choices[0].message.content).replace("```terraform","").replace("```","")
            except Exception as e:
                print(e)
        else:
           with open("aws/main.tf", 'r') as file:
            content = file.read()
            content = content.replace((chat_completion.choices[0].message.content).replace("```terraform","").replace("```",""), '')

def main():
    print("Welcome to the Groq Chatbot. Enter your prompts below.")
    chat_with_user()

# if __name__ == "__main__":
#     main()
