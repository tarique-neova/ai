import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer


def generate_aws_iam_user_code():
    # Load pre-trained model and tokenizer
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    model = GPT2LMHeadModel.from_pretrained("gpt2")

    # Set up input prompt for generating IAM user creation code
    input_prompt = "Generate Python code to create an AWS IAM user."
    inputs = tokenizer.encode(input_prompt, return_tensors="pt")

    # Generate output text
    output = model.generate(inputs, max_length=100, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)

    # Decode the output and return the generated Python code
    generated_code = tokenizer.decode(output[0], skip_special_tokens=True)
    return generated_code


if __name__ == "__main__":
    generated_code = generate_aws_iam_user_code()
    print(generated_code)
