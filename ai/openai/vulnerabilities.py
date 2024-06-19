import re
import subprocess
import os
import csv
import json
import openai
from dotenv import load_dotenv
import streamlit as st

# Load the .env file
load_dotenv()

# Set your OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key


def docker_login(username, password):
    try:
        result = subprocess.run(["sudo", "docker", "login", "--username", username, "--password", password],
                                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        st.text(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        st.error(f"Error occurred while logging in to Docker Hub: {e.stderr.decode()}")
        return False
    return True


def chat_with_user(prompt):
    chat_completion = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{prompt}"}
        ],
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5
    )

    if chat_completion.choices:
        user_message = chat_completion.choices[0].message['content'].strip()
        return user_message
    else:
        return "Sorry, I'm unable to understand your command."


def extract_docker_image_name(command):
    patterns = [
        r'for\s+docker\s+image\s+([\w\-:./]+)',  # for docker image <image>
        r'image\s+([\w\-:./]+)',  # image <image>
        r'vulnerabilities\s+for\s+([\w\-:./]+)',  # vulnerabilities for <image>
        r'scan\s+docker\s+image\s+([\w\-:./]+)',  # scan docker image <image>
    ]
    for pattern in patterns:
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def scan_image(image_name, save_to_csv):
    try:
        st.write(f"Scanning image {image_name} for vulnerabilities...")
        if save_to_csv:
            result = subprocess.run(["trivy", "image", "--format", "json", image_name], capture_output=True, text=True)
            if result.returncode == 0:
                st.write("Scan completed successfully!")
                vulnerabilities = result.stdout
                save_vulnerabilities_to_csv(vulnerabilities, image_name)
            else:
                st.error("Scan failed!")
                st.error(result.stderr)
        else:
            result = subprocess.run(["trivy", "image", image_name], capture_output=True, text=True)
            if result.returncode == 0:
                st.write("Scan completed successfully!")
                vulnerabilities = result.stdout
                st.text(vulnerabilities)
            else:
                st.error("Scan failed!")
                st.error(result.stderr)
    except FileNotFoundError:
        st.error("Trivy is not installed. Please install Trivy and try again.")
    except Exception as e:
        st.error(f"An error occurred: {e}")


def save_vulnerabilities_to_csv(vulnerabilities_json, image_name):
    try:
        vulnerabilities_data = json.loads(vulnerabilities_json)

        if 'Results' not in vulnerabilities_data or len(vulnerabilities_data['Results']) == 0:
            st.write("No vulnerabilities found.")
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

        st.write(f"Vulnerabilities saved to {csv_file}")

    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON: {e}")
    except Exception as e:
        st.error(f"An error occurred while saving to CSV: {e}")


def on_prompt_change():
    prompt = st.session_state.prompt
    response = chat_with_user(prompt)
    st.session_state.prompt = ''  # Clear the input field

    image_name = extract_docker_image_name(prompt)
    if image_name:
        image_name = image_name.rstrip('.')
        save_to_csv = 'save' in prompt or 'file' in prompt
        st.write(f"Certainly! Scanning vulnerabilities for docker image {image_name}")
        scan_image(image_name, save_to_csv)
    else:
        st.write(response)


def main():
    st.title("Docker Vulnerability Scanner AI")
    st.text_input("Enter your prompt:", key="prompt", on_change=on_prompt_change)

    username = os.getenv('DOCKER_USERNAME')
    password = os.getenv('DOCKER_PASSWORD')

    if not username or not password:
        st.error(
            "Docker Hub username and password must be set as environment variables (DOCKER_USERNAME and "
            "DOCKER_PASSWORD).")
        return

    if not docker_login(username, password):
        return


if __name__ == "__main__":
    main()
