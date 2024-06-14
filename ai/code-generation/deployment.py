from flask import Flask, request, jsonify
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from inference_pipeline import GenerateCode
app = Flask(__name__)

# Load the tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')


@app.route('/generate_code', methods=['POST'])
def generate_code_endpoint():
    data = request.json
    query = data['query']
    generated_code = GenerateCode.generate_code(query, model, tokenizer)
    return jsonify({'code': generated_code})


if __name__ == '__main__':
    app.run(debug=True)
