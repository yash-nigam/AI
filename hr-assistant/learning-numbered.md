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
