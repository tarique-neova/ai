import re
import subprocess
import streamlit as st
from groq import Groq

# Initialize Groq client
client = Groq(api_key="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")

# Global variable to store the prompt
prompt = ""


def run_terraform_command(command, working_dir):
    st.write(f"Running command: {command} in directory: {working_dir}")
    try:
        result = subprocess.run(command, cwd=working_dir, shell=True, check=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        st.text(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        st.error(f"Error: {e.stderr.decode()}")
        st.stop()


def chat_with_user():
    global prompt
    prompt_end = (".Only provide the Terraform code, nothing else. Do not include deprecated attributes. Do not create "
                  "providers.")

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
        st.write("Sorry I'm unable to understand your command")


def remove_quotes(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    with open(file_path, 'w') as file:
        file.write(content.replace('`', ''))


def remove_terraform_init_files():
    subprocess.run(["sudo", "rm", "-r", ".terraform", ".terraform.lock.hcl", "terraform.tfstate"], capture_output=True,
                   text=True)


def clean_terraform_code(code):
    # Remove any lines starting with "Here is"
    code_lines = code.split('\n')
    terraform_lines = [
        line for line in code_lines
        if not line.strip().startswith("Here is")
        if not line.strip().startswith("terraform")
    ]
    code_without_provider = re.sub(r'provider\s*"azure".*?{.*?}', '', '\n'.join(terraform_lines), flags=re.DOTALL)

    return code_without_provider


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


def on_prompt_change():
    global prompt
    prompt = st.session_state.prompt
    chat_with_user()
    st.session_state.prompt = ''


def main():
    st.title("Cloud Security AI")
    st.text_input("Enter your prompt:", key="prompt", on_change=on_prompt_change)


if __name__ == "__main__":
    main()
