# pip install chromadb openai python-dotenv tiktoken
import os, re
from pathlib import Path

import chromadb
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads OPENAI_API_KEY from .env
client = OpenAI()

DOCS_DIR = Path(os.environ["DOCS_DIR"])
CHROMA_DIR = Path(os.environ["CHROMA_DIR"])  # Chroma will persist here (just a folder on disk)

EMBED_MODEL = os.environ["EMBED_MODEL"]  # e.g. text-embedding-3-small: 1536-dim, cheap ($0.02 / 1M tokens)
CHAT_MODEL = os.environ["CHAT_MODEL"]

#enc = tiktoken.get_encoding("cl100k_base")  # tokenizer used by the embedding models
enc = tiktoken.encoding_for_model(EMBED_MODEL)
# print the encoding model for embedding model
print(f"Encoding model for {EMBED_MODEL}: {enc.name}")

# tokenizer used by the embedding models
def n_tokens(text: str) -> int:
    return len(enc.encode(text))



# ---- flag: set to True to re-chunk, re-embed and rebuild the Chroma collection ----
REBUILD_INDEX = False

chroma = chromadb.PersistentClient(path=str(CHROMA_DIR))
index_exists = (
    "hr_policies" in [c.name for c in chroma.list_collections()]
    and chroma.get_collection("hr_policies").count() > 0
)
needs_build = REBUILD_INDEX or not index_exists
if not needs_build:
    print("hr_policies already built - skipping chunking/embedding (set REBUILD_INDEX = True to redo)")

if needs_build:
    documents = {}
    for path in sorted(DOCS_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            print(f"skipping empty file: {path.name}")
            continue
        documents[path.name] = text
        n_words = len(text.split())
        n_toks = n_tokens(text)
        pct_more = (n_toks - n_words) / n_words * 100
        print(f"{path.name}: {n_words:,} words, {n_toks:,} tokens ({pct_more:.1f}% more tokens than words)")
collection = chroma.get_collection("hr_policies")

# chunking the documents into sections and subsections
SECTION_RE = re.compile(r"^=+\n(\d+\.\s+[^\n]+)\n=+\n", re.MULTILINE)   # === / "6. TITLE" / ===
SUBSECTION_RE = re.compile(r"^(?=\d+\.\d+\s)", re.MULTILINE)             # line starting with "6.1 "

def split_sections(text: str) -> list[tuple[str, str]]:
    # re.split with a capture group returns: [preamble, title1, body1, title2, body2, ...]
    parts = SECTION_RE.split(text)
    sections = [("PREAMBLE", parts[0].strip())] if parts[0].strip() else []
    for title, body in zip(parts[1::2], parts[2::2]):
        sections.append((title.strip(), body.strip()))
    return sections

def chunk_document(source: str, text: str, max_tokens: int = 350) -> list[dict]:
    chunks = []
    for section_title, body in split_sections(text):
        subsections = [s.strip() for s in SUBSECTION_RE.split(body) if s.strip()]
        for sub in subsections:
            chunks.append({
                "id": f"{source}::{len(chunks)}",
                "text": f"[{section_title}]\n{sub}",   # section title prefixed for context
                "metadata": {"source": source, "section": section_title, "chunk_index": len(chunks)},
            })
    return chunks

if needs_build:
    all_chunks = []
    for source, text in documents.items():
        all_chunks.extend(chunk_document(source, text))

    sizes = [n_tokens(c["text"]) for c in all_chunks]
    print(f"{len(all_chunks)} chunks | min {min(sizes)} / avg {sum(sizes)//len(sizes)} / max {max(sizes)} tokens")

    # for c in all_chunks[2:4]:
    #     print(f"── {c['id']}  {c['metadata']}")
    #     print(c["text"], "\n")

    def embed_texts(texts: list[str], batch_size: int = 100) -> list[list[float]]:
        vectors = []
        for i in range(0, len(texts), batch_size):
            resp = client.embeddings.create(model=EMBED_MODEL, input=texts[i : i + batch_size])
            vectors.extend(d.embedding for d in resp.data)
        return vectors

    chunk_texts = [c["text"] for c in all_chunks]
    chunk_vectors = embed_texts(chunk_texts)

    total_tokens = sum(n_tokens(t) for t in chunk_texts)
    print(f"embedded {len(chunk_vectors)} chunks x {len(chunk_vectors[0])} dims")
    print(f"~{total_tokens:,} tokens -> cost ≈ ${total_tokens / 1_000_000 * 0.02:.5f}")


    # chrome db section

    # start fresh each time the notebook runs
    if "hr_policies" in [c.name for c in chroma.list_collections()]:
        chroma.delete_collection("hr_policies")

    collection = chroma.create_collection(
        name="hr_policies",
        metadata={"hnsw:space": "cosine"},   # use cosine distance (distance = 1 - cosine similarity)
    )

    for c in all_chunks:
        print(f"Processing chunk with ID: {c['id']}")
        # add each chunk individually to the collection
        collection.add(
            ids=[c["id"]],
            embeddings=[chunk_vectors[all_chunks.index(c)]],  # we pass our own OpenAI vectors
            documents=[chunk_texts[all_chunks.index(c)]],
            metadatas=[c["metadata"]],
        )
    collection.add(
        ids=[c["id"] for c in all_chunks],
        embeddings=chunk_vectors,             # we pass our own OpenAI vectors
        documents=chunk_texts,
        metadatas=[c["metadata"] for c in all_chunks],
    )
    print("records in collection:", collection.count())

for p in sorted(CHROMA_DIR.rglob("*")):
    if p.is_file():
        print(f"{p.relative_to(CHROMA_DIR)}  ({p.stat().st_size:,} bytes)")

reopened = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection("hr_policies")
print("reopened collection has", reopened.count(), "records")
print(reopened.peek(1)["documents"][0][:200])

question = "I spilled coffee on my laptop, what should I do and will I have to pay for it?"

q_vec = client.embeddings.create(model=EMBED_MODEL, input=question).data[0].embedding
print("question vectors: {q_vec}, question vector dims:", len(q_vec))
print(q_vec[:10])                       # first 10 values
print(f"first 5: {q_vec[:5]} ... last 5: {q_vec[-5:]}")

TOP_K = 3
results = reopened.query(
    query_embeddings=[q_vec],
    n_results=TOP_K,
    include=["documents", "metadatas", "distances"],
)

# results are lists-of-lists (one inner list per query vector)
for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
    print(f"distance={dist:.3f}  similarity={1 - dist:.3f}  section={meta['section']}")
    print("   ", doc[:160].replace("\n", " "), "...\n")

def build_context(results) -> str:
    blocks = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        blocks.append(f"<source file='{meta['source']}' section='{meta['section']}'>\n{doc}\n</source>")
    return "\n\n".join(blocks)

SYSTEM_PROMPT = '''You are the HR assistant for Rebind Rise.
Answer the employee's question using ONLY the policy excerpts inside <context>.
- Cite the section(s) you used, e.g. (Section 12. LOSS, THEFT AND DAMAGE).
- If the excerpts don't contain the answer, say you don't know and suggest contacting HR/IT. Do not guess.
- Be concise and practical.'''

context = build_context(results)
user_message = f"<context>\n{context}\n</context>\n\nQuestion: {question}"

print(f"prompt context: {n_tokens(context)} tokens  (vs {n_tokens((DOCS_DIR / 'it-assets-policy.txt').read_text(encoding='utf-8')):,} for the whole doc)\n")

completion = client.chat.completions.create(
    model=CHAT_MODEL,
    temperature=0,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ],
)
print(completion.choices[0].message.content)

