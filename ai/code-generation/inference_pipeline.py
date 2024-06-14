from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

# Load the tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')


class GenerateCode:
    def generate_code(query, model, tokenizer, max_length=150):
        inputs = tokenizer.encode(query, return_tensors='pt')
        attention_mask = torch.ones(inputs.shape, dtype=torch.long)  # Create attention mask
        outputs = model.generate(inputs, attention_mask=attention_mask, max_length=max_length, num_return_sequences=1)
        code = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return code

    # Example usage
    query = "Give me a Python code to create AWS IAM user"
    generated_code = generate_code(query, model, tokenizer)
    print(generated_code)
