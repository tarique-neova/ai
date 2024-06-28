import os
from openai import OpenAI
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

upload_file = client.files.create(
    file=open("chat_formatted_data.jsonl", "rb"),
    purpose="fine-tune"
)

client.fine_tuning.jobs.create(
  training_file="file-1jWivERWQr3FSEqZwPXns2Na",
  model="gpt-3.5-turbo"
)
