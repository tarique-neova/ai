import subprocess
import os
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

# Load the .env file
load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
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
    prompt_end = (
        ". Only provide the Terraform code block, nothing else. Do not include deprecated attributes. Do not create "
        "providers. Also do not include any other text other than the Terraform code block."
    )

    response = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-0125:neova-solutions::9g9dHreT",
        messages=[
            {"role": "system",
             "content": "You are a poetic assistant, skilled in explaining complex programming concepts "
                        "with creative flair. Help me to generate the terraform code only for the following "
                        "requirements. Without comments and Description. Always use the latest parameters "
                        "don't use deprecated parameters. Do not create providers "},
            {"role": "user", "content": f"{prompt}"}
        ]
    )

    if response.choices:
        terraform_code = response.choices[0].message.content.strip()
        with open("terraform_code.tf", "w") as file:
            file.write(terraform_code)
        remove_quotes("terraform_code.tf")
        remove_lines_starting_with_hcl("terraform_code.tf", "main.tf")
        if any(word in prompt.lower() for word in ["give", "show", "display"]):
            with open("main.tf", "r") as file:
                cleaned_code = file.read()
            st.write("Here is the Terraform code to create the requested resource:")
            st.code(cleaned_code, language='hcl')
        else:
            st.write("Here is the Terraform code to create the requested resource:")
            with open("main.tf", "r") as file:
                cleaned_code = file.read()
            st.code(cleaned_code, language='hcl')
            st.write("Creating the requested resource. This may take a couple of minutes.")
            run_terraform()
            remove_terraform_init_files()
    else:
        st.write("Sorry, I'm unable to understand your command.")


def remove_quotes(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    with open(file_path, 'w') as file:
        file.write(content.replace('`', ''))


def remove_terraform_init_files():
    subprocess.run(["sudo", "rm", "-r", ".terraform", ".terraform.lock.hcl", "terraform.tfstate"], capture_output=True,
                   text=True)


def remove_lines_starting_with_hcl(input_file, output_file):
    unwanted_starts = ["hcl", "Sure", "Here", "This", "Please", "The", "Certainly", "You", "terraform", "Below"]
    with open(input_file, 'r') as file:
        lines = file.readlines()

    with open(output_file, 'w') as file:
        for line in lines:
            if not any(line.strip().startswith(start) for start in unwanted_starts):
                file.write(line)


def run_terraform():
    try:
        st.write("Initializing Terraform...")
        subprocess.run(["rm", "-r", "terraform_code.tf"], check=True)
        subprocess.run(["terraform", "init"], check=True)  # Initialize the Terraform configuration
        st.write("Terraform initialization complete.")

        st.write("Applying Terraform changes...")
        apply_result = subprocess.run(["terraform", "apply", "-auto-approve"],
                                      check=True)
        if apply_result.returncode == 0:
            st.write("Terraform apply completed successfully.")
        else:
            st.error("Error applying Terraform configuration. Resource creation failed.")
    except FileNotFoundError:
        st.error("Terraform is not installed or not in the PATH. Please install Terraform and try again.")
    except subprocess.CalledProcessError as e:
        st.error(f"Error applying Terraform configuration: {e.stderr.decode() if e.stderr else e}")


def on_prompt_change():
    global prompt
    prompt = st.session_state.prompt
    chat_with_user()
    st.session_state.prompt = ''


def main():
    st.title("Cloud Resource Creation")
    st.text_input("Enter your prompt:", key="prompt", on_change=on_prompt_change)


if __name__ == "__main__":
    main()