def ask(question: str, k: int = 4, show_sources: bool = True) -> str:
    # 4. embed the question
    q_vec = client.embeddings.create(model=EMBED_MODEL, input=question).data[0].embedding
    # 5. top-K search
    res = collection.query(query_embeddings=[q_vec], n_results=k,
                           include=["documents", "metadatas", "distances"])
    # 6. augment + generate
    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"<context>\n{build_context(res)}\n</context>\n\nQuestion: {question}"},
        ],
    )
    if show_sources:
        print("retrieved:", [f"{m['section']} ({1 - d:.2f})" for m, d in zip(res["metadatas"][0], res["distances"][0])])
    return completion.choices[0].message.content

def find_relevant_chunks(query: str, top_k: int = 5) -> list[dict]:
    # convert query to embedding
    # fire query on vector to find top K chunks
    query_embedding = client.embeddings.create(
        model=EMBED_MODEL,
        input=query
    ).data[0].embedding

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )
    chunks = []
    for i, ids in enumerate(results["ids"]):
        for j, chunk_id in enumerate(ids):
            chunks.append({
                "id": chunk_id,
                "text": results["documents"][i][j],
                "metadata": results["metadatas"][i][j],
            })
    return chunks

if __name__ == "__main__":
    # run_rag_pipeline()
    print(ask("Can I use my personal iPhone to check work email?"))
    print(ask("How many planets are there in solar system?"))
    query = "How long I can keep my laptop after I left company"
    relevant_chunks = find_relevant_chunks(query)
    print(f"Relevant chunks for query: {query}, found {len(relevant_chunks)} chunks.")
    for chunk in relevant_chunks:
        print(chunk)

