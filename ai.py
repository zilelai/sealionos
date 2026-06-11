import os
import json
import urllib.request
import urllib.error
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("YOUR_API")

if not API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY environment variable")

app = FastAPI()


class PromptRequest(BaseModel):
    prompt: str

MODEL = "gemini-2.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

@app.post("/ask")
def ask_gemini(request: PromptRequest):
    user_prompt = request.prompt.strip()
    
    if not user_prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        

    payload = {
        "contents": [{"parts": [{"text": user_prompt}]}]
    }
    json_data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        URL,
        data=json_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            ai_text = result['candidates'][0]['content']['parts'][0]['text']
            return {"response": ai_text}

    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise HTTPException(status_code=429, detail="Gemini API rate limit exceeded")
        else:
            raise HTTPException(status_code=e.code, detail=f"ERROR!!!\n: {e.reason}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
