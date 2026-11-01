import json
import os
from typing import Optional
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from db.models import autocreate_tables
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
    # check if conversation id is provided else create new con id
    print(f"Checking if conversation_id is provided: {conversation_id}")
    if conversation_id == None:
        print(f"Conversation_id not provided: Creating new conversation for message: {message[:50]}")
        from db.db import create_conversation
        conversation = create_conversation(title = f"New Conversation: {message[:50]}")
        conversation_id = conversation.id
    print(f"Conversation_id: {conversation_id}")    
    
    # use httpx module to send the message to opanapi chat endpoint and whatever response comes from openapi send it back to user
    # before sending the message to OpenAI API, we need to send the entire conversation history as well, so that it can generate a response based on the entire conversation history
    # conversation_history.append({"role": "user", "content": message})
    #  
    # read the entire conversation history from messasge table
    #messages = list_message(conversation_id=conversation_id)

    summary_text = None
    messages_to_send = []
    # Case 1 There might be summary present in the summary table
    #   Then read summary and then read all the messages from the message table which have id greater than lastmessage_id in the summary table
     
    # Case 2 There might not be summary present in the summary table, 
    #   so read all messages from the message table

    print(f"Checking if conversation summary is present for conversation_id {conversation_id}...")
    summary = get_conversation_summary(conversation_id=conversation_id)
    if summary:
        summary_text = summary.summary
        print(f"Conversation summary loaded for conversation_id {conversation_id}:\n{summary_text}\n")
        # include only messages with id greater than lastmessage_id in the summary table
        messages = list_messaages_after_summary(conversation_id=conversation_id, lastmessage_id=summary.lastmessage_id)  
        print(f"Messages loaded after summary for conversation_id {conversation_id}: {[{'role': m.role, 'content': m.content} for m in messages]}\n")
        # print length of messages loaded after summary
        print(f"Number of messages loaded after summary for conversation_id {conversation_id}: {len(messages)}\n")
    else:
        print(f"No conversation summary found for conversation_id {conversation_id}. Loading all messages from message table.")
        summary_text = None
        messages = list_message(conversation_id=conversation_id)

    if len(messages) == 6:
        print(f"Conversation has 6 messages, summarizing conversation for conversation_id {conversation_id}...")
        s=summarize_conversation(conversation_id=conversation_id)
        print(f"Conversation summarized for conversation_id {conversation_id}: {s['summary']}\n")

    ch = []

    if summary_text:
        ch.append({"role": "developer", "content": f"Conversation summary: {summary_text}"})
        print(f"Conversation summary added to conversation history for conversation_id {conversation_id}:\n{summary_text}\n")

    for m in messages:
        ch.append({"role": m.role, "content": m.content})
    
    print(f"Conversation history loaded for conversation_id {conversation_id}: {ch}")
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
    print(f"Conversation tokens updated for conversation_id {conversation_id}: {total_tokens} tokens added.")

    #extract the actual response from the OpenAI API and not the whole json 
    return {"response": assistant_reply, "conversation_id": conversation_id}


def summarize_conversation(conversation_id: int):
    # 1. list all messages for the given conversation_id from the messages table
    # 2. make llm call to summarize the conversation and return the summary
    # 3. store the summary in the conversations table for the given conversation_id
    print(f"Summarizing conversation for conversation_id {conversation_id}...")
    messages = list_message(conversation_id=conversation_id)
    ch = []
    # only include role and content and exclude other fields like id, conversation_id, tokens, created_at
    for m in messages:
        ch.append({"role": m.role, "content": m.content})
    print(f"Conversation history loaded for conversation_id {conversation_id}:{ch}\n")
    
    # perform the post call to OpenAI API to summarize the conversation
    try:
        response = httpx.post(f"{OPENAI_API_URL}", json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "developer", "content": "Summarize the following conversation to less than 100 words. Keep only facts and important information. Ignore pleasentaries and small talk."}] + ch
        }, headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"}, timeout=60)
    except httpx.RequestError as e:
        return JSONResponse(status_code=502, content={"detail": f"Could not reach OpenAI: {type(e).__name__}"})

    if response.status_code != 200:
        return JSONResponse(status_code=502, content={"detail": f"OpenAI error {response.status_code}: {response.text[:200]}"})

    summary = response.json()['choices'][0]['message']['content']
    print(f"Conversation summarized for conversation_id {conversation_id}: {summary}\n")

    # insert the summary into the conversation_summaries table
    lastmessage_id = messages[-1].id if messages else None
    insert_or_update_conversation_summary(conversation_id=conversation_id, summary=summary, lastmessage_id=lastmessage_id)

    return {"summary": summary, "conversation_id": conversation_id}

if __name__ == "__main__":
    autocreate_tables()  # create tables if they don't exist
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
