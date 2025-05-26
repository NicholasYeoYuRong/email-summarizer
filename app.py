from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
import ollama
import time
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS configuration #
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummarizeRequest(BaseModel):
    email: str
    mode: Literal["full", "tldr"] = "full"

class SummarizeResponse(BaseModel):
    summary: str


MODEL_NAME = "email-summarizer-model" # CAN CHANGE YOUR MODEL #

## Only POST is required since we are only prompting and receiving response ##
@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_email(request: SummarizeRequest):
    try:
        # Craft the prompt based on mode #
        if request.mode == "tldr":
            prompt = f"Provide a one-sentence TL;DR summary of this email:\n\n{request.email}"
        else:
            prompt = f"Summarize this email in 2-5 concise sentences:\n\n{request.email}"

        # Call ollama api #
        response = ollama.generate(
            model=MODEL_NAME,
            prompt=prompt,
            # options={
            #     'top_k': 20 # Focus on high-probability tokens
            # }
        )

        # Clean up response and pass into 'summary' variable #
        # strip(): Return a copy of the string with leading and trailing whitespace removed. If chars is given and not None, remove characters in chars instead. #
        summary = response["response"].strip()

        if request.mode == "tldr":
            # Count sentences for TLDR (should be 1) #
            if summary.count('. ') > 0: # If more than 1 sentence
                summary = summary.split(',')[0] + '.'# Take first sentence


        else:
            # Ensure 2-5 sentences for full mode
            sentences = [s.strip() for s in summary.split('.') if s.strip()]
            if len(sentences) > 5:
                summary = '. '.join(sentences[:5]) + '.'
            elif len(sentences) < 2:
                # If too short, try again with different prompt
                prompt = f"Summarize this email in exactly 3 concise sentences:\n\n{request.email}"
                response = ollama.generate(model=MODEL_NAME, prompt=prompt)
                summary = response['response'].strip()
        
        # processing_time = time.time() - start_time
        # print(f"Processing time: {processing_time:.2f} seconds")
        
        return {"summary": summary}



    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))