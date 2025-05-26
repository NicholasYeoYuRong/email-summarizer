from rouge_score import rouge_scorer
import json
import time
import requests
from typing import Dict
from pathlib import Path

def load_test_data(data_path: str) -> list:
    """Load JSONL test data"""
    with open(data_path) as f:
        return [json.loads(line) for line in f]

def evaluate_service(
    test_data: list,
    service_url: str = "http://localhost:8000/summarize",
    mode: str = "full"
) -> Dict[str, float]:
    """Run ROUGE evaluation against the summarization service"""
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    totals = {"rouge1": 0, "rouge2": 0, "rougeL": 0}
    latencies = []
    
    for item in test_data:
        start_time = time.time()
        response = requests.post(
            service_url,
            json={"email": item["email"], "mode": mode}
        )
        latency = time.time() - start_time
        latencies.append(latency)
        
        if response.status_code == 200:
            scores = scorer.score(
                item["summary"],
                response.json()["summary"]
            )
            for key in totals:
                totals[key] += scores[key].fmeasure
    
    return {
        "rouge_scores": {k: v/len(test_data) for k,v in totals.items()},
        "avg_latency": sum(latencies)/len(latencies)
    }

if __name__ == "__main__":
    test_data = load_test_data("data/email_bodies.jsonl")[:100]  # First 100 samples
    results = evaluate_service(test_data)
    
    print("\nEvaluation Results:")
    print(f"ROUGE-1: {results['rouge_scores']['rouge1']:.3f}")
    print(f"ROUGE-2: {results['rouge_scores']['rouge2']:.3f}")
    print(f"ROUGE-L: {results['rouge_scores']['rougeL']:.3f}")
    print(f"Avg Latency: {results['avg_latency']:.2f}s")