import json
import os
from typing import Optional
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from db.models import autocreate_tables
from llm.llm_client import call_llm
from db.db import update_conversation_tokens, list_message, insert_message, insert_or_update_conversation_summary, create_conversation, get_conversation_summary, list_messaages_after_summary

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
    result = call_llm(message=message, conversation_id=conversation_id)
    if isinstance(result, JSONResponse):
        return result
    assistant_reply, input_tokens, output_tokens, conversation_id = result

    # insert user message into message table along with token usage for the conversation
    from db.db import insert_message
    insert_message(conversation_id=conversation_id, role="user", content=message, tokens=input_tokens)
 
    # conversation_history.append({"role": "assistant", "content": assistant_reply})
    insert_message(conversation_id=conversation_id, role="assistant", content=assistant_reply, tokens=output_tokens)

    total_tokens = input_tokens + output_tokens
    update_conversation_tokens(conversation_id=conversation_id, tokens=total_tokens)
    print(f"Conversation tokens updated for conversation_id {conversation_id}: {total_tokens} tokens added.")

    #extract the actual response from the OpenAI API and not the whole json 
    return {"response": assistant_reply, "conversation_id": conversation_id}


if __name__ == "__main__":
    autocreate_tables()  # create tables if they don't exist
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
