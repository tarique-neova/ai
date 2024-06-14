import re
import subprocess
import os
from groq import Groq
import getpass

client = Groq(api_key="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")


def docker_login(username, password):
    try:
        subprocess.run(["sudo", "docker", "login", "--username", username, "--password", password], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while logging in to Docker Hub: {e}")
        return False
    return True


def vulnerabilities_ai():
    while True:
        system_user = getpass.getuser()
        prompt = input(f"Hello {system_user}. How can I help you? \n").strip().lower()

        if prompt.lower() == 'exit':
            print("Exiting...")
            break

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}",
                }
            ],
            model="llama3-8b-8192",
        )

        if chat_completion.choices:
            image_name = extract_docker_image_name(prompt)
            image_name = image_name.rstrip('.')
            print(f"Certainly! Scanning vulnerabilities for docker image {image_name}")
            scan_image(image_name)
            if not image_name:
                print("Unable to extract Docker image name from the command.")
                return
        else:
            print("Sorry I'm unable to understand your command")


def extract_docker_image_name(command):
    # Use regex to find the Docker image name in the command
    match = re.search(r'image\s+([\w\-:./]+)', command, re.IGNORECASE)
    if not match:
        match = re.search(r'vulnerabilities\s+for\s+([\w\-:./]+)', command, re.IGNORECASE)
    if match:
        return match.group(1)
    else:
        return None


def scan_image(image_name):
    try:
        print(f"Scanning image {image_name} for vulnerabilities...")
        result = subprocess.run(["trivy", "image", image_name], capture_output=True, text=True)
        if result.returncode == 0:
            print("Scan completed successfully!")
            print(result.stdout)
        else:
            print("Scan failed!")
            print(result.stderr)
    except FileNotFoundError:
        print("Trivy is not installed. Please install Trivy and try again.")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    # Get Docker Hub credentials
    # Login to Docker Hub
    username = os.getenv('DOCKER_USERNAME')
    password = os.getenv('DOCKER_PASSWORD')

    # Login to Docker Hub
    client = docker_login(username, password)
    if not client:
        return

    vulnerabilities_ai()


if __name__ == "__main__":
    main()
