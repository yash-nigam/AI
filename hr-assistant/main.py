import os
from typing import Optional
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI
from db.models import autocreate_tables

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
async def chat(message: str, conversation_id: Optional[int] = None):
    # check if conversation id is provided else create new con id
    if conversation_id == None:
        from db.db import create_conversation
        conversation = create_conversation(title = f"New ConversationL {message[:50]}")
        conversation_id = conversation.id
    
    # use httpx module to send the message to opanapi chat endpoint and whatever response comes from openapi send it back to user
    # before sending the message to OpenAI API, we need to send the entire conversation history as well, so that it can generate a response based on the entire conversation history
    # conversation_history.append({"role": "user", "content": message})
    
    # insert the new message into message table to persist it
    from db.db import insert_message
    insert_message(conversation_id=conversation_id, role="user", content=message)

    # read the entire conversation history from messasge table
    from db.db import list_message
    messages = list_message(conversation_id=conversation_id)
    ch = []
    for m in messages:
        ch.append({"role": m.role, "content": m.content})

    # print all messages
    print(f"Entire conversation history:\n {ch}")
    # perform the post call 
    response = httpx.post(f"{OPENAI_API_URL}", json={
        "model": "gpt-4o-mini",
        "messages": ch
    }, headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"})

    # Add assistant response to conversation history/table
    assistant_reply = response.json()['choices'][0]['message']['content']
    # conversation_history.append({"role": "assistant", "content": assistant_reply})
    insert_message(conversation_id=conversation_id, role="assistant", content=assistant_reply)

    #extract the actual response from the OpenAI API and not the whole json 
    return {"response": f"You said: {message} and OpenAI responded: {response.json()['choices'][0]['message']['content']}"}


if __name__ == "__main__":
    autocreate_tables()  # create tables if they don't exist
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
