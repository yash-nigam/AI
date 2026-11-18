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
at the same time keeping the cost low

in some cases we cannot afford to lose the technical information  then we dont compact
or wait till the context limit is reached

or a way to read the context of older conversations


need to add a left panel for all the conversations
on clicking the left hand conversation which api will be called, what data will be passed to it and how the response will be loaded into the main screen


Provide a system prompt which will tell the hr assistant to only respond to questions related to HR system - Like setting up guardrails and boundaries

Remove httpx with Openai sdk


------------
in other cases whether to pass the user question at all to the llm or not that decision needs to be taken on the basis of some conditions, so that decision model needs to be created before calling to the llm 

----
guardrails

building guardrails around the system such that the system does not break when it goes into the production  as in production there is live traffic from users, and the users questions can be vastly differen from the training data set, hence the llm response also could be vastly different

because of high user sessions the cost of llm could increase significantly

----------

local document content loading into llm llm cannot answer the details whic are sitting in mu local document

unless bot answers customized questions and provides custom solutions with custom knolwedgebase how can we provide value to the customer, otherwise chatgpt can do anything

some or the other way the private data needs to be passed to the llm api




small lm canbe built and fine tuned

specific models can be build with weightes favoring specific scenarios our output such as coding 


instead of sending entie doc content to api find the relevant section in the document and only send that section to api
so that the llm has only correct information to work with


--
1 strategy - pass only index document and ask llm, which section from this index belongs to the required question

llm will give a list of sections
we send only those sections to llm

 so we are making an llm call 2 times

 ----------

 what we need is relavance in the document of the users question based on semantic meaning and not just text match. sematic relevance can only be provided by someone who understands language

 semantic search

 select * from document_table where meaning is same as question "procedure to get a new laptop"

 semantic search--

 but this sematich search can only be run on a database which stores and understands the semantic meaning of data

 the text needs to be converted into meaning and then resotred in the database

 =======
=======
It doesn’t store meaning directly. Embeddings encode semantic and contextual relationships learned from data. The meaning is implicit in the geometry: similar items land close together, measured by cosine similarity or dot product. No single dimension holds a meaning.
It’s not limited to text. Images, audio, code, users, products and graph nodes all have embeddings. Text is just the most common case.

A technically accurate version:

“An embedding is a dense numerical vector representation of data, such as text, in a continuous vector space, where semantically similar items are positioned close to each other.”

A shorter version, if you need a one-liner:

“An embedding maps text to a vector such that similar meanings produce nearby vectors.”
=======


so there are embedding models
we will pass our document to hte embedding model
the output embedding will be stored in database
we will search that database


pass the question to embedding model and get embedding
search this embedding in the embedding database to find the other embeddings which closely match this

----------

bfroe embedding entire eoduments
convert the sections of documents into chunks
each chunk should have related information 


when underlying data changes trigger re embedding

revisit the chunking strategy again and again to find the relevant content

if i just say hi i do not need to go to rag - so when to goto rag
wehn to lookup to rag - we may not need to look up at all 
llm 

only after look at the consumer behaviour can we come to conclusion whether we need to hit the rag every time or not

if there a lot of generic questions which already have answer need to go to rag

----------
 a cheap embedding model is needed for converting text into embeddings - aws provides some

 we also need a tokenization model - cl100k_base
 the text is converted into tokens

 