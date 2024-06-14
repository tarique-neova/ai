import pandas as pd
from datasets import Dataset
from transformers import GPT2LMHeadModel, GPT2Tokenizer, DataCollatorForLanguageModeling, Trainer, TrainingArguments

# Define the dataset containing examples of Python code for creating AWS IAM users
data = [
    {"text": "Generate Python code to create an AWS IAM user.",
     "code": "import boto3\n\niam = boto3.client('iam')\niam.create_user(UserName='new_user')"}
    # Add more examples as needed
]

# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(data)

# Create a dataset object from the DataFrame
dataset = Dataset.from_pandas(df)

# Load tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")
model.resize_token_embeddings(len(tokenizer))
tokenizer.add_special_tokens({'pad_token': '[PAD]'})


# Tokenize the dataset
def tokenize_function(examples):
    return tokenizer(examples["text"], padding=True, truncation=True, max_length=512)


tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

# Data collator for language modeling
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    logging_dir="./logs",
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    eval_dataset=tokenized_dataset,
    data_collator=data_collator,
)

# Fine-tuning
trainer.train()

# Generate Python code
input_prompt = "Generate Python code to create an AWS IAM user."
inputs = tokenizer(input_prompt, return_tensors="pt")
output = model.generate(inputs.input_ids, max_length=100, num_return_sequences=1)
generated_code = tokenizer.decode(output[0], skip_special_tokens=True)

print(generated_code)
