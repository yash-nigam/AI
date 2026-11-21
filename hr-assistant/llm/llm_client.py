import json
import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from db.db import list_message, insert_or_update_conversation_summary, create_conversation, get_conversation_summary, list_messaages_after_summary
from embed import find_relevant_chunks
from llm.prompt_cache import cache_embedded_prompt_response_in_chroma_db, cache_response, fetch_cached_response_from_chroma_db, find_response_in_conversation_history
load_dotenv()  # reads .env into environment variables
OPENAI_API_URL = os.environ["OPENAI_API_URL"]
# the SDK appends /chat/completions itself, so strip it from the configured endpoint URL
OPENAI_BASE_URL = OPENAI_API_URL.removesuffix("/").removesuffix("/chat/completions")
openai_client = OpenAI(base_url=OPENAI_BASE_URL, api_key=os.environ["OPENAI_API_KEY"], timeout=60)

# A tool to return current date and time in ISO format, for use in LLM prompts. This is a simple example of a tool that can be used to provide additional context to the LLM.
# below is a tool definition in json format, which will be passed to the OpenAI API in the tools parameter of the chat.completions.create() call. The LLM can then call this tool by name, and the API will return the tool's output to the LLM.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Returns the current date and time in a human-readable format.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "greet_user",
            "description": "Greets the user by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the user to greet."
                    }
                },
                "required": ["name"]
            }
        }
    }
]
def get_current_datetime():
    from datetime import datetime
    # human-readable, e.g. "Saturday, 21 November 2026, 10:52 AM"
    now = datetime.now()
    return f"Today's date and time: {now.strftime('%A, %d %B %Y, %I:%M %p')}"
# function enrivh prompt will read relevant chunks from the chroma db and attach it to the original promp
def enrich_prompt(prompt: str) -> str:
    relevant_chunks = find_relevant_chunks(prompt)
    top_chunk = relevant_chunks[0] if relevant_chunks else ""
    enriched_prompt = f"here is the relevent infomation from my internal policy DB for below question:{top_chunk['text']}, Question : {prompt}"
    return enriched_prompt

def call_llm(message: str, conversation_id=None):
    # returns (assistant_reply, input_tokens, output_tokens, conversation_id) on success,
    # or a JSONResponse on failure

    # Prompt caching
    # Check if the users question is already present in the conversation history, 
    # if yes then return the previous answer from the conversation history
    
    # find lexical match for the prompt in the conversation history, if found return the response from the conversation history
    if conversation_id is not None:
        response = find_response_in_conversation_history(message, conversation_id)
        if response:
            print(f"Found previous response for message: {message[:50]} in conversation_id {conversation_id}")
            # if the flow reaches here it means the user has asked the same question again, so we can return the previous response from the conversation history
            # no need to go through the entire LLM call flow again, just return the previous response from the conversation history
            # return the same 4-tuple shape as a normal call; 0 tokens since no LLM call was made
            return response, 0, 0, conversation_id
        
        # find semantic match for the prompt in the conversation history using Chroma DB, if found return the response from the conversation history
        response = fetch_cached_response_from_chroma_db(message, conversation_id)
        if response:
            print(f"Found previous response for message: {message[:50]} in conversation_id {conversation_id} from Chroma DB")
            # This is the one place we DO insert into SQL from call_llm: the paraphrased question
            # isn't in the messages table yet, and main.py skips inserts when tokens are 0 (cache hit),
            # so without this the exchange would be missing from the user's history.
            cache_response(message, response, conversation_id)
            return response, 0, 0, conversation_id


    enriched_prompt = enrich_prompt(message)

    # check if conversation id is provided else create new con id
    print(f"Checking if conversation_id is provided: {conversation_id}")
    if conversation_id == None:
        print(f"Conversation_id not provided: Creating new conversation for message: {message[:50]}")
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

    # adding the enriched prompt to the conversation history
    ch.append({"role": "developer", "content": f"Enriched prompt: {enriched_prompt}"})

    # perform the chat completions call using the OpenAI SDK
    # timeout (60s) is configured on the client, as the default is too short for longer LLM answers
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=ch,
            tools=TOOLS,)
    except openai.APIStatusError as e:
        return JSONResponse(status_code=502, content={"detail": f"OpenAI error {e.status_code}: {str(e.response.text)[:200]}"})
    except openai.APIConnectionError as e:
        return JSONResponse(status_code=502, content={"detail": f"Could not reach OpenAI: {type(e).__name__}"})

    # print response from OpenAI API in pretty format
    print(f"Response from OpenAI API:\n{response.model_dump_json(indent=4)}\n")

    # check if there is a tool call in the response, if yes then run the tool(s) and return the tool output directly to the user
    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        print(f"Executing tool calls detected in OpenAI API response for conversation_id {conversation_id}...")
        tool_outputs = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_args = tool_call.function.arguments
            print(f"Tool call detected in OpenAI API response: {tool_name} with arguments: {tool_args}")
            if tool_name == "get_current_datetime":
                tool_response = get_current_datetime()
            elif tool_name == "greet_user":
                # arguments arrive as a JSON string, e.g. '{"name": "Yash"}'
                args = json.loads(tool_args or "{}")
                name = args.get("name", "User")
                tool_response = f"Hello, {name}, you are being greeted by a Tool Call!"
            else:
                print(f"Unknown tool call detected in OpenAI API response: {tool_name}")
                return JSONResponse(status_code=400, content={"detail": f"Unknown tool call detected in OpenAI API response: {tool_name}"})
            print(f"Tool response from {tool_name}: {tool_response}")
            tool_outputs.append(tool_response)

        # send the tool output itself back to the UI (no second LLM call).
        # Not cached in Chroma: tool output such as the current time goes stale.
        tool_reply = "\n".join(tool_outputs)
        return tool_reply, response.usage.prompt_tokens, response.usage.completion_tokens, conversation_id

    reply = response.choices[0].message.content
    # NOTE: we deliberately do NOT call cache_response() (SQL insert) here.
    # On a cache miss, main.py's /chat endpoint already inserts the user + assistant messages
    # (with token counts) after call_llm returns. Inserting here too would store every
    # new exchange twice.
    # We only store the embedded prompt/response in Chroma here, so that later
    # similar questions can hit the semantic cache.
    cache_embedded_prompt_response_in_chroma_db(message, reply, conversation_id)

    # Read input tokens
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    print(f"Input tokens: {input_tokens}, Output tokens: {output_tokens}, Total tokens: {input_tokens + output_tokens}")

    # Add assistant response to conversation history/table
    assistant_reply = reply

    return assistant_reply, input_tokens, output_tokens, conversation_id


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

    # perform the chat completions call using the OpenAI SDK to summarize the conversation
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "developer", "content": "Summarize the following conversation to less than 100 words. Keep only facts and important information. Ignore pleasentaries and small talk."}] + ch,
        )
    except openai.APIStatusError as e:
        return JSONResponse(status_code=502, content={"detail": f"OpenAI error {e.status_code}: {str(e.response.text)[:200]}"})
    except openai.APIConnectionError as e:
        return JSONResponse(status_code=502, content={"detail": f"Could not reach OpenAI: {type(e).__name__}"})

    summary = response.choices[0].message.content
    print(f"Conversation summarized for conversation_id {conversation_id}: {summary}\n")

    # insert the summary into the conversation_summaries table
    lastmessage_id = messages[-1].id if messages else None
    insert_or_update_conversation_summary(conversation_id=conversation_id, summary=summary, lastmessage_id=lastmessage_id)

    return {"summary": summary, "conversation_id": conversation_id}
