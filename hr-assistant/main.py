import json
import os
from typing import Optional
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from db.models import autocreate_tables
from db.db import update_conversation_tokens, list_message

load_dotenv()  # reads .env into environment variables
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_API_URL = os.environ["OPENAI_API_URL"]

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def index():
    return FileResponse("static/index.html")

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
        print(f"Conversation_id not provided: Creating new conversation for message: {message[:50]}")
        from db.db import create_conversation
        conversation = create_conversation(title = f"New Conversation: {message[:50]}")
        conversation_id = conversation.id
    print(f"Conversation_id: {conversation_id}")    
    
    # use httpx module to send the message to opanapi chat endpoint and whatever response comes from openapi send it back to user
    # before sending the message to OpenAI API, we need to send the entire conversation history as well, so that it can generate a response based on the entire conversation history
    # conversation_history.append({"role": "user", "content": message}) 
    # read the entire conversation history from messasge table
    
    messages = list_message(conversation_id=conversation_id)
    ch = []
    for m in messages:
        ch.append({"role": m.role, "content": m.content})
    print(f"Conversation history loaded for conversation_id {conversation_id}:\n")
    # add the latest user message to the conversation history
    ch.append({"role": "user", "content": message})

    # perform the post call 
    # httpx defaults to a 5s timeout, which is too short for longer LLM answers
    try:
        response = httpx.post(f"{OPENAI_API_URL}", json={
            "model": "gpt-4o-mini",
            "messages": ch
        }, headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"}, timeout=60)
    except httpx.RequestError as e:
        return JSONResponse(status_code=502, content={"detail": f"Could not reach OpenAI: {type(e).__name__}"})

    if response.status_code != 200:
        return JSONResponse(status_code=502, content={"detail": f"OpenAI error {response.status_code}: {response.text[:200]}"})

    # print response from OpenAI API in pretty format
    import json
    pretty_response = json.dumps(response.json(), indent=4)

    print(f"Response from OpenAI API:\n{pretty_response}\n")

    # Read input tokens
    input_tokens = response.json()["usage"]["prompt_tokens"]
    output_tokens = response.json()["usage"]["completion_tokens"]
    print(f"Input tokens: {input_tokens}, Output tokens: {output_tokens}, Total tokens: {input_tokens + output_tokens}")

    # Add assistant response to conversation history/table
    assistant_reply = response.json()['choices'][0]['message']['content']
 
    # insert user message into message table along with token usage for the conversation
    from db.db import insert_message
    insert_message(conversation_id=conversation_id, role="user", content=message, tokens=input_tokens)
 
    # conversation_history.append({"role": "assistant", "content": assistant_reply})
    insert_message(conversation_id=conversation_id, role="assistant", content=assistant_reply, tokens=output_tokens)

    total_tokens = input_tokens + output_tokens
    update_conversation_tokens(conversation_id=conversation_id, tokens=total_tokens)

    #extract the actual response from the OpenAI API and not the whole json 
    return {"response": assistant_reply, "conversation_id": conversation_id}


if __name__ == "__main__":
    autocreate_tables()  # create tables if they don't exist
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
