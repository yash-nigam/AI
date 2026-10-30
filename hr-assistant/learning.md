Identify problems and solve those problems using features of AI
Learn multiple features of AI by solving real world problems
1 - since llm api is stateless and does not remember the previous question, 
we need to include all previous conversation history (responses of the user and assistant) in every subsequent api call so that the llm has a context  and there is meaningful conversation

2- Including entire conversation history in every api call creates the following problems
api call message content doubles on every turn
we will be charged more as more tokens are being passed
since input data has increased the accuracy of llm reduces
there is latency issue
The limit can be breached

3 - Persisting the conversation
The conversation history with LLM will be lost if it is not saved to disk
hence conversation history must be saved to disk
persistent layer needs to be added

Store each message - role and message per row in a database table
There can be multiple conversation which i want con continue parallely
and there can be a set of messages per conversation

messages table and conversations table
there will be a conversation id as a foreing in messages table
in the /chat endpoint we will add conversation_id parameter
if there is no conversation id is passed then a new conversation id is created and all messages of this conversation will use that conversation id

insert the user provided prompt or message into the the message table along with new conversation id

after inserting, read all the messages from message table as conversation history array
as we need to pass the entire history to the api


