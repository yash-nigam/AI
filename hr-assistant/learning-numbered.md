# Learning Notes

## 1. Goal: Learning AI Features Through Real-World Problems

- Identify problems and solve those problems using features of AI
- Learn multiple features of AI by solving real world problems

## 2. The LLM API Is Stateless

- Since the LLM API is stateless and does not remember the previous question, we need to include all previous conversation history (responses of the user and assistant) in every subsequent API call so that the LLM has a context and there is meaningful conversation

## 3. Problems With Sending the Entire Conversation History

- Including entire conversation history in every API call creates the following problems:
  - API call message content doubles on every turn
  - We will be charged more as more tokens are being passed
  - Since input data has increased, the accuracy of the LLM reduces
  - There is a latency issue
  - The limit can be breached

## 4. Persisting the Conversation

- The conversation history with the LLM will be lost if it is not saved to disk
- Hence conversation history must be saved to disk
- A persistent layer needs to be added

## 5. Database Design

- Store each message - role and message per row in a database table
- There can be multiple conversations which I want to continue in parallel
- There can be a set of messages per conversation
- Tables: messages table and conversations table
- There will be a conversation id as a foreign key in the messages table

## 6. The /chat Endpoint Flow

- In the /chat endpoint we will add a conversation_id parameter
- If no conversation id is passed, a new conversation id is created and all messages of this conversation will use that conversation id
- Insert the user provided prompt or message into the messages table along with the new conversation id
- After inserting, read all the messages from the messages table as a conversation history array, as we need to pass the entire history to the API

## 7. Tracking Token Usage

- An additional problem which comes up is the number of tokens used per API call
- We need to know the exact number of tokens per API call to calculate cost
- Keep track of tokens per message in a separate tokens field in the messages and conversations tables

## 8. Context and the Context Window

- As the number of messages in a conversation increases, those need to be summarized infrequently to keep the number of tokens per message low
- Both the user questions and the assistant responses for the entire conversation need to be passed in every LLM API call, hence the data or tokens passed to the API double at every call
- This is also called context, and there is also a limit to the context window
- If the amount of input + output tokens increases past the context window, the response could be cut in between

## 9. Context Management, Summarization, and Compaction

- Hence AI engineering also involves context management, context summarization or context compaction
- Summarization needs to be done in such a way that the unnecessary stuff is removed but the essence is kept, hence the LLM has the required historical or past messages to create a relevant output

## 10. Storing the Summary

- Store the last message id up to which the summary has been calculated
- Store the summary inside a separate table
  - The table stores the actual summary, the conversation id, and the id of the message till which the summarization was done
- We need to know till which message the summarization was done, so that we can send the summary plus the messages after the summary

## 11. Summarization Logic

- Whenever the user creates a new conversation there is no past summary, as there is no message history
- As the user keeps on typing messages and the assistant responds, the conversation history increases
- A threshold of 10 messages has been set
  - If a conversation reaches 10 consecutive messages, a summary is generated for those 10 messages
  - That summary is saved in the summary table along with the last message id, which would be 10
- When the user types the 11th question, the LLM is not sent the entire history of 10 messages
  - It is sent only the summary of the first 10 messages and the 11th message
- Similarly for the 12th message, it is sent the summary of the first 10 messages and the 2 newer messages
- In this way we can keep a check on the growing token usage in a conversation


## 12. Reading a Document and Using It in the LLM

- While calling the LLM, we need to call it with the relevant text
- Whatever prompt we type needs to pick up the relevant chunk first
- Enrich the chunk with the relevant LLM
- All calls will be made from the LLM client
- In ChromaDB we should store the actual data along with the embedding data, so that when an embedding match is found for a prompt, we can pull the actual text data for that match
- An LLM can also be used to chunk the files
  - It will keep all related chunks together, along with some duplication
  - Every chunk includes metadata
  - At the same time, every chunk should be independent
- We may not always want to read from ChromaDB, as the question may or may not really need a lookup in the policy file

---

## Assignment 1: Chatbot for Internal Company Documents

### Problem Statement

- How to design a system - a chatbot for my internal company documents - and a high-level design of it
- The documents are sitting in various locations: some in Confluence, some as PDFs, some as Word documents, and some in doc sites. How do we design a system for that?
- Total size is 50 GB
- How to handle changes in documents, chunking, and where the data will be stored
- What will the overall RAG pipeline look like, and what are the nuances?

### Requirements and Constraints

- After a change in any document, the change should appear within 24 hours at most
- We can use a hash to check whether a file has changed
- The maximum file size will be 5 GB, and the total will not be more than 50 GB
- The documents will not have images, but will have tables and formatting
- Pagination may be used to solve the 5 GB file problem
- Formatting is not guaranteed, so the prompt needs to be created accordingly
- The LLM also has a limit on request body size

### Handling Tables

- There are also tables in the documents
  - Ask the LLM to summarize the table, or keep metadata on top
  - While querying, the descriptive data is used from the database
- Whenever you find a table, my embedding engine does not allow searching solely based on the table
  - So create a summary text for the table, so that the table can be identified using the summary text or metadata
- If the metadata of a table is matched in the vector DB, we can retrieve the original table from the chunk and pass that table back to the LLM

### Handling Images

- The same applies to images: create a text alternative of the image, so that the text becomes relevant for the image and search works
- We can pass the image back to the LLM
- The intent of embedding is to make search work perfectly

### Chunking Nuances

- Some data between two sections can be lost
- If the LLM is not able to chunk the last part of a section, those lines should be taken into the next chunk
- This smartness has to be added to the RAG pipeline so that we don't miss any data
- In order to chunk my data I am using an LLM
  - That is a trade-off I am taking
  - I am OK spending on every chunking cycle, but my chunks are perfect, and the consumer will get the right information only

### Vector Database and Embeddings

- The vector DB should scale based on the data size
- There are dedicated databases for embedding algorithms
- Just by searching "dog", I can find the photo of the dog
- The embedding algorithm needs to be language specific
- Media embeddings are completely different

### Open Questions

- Is it worth maintaining a RAG pipeline where the human effort is higher if there is a low number of users?
- Can one table be one chunk?
- There can be cases where... *(incomplete note)*

---

## Assignment 2: Natural Language Questions over SQL Tables

- We have SQL tables with hundreds of tables, and someone asks a question in human language instead of SQL
- We have access to the DB and can run the query - we need a system that can do that
- There can be 2000 tables - we need an interface where a natural language question can be asked and answers can be given
- We do not always need a RAG system, as RAG has some fundamental problems
  - PageIndex is an alternative to RAG

---

## Assignment 3: Prompt Caching

- If most of the questions are common, they can be stored in advance instead of searching for them or querying them every time, as each call requires an LLM call, which costs money
- How do we design the solution?
- I want to avoid LLM calls
- If a question matches a previous question to a certain extent, we can retrieve the top matching questions and get their answers
- Keep a note of relevant previously asked questions
- Other ways to reduce the cost of the LLM: caching responses

Prompt caching should also be done semantically meaning the the users prompt should be semantically matched to the history of prompts

for this use chroma db to store embeddings of prompts and responses in in a prompts table


all the conversations should be shown as a list in the left navigation bar in the ui and clicking on the conversation should load the conversation history into the main ui as bubbles