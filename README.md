# Convert JSONL to Ollama format
python -c "
import json
with open('training_data.jsonl') as f:
    pairs = [json.loads(line) for line in f]
with open('finetune.md','a') as f:
    for p in pairs:
        f.write(f'MESSAGE user \"Email: {p[\"Email\"]}\"\n')
        f.write(f'MESSAGE assistant \"Summary: {p[\"Summary\"]}\"\n\n')
"# email-summarizer

# Funtionalities and Specifications #
- Summarizes email in 2 modes: Full | TLDR
- Custom model is used to help faclitate in summation of email.
- Pulled out dataset from HuggingFace and evaluate the model against it.

# API Used #
- Fastapi
- Ollama

- # Finetune.md #
- Model fine-tuned to identify phishing emails
- Examples used < 50 examples
- Not fully usable
