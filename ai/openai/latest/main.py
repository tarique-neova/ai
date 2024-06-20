from openai import OpenAI
from helper import run_terraform_command
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Get user input
user_input = input("Enter your command: ")

completion = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts "
                                      "with creative flair. Help me to generate the terraform code only for the following "
                                      "requirements. Without comments and Description. Always use the latest parameters "
                                      "don't use deprecated parameters. Do not create providers "},
        {"role": "user", "content": f"{user_input}"}
    ]
)

print(completion.choices[0].message.content.replace("```hcl", "").replace("```", ""))

if completion.choices:
    with open("terraform/main.tf", 'a') as file:
        file.write(f'\n{completion.choices[0].message.content.replace("```hcl", "").replace("```", "")}\n')

try:
    run_terraform_command("terraform init", "terraform")
    run_terraform_command("terraform apply --auto-approve", "terraform")
except Exception as e:
    print(e)
