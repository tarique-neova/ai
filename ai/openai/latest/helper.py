import subprocess
import sys


def run_terraform_command(command, working_dir):
    print(f"Running command: {command} in directory: {working_dir}")
    try:
        result = subprocess.run(command, cwd=working_dir, shell=True, check=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode()}", file=sys.stderr)
