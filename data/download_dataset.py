from datasets import load_dataset
import json
import re
from datetime import datetime
from typing import Dict, List, Any

def json_serializer(obj: Any) -> Any:
    """Custom JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def extract_message_bodies(thread: Dict) -> str:
    """
    Extract and concatenate all 'body' fields from the 'messages' list.
    Returns cleaned, concatenated text of all message bodies.
    """
    if not isinstance(thread, dict):
        return ""
    
    messages = thread.get("messages", [])
    if not isinstance(messages, list):
        return ""
    
    bodies = []
    for message in messages:
        if isinstance(message, dict):
            body = message.get("body", "")
            if body and isinstance(body, str):
                bodies.append(clean_text(body))
    
    return " ".join(bodies) if bodies else ""

def clean_text(text: str) -> str:
    """Basic text cleaning"""
    # Remove quoted text
    text = re.split(r'\nOn.*wrote:|\n-----Original Message-----', text)[0]
    # Remove signatures
    text = re.split(r'\n--|\nBest|\nRegards', text, flags=re.IGNORECASE)[0]
    # Normalize whitespace
    return " ".join(text.strip().split())

def process_dataset(output_path: str = "data/email_bodies.jsonl"):
    """Process dataset and save message bodies with summaries"""
    print("Loading dataset...")
    dataset = load_dataset("sidhq/email-thread-summary", split="train")
    
    # Verify structure
    if not dataset or "thread" not in dataset[0]:
        raise ValueError("Dataset missing 'thread' field")
    
    print("\nSample thread structure (simplified):")
    sample_thread = {
        "messages": [
            {"body": str(msg.get("body", ""))[:100] + "..." if isinstance(msg, dict) else str(msg)}
            for msg in dataset[0]["thread"].get("messages", [])[:2]  # First 2 messages only
        ]
    }
    print(json.dumps(sample_thread, indent=2, default=json_serializer))
    
    with open(output_path, "w") as f:
        for example in dataset:
            try:
                email_body = extract_message_bodies(example["thread"])
                summary = example.get("summary", "")
                
                if email_body:  # Only write non-empty bodies
                    f.write(json.dumps({
                        "email": email_body,
                        "summary": summary
                    }) + "\n")
                    
            except Exception as e:
                print(f"Skipping malformed example: {e}")
                continue
    
    print(f"\nSaved to {output_path}")
    
    # Verify output
    try:
        with open(output_path) as f:
            first_line = json.loads(next(f))
            print("\nFirst output example:")
            print(f"Email length: {len(first_line['email'])} chars")
            print(f"Summary: {first_line['summary'][:100]}...")
    except Exception as e:
        print(f"Output verification failed: {e}")

if __name__ == "__main__":
    process_dataset()