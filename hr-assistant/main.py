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

# history needs to be maintained for both user and assistant messages, so we can send the entire history to OpenAI API for context
# this needs to be sent on every request to OpenAI API, so that it can generate a response based on the entire conversation history
conversation_history = []

@app.get("/chat")
async def chat(message: str):
    # use httpx module to send the message to opanapi chat endpoint and whatever response comes from openapi send it back to user
    # before sending the message to OpenAI API, we need to send the entire conversation history as well, so that it can generate a response based on the entire conversation history
    conversation_history.append({"role": "user", "content": message})
    print(f"Conversation history: {conversation_history}")
    response = httpx.post(f"{OPENAI_API_URL}", json={
        "model": "gpt-4o-mini",
        "messages": conversation_history
    }, headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"})

    # Add assistant response to conversation history
    conversation_history.append({"role": "assistant", "content": response.json()['choices'][0]['message']['content']})
    
    #extract the actual response from the OpenAI API and not the whole json 
    return {"response": f"You said: {message} and OpenAI responded: {response.json()['choices'][0]['message']['content']}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
