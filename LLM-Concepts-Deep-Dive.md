# LLM Concepts Deep Dive

*Course: LLM Concepts Deep Dive: Conceptual Mastery for Developers | Udemy Business*
*Notes from: Monday, September 14, 2026*

## Table of Contents

- [What is a Model](#what-is-a-model)
  - [1.1 What is a Language Model?](#11-what-is-a-language-model)
  - [1.2 How Does a Language Model Learn?](#12-how-does-a-language-model-learn)
  - [1.3 What Does "Predict the Likelihood of Next Set of Words" Mean?](#13-what-does-predict-the-likelihood-of-next-set-of-words-mean)
  - [1.4 Language Model vs. Generative AI](#14-language-model-vs-generative-ai)
  - [1.5 Modern LLMs](#15-modern-llms)
- [Two Types of Language Modeling Tasks](#two-types-of-language-modeling-tasks)
  - [2.1 Autoencoding](#21-autoencoding)
  - [2.2 Autoregressive](#22-autoregressive)
- [LLM Training Methodology](#llm-training-methodology)
  - [3.1 Learn/Model Language](#31-learnmodel-language)
  - [3.2 Pre-training](#32-pre-training)
  - [3.3 Weights](#33-weights)
  - [3.4 Pre-training Alone Is Not Enough](#34-pre-training-alone-is-not-enough)
  - [3.5 Fine-tuning](#35-fine-tuning)
- [Tokens and Embeddings](#tokens-and-embeddings)
  - [4.1 How LLMs Process Tokens](#41-how-llms-process-tokens)
  - [4.2 Visualizing Tokenization](#42-visualizing-tokenization)
  - [4.3 Why Isn't One Word Always One Token?](#43-why-isnt-one-word-always-one-token)
  - [4.4 The Solution](#44-the-solution)
  - [4.5 Token Decoding](#45-token-decoding)
  - [4.6 What Numbers Are Assigned to Tokens](#46-what-numbers-are-assigned-to-tokens)
  - [4.7 How the Model Learns](#47-how-the-model-learns)
- [Feature Matrix](#feature-matrix)
  - [5.1 Feature Matrix for Language](#51-feature-matrix-for-language)
- [Embedding](#embedding)
  - [6.1 Understanding Embeddings Using Dimensions](#61-understanding-embeddings-using-dimensions)
  - [6.2 Embedding Math](#62-embedding-math)
- [Tokens and Their Values](#tokens-and-their-values)
  - [7.1 Text Similarity](#71-text-similarity)
- [Transformer Architecture](#transformer-architecture)
- [Context Length in LLMs](#context-length-in-llms)
  - [9.1 LLM State](#91-llm-state)
- [What is RAG](#what-is-rag)
  - [10.1 Vectors and Chunks](#101-vectors-and-chunks)
- [RAG Pipeline](#rag-pipeline)
- [Vector Databases](#vector-databases)
  - [12.1 How It Works — Ingestion](#121-how-it-works--ingestion)
  - [12.2 How It Works — Indexing](#122-how-it-works--indexing)
  - [12.3 How It Works — Querying](#123-how-it-works--querying)
  - [12.4 Some Vector DBs](#124-some-vector-dbs)

## What is a Model

A model is something that represents, simulates, or predicts something else.
It is a simplified version of a real thing that helps us understand it or predict what might happen.

**Example:**

- 🏠 Model of a house - Represents what a real house looks like.
- 🏙️ Model of a city - Represents the roads, buildings, and layout of a real city.
- 🌦️ Weather model - Uses weather data and patterns from the past to predict how the weather may be in the future.
- 🗣️ Language model - Learns patterns in language and predicts what words or tokens are likely to come next.

### 1.1 What is a Language Model?

A language model is a model that learns how language works, its patterns from large amounts of text, such as:

- Which words commonly appear together.
- How sentences are structured.
- How people communicate.
- How words relate to each other.

It then uses these learned patterns to predict and generate language.

### 1.2 How Does a Language Model Learn?

Give thousands of examples. such as:

- The cat is sleeping.
- The dog is running.
- I am drinking water.

Over time, the following patterns are learnt:

- Cat and dog are animals.
- Sleeping and running are actions.
- Words follow certain grammatical patterns.

A language model learns language patterns from text in a similar broad sense, although its internal learning process is based on neural networks and mathematical optimization.

**Example of next-word prediction:**

| Prompt | Predicted next word |
|---|---|
| The sky is | blue |
| I am going to the | market |
| Please open the | door |

### 1.3 What Does "Predict the Likelihood of Next Set of Words" Mean?

A language model looks at the words already written and calculates how likely different next words or tokens are.

**Example:**

Input: `I am going to the`

The model might assign probabilities like this:

| Possible next word | Illustrative likelihood |
|---|---|
| market | 35% |
| office | 25% |
| park | 15% |
| school | 10% |

The model selects or samples a token according to its generation process, then continues predicting the next token.

### 1.4 Language Model vs. Generative AI

This is an important distinction in your notes.

- **Language model** - A model that learns patterns in language and predicts language.
- **Generative AI** - AI that can create new content, such as text, images, music, and videos.
- **LLM (Large Language Model)** - A language model trained on a large amount of data, with many learned parameters, to understand and generate language.

### 1.5 Modern LLMs

- Are Text prediction machines
- Recursive completion – generate text based on previously generated text hence can do this infinitely
- Generates text based on parameters – temperatures
- Uses training data for prediction
- LLM cannot do anything other except generate text
- However, tools can be used to perform external operations using the generated output

## Two Types of Language Modeling Tasks

### 2.1 Autoencoding

A neural network architecture that learns to understand and represent data by encoding it into essential features and reconstructing the original input. In language modeling, it learns by predicting a missing word in a sentence using the surrounding context. Example: "The cat sat on the ___." → "mat".

### 2.2 Autoregressive

A language modeling approach that predicts the next word or token based on the previous words. It generates text one token at a time. Example: "The cat sat on the" → "mat". ChatGPT and other GPT-style LLMs use autoregressive language modeling.

**Remember:**

- Autoencoding: Predict the missing word → Understand language.
- Autoregressive: Predict the next word → Generate language.

Autoregression can also be used for stock price and weather prediction, where future values are predicted from past values.

## LLM Training Methodology

3 main stages that enable an LLM to perform useful tasks.

### 3.1 Learn/Model Language

- First learn/model language
- To model language, the LLM is trained on very large amounts of text so it can learn patterns, relationships, syntax, context, and knowledge contained in that data.

### 3.2 Pre-training

- Initial phase of LLM training - where the model learns from a very large and diverse dataset containing billions or trillions of tokens.
- Develop broad language understanding, contextual patterns, reasoning capabilities, and knowledge represented in the training data.
- For an autoregressive LLM, the model learns to predict the probability of the next token given the previous tokens across a huge number of text sequences.
- Training data is divided into sequences/chunks of tokens; each sequence provides many next-token prediction examples.

**The model learns by adjusting its internal parameters (weights) based on the difference between its predictions and the actual training tokens.**

### 3.3 Weights

- a. They are numerical values (parameters) inside the neural network.
- b. During training, these parameters are continuously adjusted to capture statistical relationships between tokens and their contexts.
- c. For example, the model learns that "cat sat on the" is statistically more likely to be followed by "mat" than "house" in certain contexts.

The goal is to optimize the model parameters so that the model performs well on predicting tokens across diverse language examples.

Training uses backpropagation and gradient descent to calculate how the weights should be adjusted, repeated across many training iterations.

**Training data can include:**

- a. Wikipedia and other reference sources
- b. Books and curated text datasets
- c. Web/internet text and other licensed or publicly available data

### 3.4 Pre-training Alone Is Not Enough

- A pretrained model primarily learns to predict/continue text; it is not automatically a helpful conversational assistant.
- Model should respond appropriately to user requests and have useful conversations.
- This requires additional training to improve instruction following, helpfulness, safety, and response behavior.
- Pre-training is therefore more than simple phone autocomplete, but the underlying next-token prediction objective is similar.
- Additional instruction tuning/post-training is used to teach the model how to respond to instructions and conversations.

### 3.5 Fine-tuning

#### Instruction Tuning

Also called instruction fine-tuning (IFT); it is a form of supervised fine-tuning rather than simply "transfer learning."

The model is trained to follow natural-language instructions and produce appropriate responses.

**Use an instruction dataset:**

- a. Contains instruction/prompt → response examples.
- b. The pretrained model already contains broad language patterns and learned representations, but needs examples of how to follow instructions and format useful responses.
- c. These datasets can be manually created or curated, often containing high-quality question-and-answer or task-and-response examples.
- d. Reinforcement Learning from Human Feedback (RLHF) can be an additional post-training stage used to align responses with human preferences; it is not the same thing as instruction tuning.
- e. A reward model can score responses based on learned human preferences, and reinforcement learning can optimize the model toward higher-reward behavior.

#### Fine-tuning

- Further training of an already pretrained/instruction-tuned model for a specific task, domain, behavior, or use case.
- Focused dataset relevant to the target task—for example, customer-support conversations, legal text, or a specific classification task.
- Additional training is performed on the existing model

**Process:**

- a. Prepare examples representative of the desired task and behavior.
- b. Provide input/output examples showing what response or behavior is desired.

Fine-tuning APIs offered by some model providers allow developers to upload training examples that teach the model "given this type of input, produce this type of output."

## Tokens and Embeddings

- Search engines primarily relied on keyword matching—pages containing more relevant occurrences of the search terms could rank higher.
- However, we want to search based on the meaning and context of words, known as **Semantic search**, rather than exact word matching.
- Example: "Spring framework" should understand that Spring refers to the Java software framework, not the spring season or a car spring.

### 4.1 How LLMs Process Tokens

- LLMs ultimately process numbers, so text must first be converted into numerical representations.
- Character codes such as ASCII/Unicode are not sufficient because they represent characters, not learned linguistic relationships or meaning.
- LLMs learn language patterns and relationships from token sequences; semantic understanding emerges from the model's learned representations.
- Therefore, text is broken into manageable units called tokens, which the model can process efficiently.
- A token is a unit of text, not strictly a "unit of meaning"; meaning is represented through the model's learned embeddings and internal representations.

This is done using tokenization:

- The tokenizer breaks text into tokens.
- Each token is assigned a unique token ID from the model's vocabulary.
- The model receives token IDs and processes them to predict/output token IDs.
- One token is not necessarily one word; it can be a word, part of a word, punctuation, whitespace, or other text fragment.

### 4.2 Visualizing Tokenization

- **Tokenizer playground:** GPT-4o, o200k_base
- **Prompt:** `i am doing tokenization`
- **Token breakdown:** `i am doing token ization`
- **Token count:** 5 tokens
- **Token IDs:** `72, 939, 5306, 6602, 2860`

### 4.3 Why Isn't One Word Always One Token?

- Token IDs are assigned to vocabulary entries so the model can efficiently process text as numbers.
- Words are useful linguistic units, but they are not always the most efficient units for an LLM.
- Giving every possible word its own token would require a very large vocabulary.
- Related words such as learn, learning, learned can share subword pieces rather than requiring completely separate tokens.
- Languages contain an enormous number of words, forms, names, and new words.
- Subword tokenization allows the model to handle related and previously unseen words more efficiently.
- Words can also have multiple meanings; context helps the model determine the intended meaning.

### 4.4 The Solution

- Break text into commonly occurring subword/character sequences, rather than relying only on complete words.
- Tokenizers generally use frequency/statistical patterns in training data to build an efficient vocabulary.
- Punctuation such as a comma can be its own token or part of another token.
- Frequently occurring text sequences can receive their own tokens, making processing more efficient.
- Tokenization is not necessarily based on grammatical word boundaries.
- Different models use different tokenizers and vocabularies, so the same text can produce different tokens and token counts.

**Overall process:** Text → Tokenizer → Token IDs → LLM → learned embeddings/internal representations → predicted Token IDs → Tokenizer → Text. Embeddings are the numerical vectors the model uses to represent tokens in a learned continuous space; they are different from token IDs.

### 4.5 Token Decoding

- The tokenizer processes the text from left to right and splits it into tokens based on the tokenizer's vocabulary and tokenization rules.
- It generally prefers token pieces that efficiently match the available vocabulary; it is not simply a greedy search for the longest English word.
- Example: tokenization may be split into token + ization because those pieces exist in the tokenizer's vocabulary.

### 4.6 What Numbers Are Assigned to Tokens

- Each token is assigned a token ID from the tokenizer's vocabulary. The ID itself does not store the meaning of the token.
- The token ID is then converted into an embedding vector, which is a learned **set of numerical values [,,,]** helps the model represent relationships between tokens.

### 4.7 How the Model Learns

- Example: Picture classification: how does AI determine whether a picture is a cat?
- The model learns to identify cat vs. not-cat from many examples.
- It adjusts its internal parameters based on more examples and learns which visual patterns are useful.
- Features: whiskers, ears, eyes, fur, and body shape can provide signals that a picture may contain a cat.
- Different features can have different importance; a feature such as whiskers may provide a stronger signal than something like background color.
- The model learns patterns by representing features numerically and combining many signals rather than relying on a single feature.
- The model examines features/patterns across many examples and learns which visual characteristics are associated with cats.
- It also learns from incorrect predictions, adjusting its internal parameters when its prediction differs from the correct answer.
- Over many examples, it learns that some attributes have a stronger statistical relationship with the target than others.
- For example, whiskers, ears, eyes, and body shape can be useful signals for identifying a cat, while features such as day vs. night or background are generally less reliable.

## Feature Matrix

**Why does AI require matrix multiplication?**

- In AI, matrix operations are fundamental because models need to process and transform large numbers of values efficiently.
- A feature can be represented as a numerical dimension in a vector; for example, whiskers can be one feature.
- For a simple example: whiskers = 0 for a spoon and whiskers = 1 for a cat or dog.
- Attributes/features can therefore be represented using numerical values for each object.
- In real AI models, the model learns useful features automatically rather than us manually defining features such as whiskers.
- During training, the model adjusts its parameters to capture patterns and correlations that help it perform its task.

### 5.1 Feature Matrix for Language

**LLM create feature matrix for every token**

- An LLM represents each token using a vector of learned numerical features.
- Columns represent learned dimensions/features, and rows represent tokens.
- Each token therefore has a value for every learned dimension.
- The value in each cell represents how strongly that token is represented along that particular learned dimension; these are embedding values, not simply weights.
- For example, a token such as "hello" may have a strong value along a learned dimension associated with greetings or conversational context.
- Because there can be hundreds or thousands of dimensions, each token is represented by an N-dimensional vector.

## Embedding

`[1, 1.04, -2.55, ...]`

- Away of representing things using numbers/vectors based on learned patterns and relationships.
- This set of numerical values is called an embedding.
- Every token is mapped to an embedding vector that captures learned patterns and relationships.
- These embeddings are part of how the model represents and processes language; meaning is not stored in a single number or dimension.

### 6.1 Understanding Embeddings Using Dimensions

Imagine, for simplicity, that we have three dimensions:

- Dimension 1: Pet ↔ Not pet
- Dimension 2: Wild ↔ Not wild
- Dimension 3: Mammal ↔ Not mammal

- Each word/token receives a numerical value along each dimension.
- For example, dog, cat, lion, and crocodile would have different values across these dimensions.
- Dog and cat would tend to have more similar representations because they share several characteristics.
- In real LLMs, there are many more dimensions—often hundreds or thousands—not just three manually defined dimensions.
- Tokens with similar learned representations tend to be closer together in the embedding space.
- Tokens with different representations tend to be farther apart.
- Therefore, similar concepts or usage patterns can occupy nearby regions of the embedding space.

### 6.2 Embedding Math

> Slide: Embedding math!
>
> **Embedding math!**
>
> `v("king") − v("man") + v("woman") ≈ v("queen")`

- v("king") represents the embedding vector for king.
- The relationship captured between king/man and woman/queen can approximately appear through vector arithmetic.
- This demonstrates that embeddings can capture relationships and patterns between words/tokens.
- Embeddings influence how an LLM processes language and are an important part of how it develops useful representations of meaning and context.

## Tokens and Their Values

- Each token has a number called a token ID (an identifier used by the model).
- The token ID is used to look up the token's embedding vector.
- An embedding is a set of numerical values representing how strongly a token is represented across the model's learned dimensions/features.

> Q&A: tokenizer vocab splitting
>
> **Question 1**
> If our tokenizer's vocab contains the subwords {"uni", "vers", "ity", "un", "iverse"}, how would it most likely split the word "university"?
>
> **Answer**
> ["uni", "vers", "ity"] (greedy longest-match)

### 7.1 Text Similarity

**From tokens to text**

> **Problem statement**
>
> Given a sequence of tokens x₁, x₂, …, xₜ, predict the most likely next token xₜ₊₁.

**Two things need to happen:**

- The next token depends on the context of the preceding text, potentially including many earlier tokens.
- Not every part of the previous text is equally relevant to predicting the next token.

**How do you know what's important?**

- The model learns during training which parts of the preceding context are relevant to other parts.
- During processing, mechanisms such as attention allow the model to give more importance to relevant tokens and less importance to less-relevant tokens.
- In this way, the model learns from patterns in the training data which information is useful for predicting the next token.

## Transformer Architecture

> **What transformers do**
>
> - They transform text to an "intermediate" language (encoding)
> - Language is embeddings + positional embeddings
> - Get the best next embeddings
> - Transform that back to text (decoding)

- A Transformer is a neural-network architecture designed to solve the language-modeling problem of understanding context and predicting the next token.
- It uses attention to determine which other tokens are important to each token when building its contextual representation.
- This idea was introduced in the landmark paper "Attention Is All You Need."
- They transform tokens into context-aware numerical representations inside the network.
- The input representation combines token embeddings + positional information.
- Attention and other Transformer layers transform these representations to produce information useful for predicting the next token.
- The model converts the final numerical output into probabilities over possible tokens, and a token is selected/generated from those probabilities.
- Each token effectively "asks" other tokens how relevant they are to its current context through the attention mechanism.
- This is especially important because many words have multiple meanings, and their meaning depends on the surrounding context.
- The token's representation is updated through the Transformer layers based on its relationship with other tokens in the sentence/context.

> **Get the next best embedding**
>
> - Each token "asks" every other token "how relevant are you to me?"
> - Builds a context-aware representation
> - Goes through a process to decide what to do with the relevant tokens
> - Goes through weight matrix to generate the final output tokens
> - There are lot of ambiguous words in english language and meaning depends on the context
> - Embedding is transformed on the fly or adjusted on the fly depending on the meaning of each token with rest pect to the other token in the sentence

> **"How relevant are you?"**
>
> Consider these sentences
>
> - The animal didn't cross the street because it was too tired
> - The animal didn't cross the street because it was too wide

- In the first sentence, "it" is likely referring to the animal, because an animal can be tired.
- In the second sentence, "it" is likely referring to the street, because a street can be wide.
- Attention helps the Transformer use these contextual relationships to build different representations for the same token depending on the surrounding text.

**Key idea:** The embedding starts as a learned representation of a token, but Transformer layers transform it into a context-dependent representation based on the surrounding tokens.

## Context Length in LLMs

**LLM have context limit**

- LLMs have a context limit — the maximum number of tokens the model can consider in a single request.
- The Transformer processes relationships between tokens using attention, and practical/model-design limits determine how many tokens can be handled at once.
- The context typically includes both input tokens and the tokens generated as output, subject to the model's total context window.
- Context length is therefore measured in tokens, not words or characters.

### 9.1 LLM State

**LLMs are stateless and do not have memory**

- LLMs are generally stateless between separate API requests; the model itself does not automatically remember previous conversations.
- Each new request is processed based on the information provided in that request and any external state/memory system.
- The trained model primarily consists of learned parameters (weights); conversation history is not stored inside those weights.
- Therefore, the model does not inherently retain your previous conversation after the request ends.
- To make an LLM behave as though it remembers a conversation, the application can send relevant previous conversation/context with each request.
- Conversation context can contain sensitive or private information, so applications need appropriate data-handling and privacy controls.
- As context becomes very large, cost, latency, and sometimes the model's ability to use all the information effectively can become concerns.

## What is RAG

> **Retrieval Augmented Generation**

- A common way to handle knowledge that is too large, private, or frequently changing to put entirely into the LLM context.
- Dynamically retrieves relevant document chunks at query time.
- Retrieved text should be relevant and useful; the LLM uses the retrieved context to generate the answer, but retrieval quality still matters.
- Often used when the information changes frequently or comes from private documents.

**Goal of RAG** – retrieve relevant information that fits within the model's available context window and provide it to the LLM.

**Example:** "Hello bot, what is the return policy for this particular product of company x?"

- The LLM may not have the company's latest or specific return policy in its model knowledge, so the application needs to retrieve the relevant information from the company's documents or knowledge base.
- The basic process is: find the relevant part of the policy → insert it into the LLM's context → provide the user's question → ask the LLM to generate an answer based on that retrieved context.

### 10.1 Vectors and Chunks

- The key challenge is: how do we find the specific portion of the documents that is relevant to the user's question?
- First, documents are typically split into smaller chunks that can be individually retrieved.
- When the user asks a question, the system searches for the chunks most relevant to that question.
- The relevant chunks are then inserted into the LLM's context along with the user's query.
- To find the appropriate chunks, we can use **semantic similarity—representing** the query and **document chunks as embeddings** and comparing their **vectors**.
- The system **generates an embedding** for the user's query and compares it with the embeddings of the document chunks.
- It retrieves the top-K most similar/relevant chunks and provides them to the LLM.
- This overall approach is called Retrieval-Augmented Generation (RAG):
  - **Retrieval:** find relevant information from the knowledge base.
  - **Augmentation:** add that retrieved information to the user's query/context.
  - **Generation:** the LLM uses the augmented context to generate the response.

## RAG Pipeline

> **RAG Pipeline**

1. **User prompt** → User prompt arrives — this contains what the user is asking LLM
2. **LLM** - The LLM or application creates a retrieval query, which may be the original prompt or a reformulated query to retrieve data from vector database.
3. **Vector DB** — The query is embedded and searched against the vector database. Top-k relevant chunks are retrieved.
4. **Context assembly** — Retrieved chunks are added to the original prompt/context.
5. **Final generation** — Feed the assembled context to the LLM to generate the response.

## Vector Databases

**What is a vector database?**

- A database optimized for storing and searching high-dimensional vectors, often alongside metadata or references to the original documents.
- Can retrieve records using IDs/metadata, but its key RAG capability is vector similarity search.
- Finds vectors that are nearest or most similar to a given query vector.

**The problem**

- Finding the right text is not always easy.
- Simple keyword/text matching may miss relevant content with different wording.
- Semantic/vector search can find text based on meaning and contextual similarity.

**The solution**

- Chunk the documents into smaller pieces.
- Generate an embedding for each document chunk.
- Generate an embedding for the user's query.
- Find the chunks whose vectors are most similar/relevant to the query vector.
- Add the retrieved chunks to the LLM's context.

Vector databases help in these.

> **A vector database query**
>
> "Which stored embedding vectors are closest to my query vector, and what documents do they point at?"

### 12.1 How It Works — Ingestion

- Precompute embeddings for each document/chunk using a chosen embedding model.
- Store the vector along with a unique ID and metadata/payload, such as document ID, source, or text.

### 12.2 How It Works — Indexing

- The database builds a vector-search index, often using an Approximate Nearest Neighbor (ANN) algorithm.
- ANN structures organize/search vectors efficiently so similar vectors can be found much faster than comparing the query with every stored vector.
- Performance depends on the index and implementation; O(log N) is not guaranteed and should not be treated as a general property of vector databases.

### 12.3 How It Works — Querying

- Generate an embedding for the incoming question/query.
- The vector index quickly returns the top-k most similar vectors, usually approximately rather than by exhaustive comparison.
- Retrieve their IDs/metadata and associated document chunks for use as context.

> Code example: vector DB usage
>
> ```python
> from your_vector_db import Client
> from your_embedding_model import embed
>
> # 1. Initialize
> db = Client(api_key="...")
>
> # 2. Upsert documents
> for doc_id, text in docs.items():
>     vec = embed(text)
>     db.upsert(id=doc_id, vector=vec, metadata={"text": text})
>
> # 3. Query
> query = "What is the return policy for electronic items?"
> q_vec = embed(query)
> results = db.search(vector=q_vec, top_k=5)
>
> for hit in results:
>     print(hit.id, hit.score, hit.metadata["text"])
> ```

### 12.4 Some Vector DBs

- Pinecone
- Qdrant
- Weaviate
- Milvus
