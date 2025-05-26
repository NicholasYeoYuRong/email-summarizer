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
