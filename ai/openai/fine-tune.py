import os
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load the .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Upload the training file
try:
    upload_response = client.files.create(
        file=open("chat_formatted_data.jsonl", "rb"),
        purpose="fine-tune"
    )

    # Extract the training file ID from the upload_response object
    training_file_id = upload_response.id
    print(f"Training file uploaded successfully. File ID: {training_file_id}")

    # Create the fine-tuning job
    fine_tuning_response = client.fine_tuning.jobs.create(
        training_file=training_file_id,
        model="gpt-3.5-turbo"
    )

    # Extract the job ID from the fine_tuning_response object
    job_id = fine_tuning_response.id
    print(f"Fine-tuning job created successfully. Job ID: {job_id}")

    # Monitor the fine-tuning job status and retrieve the updated model ID
    while True:
        job_status_response = client.fine_tuning.jobs.retrieve(job_id)
        job_status = job_status_response.status
        if job_status == 'succeeded':
            updated_model_id = job_status_response.fine_tuned_model
            print(f"Fine-tuning succeeded. Updated Model ID: {updated_model_id}")
            break
        elif job_status == 'failed':
            error_message = job_status_response.error.message
            print(f"Fine-tuning failed. Error: {error_message}")
            break
        else:
            print(f"Fine-tuning job status: {job_status}. Waiting to complete...")
            time.sleep(60)

except Exception as e:
    print(f"An error occurred: {str(e)}")
