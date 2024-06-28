import json

input_file = "training.jsonl"  # Replace with your actual input file

# Read and process the prompt-completion formatted data
dialogs = []
with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            entry = json.loads(line)
            prompt = entry.get("prompt", "")
            completion = entry.get("completion", "")
            dialogs.append({"messages": [{"role": "user", "content": prompt},
                                         {"role": "assistant", "content": completion}]})
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

# Save the processed data in chat format
output_file = "chat_formatted_data.jsonl"
with open(output_file, 'w', encoding='utf-8') as f:
    for dialog in dialogs:
        json.dump(dialog, f)
        f.write('\n')

print(f"Successfully converted prompt-completion data to chat format. Saved to {output_file}")
