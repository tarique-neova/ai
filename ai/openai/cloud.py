import subprocess
import os
import openai
from dotenv import load_dotenv
import streamlit as st

# Load the .env file
load_dotenv()

# Set your OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key


def generate_terraform_code(prompt):
    prompt_end = (
        ". Only provide the Terraform code, nothing else. Do not include deprecated attributes. Do not create "
        "providers. Also do not include any other text other than code")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{prompt}{prompt_end}"}
        ],
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5
    )
    return response.choices[0].message['content'].strip()


def save_terraform_code(code, filename='main.tf'):
    with open(filename, 'w') as file:
        file.write(code)


def remove_quotes(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    with open(file_path, 'w') as file:
        file.write(content.replace('`', ''))


def remove_terraform_init_files():
    subprocess.run(["sudo", "rm", "-r", ".terraform", ".terraform.lock.hcl", "terraform.tfstate"], capture_output=True,
                   text=True)


def clean_terraform_code(code):
    # Clean the code by removing unwanted lines
    code_lines = code.split('\n')
    terraform_lines = [line for line in code_lines if not line.strip().startswith("hcl")]
    return '\n'.join(terraform_lines)


def apply_terraform():
    # Initialize Terraform
    subprocess.run(["terraform", "init"], check=True)
    # Apply Terraform configuration
    subprocess.run(["terraform", "apply", "-auto-approve"], check=True)


def run_terraform():
    try:
        st.write("Initializing Terraform...")
        subprocess.run(["terraform", "init"])  # Initialize the Terraform configuration
        st.write("Terraform initialization complete.")

        st.write("Applying Terraform changes...")
        subprocess.run(["terraform", "apply", "-auto-approve"])  # Apply the Terraform configuration
        st.write("Terraform apply completed successfully.")
    except FileNotFoundError:
        st.error("Terraform is not installed or not in the PATH. Please install Terraform and try again.")


def main():
    st.title("Terraform Code Generator")
    user_input = st.text_input("Enter your request:")

    if user_input:
        if "create resource" in user_input.lower():
            prompt = f"Generate Terraform code to {user_input}"
            chat_completion = generate_terraform_code(prompt)
            terraform_code = chat_completion.choices[0].message.content
            terraform_code = clean_terraform_code(terraform_code)
            with open("terraform_code.tf", "w") as file:
                file.write(terraform_code)
            remove_quotes("terraform_code.tf")

            if "give" in prompt or "show" in prompt or "display" in prompt:
                st.write("Here is the terraform code to create requested resource")
                st.code(terraform_code, language='hcl')
            else:
                st.write("Here is the terraform code to create requested resource")
                st.code(terraform_code, language='hcl')
                st.write("Creating requested resource. This may take couple of minutes.")
                run_terraform()
                st.write("Requested resource has been created successfully...")
                remove_terraform_init_files()
        else:
            st.write("Sorry, I'm unable to understand your command.")


if __name__ == "__main__":
    main()
