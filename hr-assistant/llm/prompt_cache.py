from db.db import insert_message, list_message


def find_response_in_conversation_history(message: str, conversation_id: str) -> str:
    """
    Check if the user's question is already present in the conversation history.
    If yes, return the previous answer from the conversation history.
    """
    # read all messages from the message table for the given conversation_id
    messages = list_message(conversation_id=conversation_id)
    # iterate through the messages and check if the user's question is already present
    for m in messages:
        if m.role == "user" and m.content == message:
            # if the user's question is found, return the previous answer from the conversation history
            for m2 in messages:
                if m2.role == "assistant" and m2.id > m.id:
                    return m2.content
    return None

def cache_response(prompt: str, response: str, conversation_id: str):
    """
    Cache the response for future use in the messages table.
    """
    # insert the prompt and response into the message table with the given conversation_id
    insert_message(conversation_id=conversation_id, role="user", content=prompt)
    insert_message(conversation_id=conversation_id, role="assistant", content=response)