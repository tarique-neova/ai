import json
import numpy as np
import tiktoken  # Assuming 'tiktoken' is a valid library, adjust import as needed
from collections import defaultdict

data_path = "training.jsonl"

# Load the dataset
dataset = []
with open(data_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            entry = json.loads(line)
            dataset.append(entry)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

# Initial dataset stats
print("Num examples:", len(dataset))
if len(dataset) > 0:
    print("First example:")
    print(dataset[0])  # Print the first entry for inspection

# Format error checks (adjust according to your specific validation needs)
format_errors = defaultdict(int)

for ex in dataset:
    if not isinstance(ex, dict):
        format_errors["data_type"] += 1
        continue

    prompt = ex.get("prompt", None)
    completion = ex.get("completion", None)

    if not prompt or not isinstance(prompt, str):
        format_errors["missing_or_invalid_prompt"] += 1

    if not completion or not isinstance(completion, str):
        format_errors["missing_or_invalid_completion"] += 1

# Print format errors if any
if format_errors:
    print("\nFound format errors:")
    for k, v in format_errors.items():
        print(f"{k}: {v}")
else:
    print("\nNo format errors found")

# Assuming 'tiktoken' provides the following function:
encoding = tiktoken.get_encoding("cl100k_base")


# Functions for token counting and analysis (adapt as needed)
def num_tokens_from_completion(completion):
    return len(encoding.encode(completion))


def print_distribution(values, name):
    print(f"\n#### Distribution of {name}:")
    print(f"min / max: {min(values)}, {max(values)}")
    print(f"mean / median: {np.mean(values)}, {np.median(values)}")
    print(f"p5 / p95: {np.quantile(values, 0.1)}, {np.quantile(values, 0.9)}")


# Example token analysis (adapt to fit your specific analysis needs)
token_counts = [num_tokens_from_completion(entry["completion"]) for entry in dataset]
print_distribution(token_counts, "num_tokens_per_example")
