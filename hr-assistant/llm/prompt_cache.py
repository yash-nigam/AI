import uuid

from db.db import insert_message, list_message
SIMILARITY_THRESHOLD = 0.85  # threshold for semantic similarity (0.0 - 1.0)

# an exact search function which will check if the prompt is already present in the conversation history and return the response if it is present
def find_response_in_conversation_history(message: str, conversation_id: str) -> str:
    """
    Check if the user's question is already present in the conversation history.
    If yes, return the previous answer from the conversation history.
    """
    print(f"Searching for previous response for message: {message[:50]} in conversation_id {conversation_id} from SQL DB")
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
    print(f"Caching response for prompt: {prompt[:50]} in conversation_id {conversation_id} in SQL DB")
    # insert the prompt and response into the message table with the given conversation_id
    insert_message(conversation_id=conversation_id, role="user", content=prompt)
    insert_message(conversation_id=conversation_id, role="assistant", content=response)

# A semantic search function which will find a matching prompt in the conversation history based on semantic similarity and return the response if it is found
# Chroma db will be used to store the embeddings of the prompts and responses in the conversation history, and a semantic search will be performed to find a matching prompt based on semantic similarity
# this function will store the embeddings of the prompts and responses in the conversation history in a Chroma db collection, and perform a semantic search to find a matching prompt based on semantic similarity, and return the response if it is found
def cache_embedded_prompt_response_in_chroma_db(prompt: str, response: str, conversation_id: str):
    """
    Store the prompt and response in a Chroma db collection for semantic search.
    """
    print(f"Storing embedded prompt and response in Chroma DB for conversation_id {conversation_id}")
    # create a Chroma db client
    from embed import chroma, client as openai_client, EMBED_MODEL

    # one shared, persistent collection for all conversations
    collection = chroma.get_or_create_collection(
        name="prompt_cache",
        metadata={"hnsw:space": "cosine"},
    )

    # embed both texts in a single API call
    resp = openai_client.embeddings.create(model=EMBED_MODEL, input=[prompt, response])
    prompt_embedding, response_embedding = (d.embedding for d in resp.data)

    uid = uuid.uuid4().hex  # unique ids, so a second message in the same conversation doesn't collide
    collection.add(
        ids=[f"{uid}_prompt", f"{uid}_response"],
        documents=[prompt, response],
        embeddings=[prompt_embedding, response_embedding],
        metadatas=[
            {"role": "user", "conversation_id": conversation_id},
            {"role": "assistant", "conversation_id": conversation_id},
        ],
    )

def fetch_cached_response_from_chroma_db(prompt: str, conversation_id: str) -> str:
    """
    Fetch a cached response from the Chroma db collection based on semantic similarity.
    """
    from embed import chroma, client as openai_client, EMBED_MODEL
    print(f"Searching for cached response for prompt: {prompt[:50]} in conversation_id {conversation_id} from Chroma DB")
    collection = chroma.get_or_create_collection(
        name="prompt_cache", metadata={"hnsw:space": "cosine"}
    )
    if collection.count() == 0:
        return None

    # convert query to embedding
    query_embedding = openai_client.embeddings.create(
        model=EMBED_MODEL,
        input=prompt
    ).data[0].embedding

    # perform a semantic search in the Chroma db collection
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1,
        #where={"role": "user", "conversation_id": conversation_id},
        where={"$and": [{"role": "user"}, {"conversation_id": conversation_id}]},
    )

    if not results["ids"][0]:
        return None

    similarity = 1 - results["distances"][0][0]   # cosine distance -> similarity
    if similarity < SIMILARITY_THRESHOLD:
        return None

    # matched id is "<uid>_prompt" -> the paired answer is "<uid>_response"
    response_id = results["ids"][0][0].replace("_prompt", "_response")
    stored = collection.get(ids=[response_id])
    return stored["documents"][0] if stored["documents"] else None