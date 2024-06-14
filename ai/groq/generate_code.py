import subprocess
import getpass
from groq import Groq

# Initialize Groq client
client = Groq(api_key="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")


def remove_quotes(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    with open(file_path, 'w') as file:
        file.write(content.replace('`', ''))


def chat_with_user():
    while True:
        system_user = getpass.getuser()
        prompt = input(f"Hello {system_user}. How can I help you? \n").strip().lower()
        prompt_end = ".Only provide the Terraform code, nothing else."

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
            print("Certainly! Let me do it for you !!!")

            terraform_code = chat_completion.choices[0].message.content
            terraform_code = clean_terraform_code(terraform_code)
            if "give" in prompt or "show" in prompt or "display" in prompt:
                print(terraform_code)
                with open("terraform_code.tf", "w") as file:
                    file.write(terraform_code)

                print("Terraform code has also been written to terraform_code.tf")
                remove_quotes("terraform_code.tf")
            else:
                print(terraform_code)
                run_terraform()
                remove_terraform_init_files()
        else:
            print("Sorry I'm unable to understand your command")


def clean_terraform_code(code):
    # Remove any lines starting with "Here is"
    code_lines = code.split('\n')
    terraform_lines = [
        line for line in code_lines
        if not line.strip().startswith("Here is")
        if not line.strip().startswith("terraform")
    ]
    return '\n'.join(terraform_lines)


def remove_terraform_init_files():
    subprocess.run(["sudo", "rm", "-r", ".terraform", ".terraform.lock.hcl", "terraform.tfstate"], capture_output=True,
                   text=True)


def run_terraform():
    try:
        print("Initializing Terraform...")
        subprocess.run(["terraform", "init"])  # Initialize the Terraform configuration
        print("Terraform initialization complete.")

        print("Applying Terraform changes...")
        subprocess.run(["terraform", "apply", "-auto-approve"])  # Apply the Terraform configuration
        print("Terraform apply completed successfully.")
    except FileNotFoundError:
        print("Terraform is not installed or not in the PATH. Please install Terraform and try again.")


def main():
    chat_with_user()


if __name__ == "__main__":
    main()
