# from transformers import GPT2LMHeadModel, GPT2Tokenizer, DataCollatorForLanguageModeling, Trainer, TrainingArguments
# from datasets import Dataset
# import os
#
# # Define the dataset
# data = [
#     "Create a new user in AWS IAM",
#     "Grant S3 read permissions to a user",
#     "Delete an IAM user in AWS",
#     "Create an S3 bucket in AWS",
#     "List objects in an S3 bucket",
#     "Configure IAM policies in AWS",
#     "Add tags to an EC2 instance",
#     "Launch an EC2 instance in AWS"
# ]
#
# # Create a dataset object
# dataset = Dataset.from_dict({"text": data})
#
# # Load tokenizer and model
# tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
# tokenizer.add_special_tokens({'pad_token': '[PAD]'})  # Add padding token if necessary
# model = GPT2LMHeadModel.from_pretrained("gpt2")
# model.resize_token_embeddings(len(tokenizer))
#
# # Tokenize the dataset
# def tokenize_function(examples):
#     return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=512)
#
# tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])
#
# # Data collator for language modeling
# data_collator = DataCollatorForLanguageModeling(
#     tokenizer=tokenizer,
#     mlm=False
# )
#
# # Define training arguments
# training_args = TrainingArguments(
#     output_dir="./fine_tuned_gpt2",
#     overwrite_output_dir=True,
#     num_train_epochs=3,  # Adjust epochs as needed
#     per_device_train_batch_size=4,
#     save_steps=1000,
#     save_total_limit=2
# )
#
# # Trainer
# trainer = Trainer(
#     model=model,
#     args=training_args,
#     data_collator=data_collator,
#     train_dataset=tokenized_dataset,
# )
#
# # Fine-tuning
# trainer.train()
#
# # Save the fine-tuned model and tokenizer
# trainer.save_model("./fine_tuned_gpt2")
# tokenizer.save_pretrained("./fine_tuned_gpt2")
import os
from transformers import GPT2Tokenizer, GPT2LMHeadModel, DataCollatorForLanguageModeling, Trainer, TrainingArguments
from datasets import Dataset

# Load tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# Add padding token to the tokenizer
tokenizer.add_special_tokens({'pad_token': '[PAD]'})

model = GPT2LMHeadModel.from_pretrained("gpt2")
model.resize_token_embeddings(len(tokenizer))  # Resize model embeddings to match tokenizer

# Define dataset content
dataset_content = """
Create a new user in AWS IAM
Grant S3 read permissions to a user
Delete an IAM user in AWS
Create an S3 bucket in AWS
List objects in an S3 bucket
Configure IAM policies in AWS
Add tags to an EC2 instance
Launch an EC2 instance in AWS
"""

# Split the content into lines
lines = dataset_content.strip().split('\n')

# Create a Hugging Face dataset from the lines
dataset = Dataset.from_dict({"text": lines})

# Print number of samples
print(f"Number of samples in the dataset: {len(dataset)}")


# Tokenize the dataset
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=512)


tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

# Data collator for language modeling
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# Define training arguments
training_args = TrainingArguments(
    output_dir="./fine_tuned_gpt2",
    overwrite_output_dir=True,
    num_train_epochs=3,  # Adjust epochs as needed
    per_device_train_batch_size=4,
    save_steps=1000,
    save_total_limit=2
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=tokenized_dataset,
)

# Fine-tuning
trainer.train()

# Save the fine-tuned model
trainer.save_model("./fine_tuned_gpt2")
