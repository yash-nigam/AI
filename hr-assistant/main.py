import os
import httpx    
from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI

load_dotenv()  # reads .env into environment variables
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_API_URL = os.environ["OPENAI_API_URL"]

app = FastAPI()

@app.get("/")
async def hello():
    return {"message": "Hello, World!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/chat")
async def chat(message: str):
    # use httpx module to send the message to opanapi chat endpoint and whatever response comes from openapi send it back to user
    response = httpx.post(f"{OPENAI_API_URL}", json={
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": message}]
    }, headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"})

    #extract the actual response from the OpenAI API and not the whole json 
    return {"response": f"You said: {message} and OpenAI responded: {response.json()['choices'][0]['message']['content']}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
