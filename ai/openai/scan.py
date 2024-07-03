import re
import subprocess
import os
import csv
import json
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

# Load the .env file
load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def docker_login(username, password):
    try:
        result = subprocess.run(["sudo", "docker", "login", "--username", username, "--password", password],
                                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        st.text(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        st.error(f"Error occurred while logging in to Docker Hub: {e.stderr.decode()}")
        return False
    return True


def extract_docker_image_name_with_ai(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant that helps extract Docker image names from prompts."},
            {"role": "user",
             "content": f"Extract the Docker image name from the following prompt, ignoring any additional context or "
                        f"words: {prompt}"}
        ]
    )

    if response.choices:
        extracted_name = response.choices[0].message.content.strip()
        # Check if the extracted name is not None
        if extracted_name is not None:
            # Adding a check to ensure the extracted name is a valid Docker image name
            if re.match(r'^[a-zA-Z0-9\-_.]+(:[a-zA-Z0-9\-_.]+)?$', extracted_name):
                return extracted_name
            else:
                st.warning(f"Failed to extract a valid Docker image name.")
                return None
    else:
        st.error("Failed to extract Docker image name. Please try again.")
        return None


def run_trivy_scan(image_name, format_type):
    try:
        result = subprocess.run(["trivy", "image", f"--format={format_type}", image_name], capture_output=True,
                                text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            st.error("Scan failed!")
            st.error(result.stderr)
            return None
    except FileNotFoundError:
        st.error("Trivy is not installed. Please install Trivy and try again.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None


def scan_image(image_name, display_vulnerabilities, save_to_csv):
    vulnerabilities = run_trivy_scan(image_name, "table")
    if vulnerabilities:
        # Check if no vulnerabilities found
        if "No vulnerabilities found" in vulnerabilities:
            st.write("No vulnerabilities found.")
            if save_to_csv:
                create_empty_csv(image_name)
        else:
            if save_to_csv and display_vulnerabilities:
                vulnerabilities_json = run_trivy_scan(image_name, "json")
                save_vulnerabilities_to_csv(vulnerabilities_json, image_name)
                st.code(vulnerabilities)
            elif save_to_csv:
                vulnerabilities_json = run_trivy_scan(image_name, "json")
                save_vulnerabilities_to_csv(vulnerabilities_json, image_name)
            elif display_vulnerabilities:
                st.code(vulnerabilities)


def create_empty_csv(image_name):
    csv_file = f"{image_name.replace(':', '_').replace('/', '_')}_vulnerabilities.csv"
    with open(csv_file, 'w', newline='') as csvfile:
        fieldnames = ['Target', 'Type', 'VulnerabilityID', 'PkgName', 'InstalledVersion', 'FixedVersion', 'Severity',
                      'Title', 'Description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    st.write(f"Created empty file: {csv_file}")


def save_vulnerabilities_to_csv(vulnerabilities_json, image_name):
    try:
        vulnerabilities_data = json.loads(vulnerabilities_json)

        if 'Results' not in vulnerabilities_data or not vulnerabilities_data['Results']:
            st.write("No vulnerabilities found.")
            create_empty_csv(image_name)
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


def scan_image_page(image_name, prompt):
    st.write(f"Scanning vulnerabilities for Docker image '{image_name}'")
    display_vulnerabilities = 'can' in prompt or 'display' in prompt or 'how' in prompt
    save_to_csv = 'ave' in prompt or 'file' in prompt or 'export' in prompt
    scan_image(image_name, display_vulnerabilities, save_to_csv)


def main():
    st.title("Docker Vulnerability Scanner Solution")
    st.text("""
                This model scans vulnerabilities for any docker image provided to it. 
                Please make sure you enter valid image name in the format 'image_name:tag'
                """)
    prompt = st.text_input("Enter your prompt")
    if prompt:
        image_name = extract_docker_image_name_with_ai(prompt)
        if image_name and ":" in image_name:
            st.write(f"Certainly! Scanning vulnerabilities for Docker image {image_name}")
            scan_image_page(image_name, prompt)
        else:
            st.write("No valid Docker image name found in the prompt. Please enter the Docker image name:")
            image_name_input = st.text_input("Enter the Docker image name:")
            if st.button("Scan Image"):
                scan_image_page(image_name_input, prompt)

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
