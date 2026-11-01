# number all the points below

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

An additional problems which comes up is the number of token used per api call 
we need to know exact number of tokens per api call to claculate cost
keep a track of tokens per message in separate tokens field in messages and conversation table

as the number of messasgesi= in a conversation increase those needs to be summarized infrequently to keep the number of tokens per message low. Since both the user questions and the assistant response for the entire conversation needs to be passed in every llm api call hence the data or tokens passed to the api double at every call. This is also called as context, and there is also a limit to the context window.

If the amount of input+output tokens increase pass the context window the the response could be cut in between

Hence AI engineering also involves context management, context summarization or context compaction
Summarization needs to be done in such a way that the unnecessary stuff is removed but the essence is kept hence the llm has the require historical or past messages to create a relevant output

store the last message till which the summary is being calculated
store the summary inside a separte table store actual summary - conversation id, and the id of message till the summarization was done
- we need to know till which message the summzarization was done, summary plus message agfter summary

summarization logic
whenever user creates a new conversation then there would be no past summary as there is no message history
as user keeps on typing messages and there assitent responds to it the conversation history increases
we have kept a threshold of 10 messages 
if in a conversation there are consequently 10 conversation, then a summary will be generated for those 10 messages
that summary will be saved in summary table along with the last message id which would be 10

so when the user types in 11th question the llm will not be sent the entire history of 10 messages
but only the summary of the last 10 messages and only the 11th message

similarly for 12th message also, the summary of first 1o messages and the 2 newer messages  

in this way we can keep a check on the grwoing token usage in an conversation



