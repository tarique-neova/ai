import re
import subprocess
import os
import csv
import json
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
            if image_name:
                image_name = image_name.rstrip('.')
                save_to_csv = 'save' in prompt or 'file' in prompt
                print(f"Certainly! Scanning vulnerabilities for docker image {image_name}")
                scan_image(image_name, save_to_csv)
            else:
                print("Unable to extract Docker image name from the command.")
        else:
            print("Sorry I'm unable to understand your command")


def extract_docker_image_name(command):
    match = re.search(r'for\s+([\w\-:./]+)\s+image', command, re.IGNORECASE)
    if not match:
        match = re.search(r'image\s+([\w\-:./]+)', command, re.IGNORECASE)
    if not match:
        match = re.search(r'vulnerabilities\s+for\s+([\w\-:./]+)', command, re.IGNORECASE)
    if match:
        return match.group(1)
    else:
        return None


def scan_image(image_name, save_to_csv):
    try:
        print(f"Scanning image {image_name} for vulnerabilities...")
        if save_to_csv:
            result = subprocess.run(["trivy", "image", "--format", "json", image_name], capture_output=True, text=True)
            if result.returncode == 0:
                print("Scan completed successfully!")
                vulnerabilities = result.stdout
                save_vulnerabilities_to_csv(vulnerabilities, image_name)
            else:
                print("Scan failed!")
                print(result.stderr)
        else:
            result = subprocess.run(["trivy", "image", image_name], capture_output=True, text=True)
            if result.returncode == 0:
                print("Scan completed successfully!")
                vulnerabilities = result.stdout
                print(vulnerabilities)
            else:
                print("Scan failed!")
                print(result.stderr)
    except FileNotFoundError:
        print("Trivy is not installed. Please install Trivy and try again.")
    except Exception as e:
        print(f"An error occurred: {e}")


def save_vulnerabilities_to_csv(vulnerabilities_json, image_name):
    try:
        vulnerabilities_data = json.loads(vulnerabilities_json)

        if 'Results' not in vulnerabilities_data or len(vulnerabilities_data['Results']) == 0:
            print("No vulnerabilities found.")
            return

        csv_file = f"{image_name.replace(':', '_').replace('/', '_')}_vulnerabilities.csv"
        with open(csv_file, 'w', newline='') as csvfile:
            fieldnames = ['Target', 'Type', 'VulnerabilityID', 'PkgName', 'InstalledVersion', 'FixedVersion',
                          'Severity', 'Title', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for result in vulnerabilities_data['Results']:
                for vulnerability in result.get('Vulnerabilities', []):
                    writer.writerow({
                        'Target': result.get('Target', ''),
                        'Type': result.get('Type', ''),
                        'VulnerabilityID': vulnerability.get('VulnerabilityID', ''),
                        'PkgName': vulnerability.get('PkgName', ''),
                        'InstalledVersion': vulnerability.get('InstalledVersion', ''),
                        'FixedVersion': vulnerability.get('FixedVersion', ''),
                        'Severity': vulnerability.get('Severity', ''),
                        'Title': vulnerability.get('Title', ''),
                        'Description': vulnerability.get('Description', ''),
                    })

        print(f"Vulnerabilities saved to {csv_file}")

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
    except Exception as e:
        print(f"An error occurred while saving to CSV: {e}")


def main():
    username = os.getenv('DOCKER_USERNAME')
    password = os.getenv('DOCKER_PASSWORD')

    if not username or not password:
        print("Docker Hub username and password must be set as environment variables (DOCKER_USERNAME and "
              "DOCKER_PASSWORD).")
        return

    if not docker_login(username, password):
        return

    vulnerabilities_ai()


if __name__ == "__main__":
    main()
