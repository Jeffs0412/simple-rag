"""Minimal RAG pipeline: markdown -> ChromaDB (OpenAI embeddings) -> grounded answer.

No LangChain, no LlamaIndex. Just openai + chromadb + python-dotenv.

Usage:
    python simple_rag.py                 # interactive prompt
    python simple_rag.py "your question" # one-shot
"""

import os
import re
import sys

import chromadb
from dotenv import load_dotenv
from openai import APIError, OpenAI

DOCS_PATH = "sample_docs.md"
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
TOP_K = 2

SYSTEM_PROMPT = """You are a question-answering assistant restricted to the CONTEXT below.

Rules:
1. Answer ONLY using facts stated in the CONTEXT. Do not use outside knowledge.
2. If the CONTEXT does not contain the answer, reply with exactly: I don't know
3. Do not guess, infer beyond the text, or pad the answer with caveats.
4. Keep the answer short and cite the section heading(s) you used."""


def chunk_markdown(path):
    """Split a markdown file on `##` headers. Returns [(heading, text), ...]."""
    with open(path, encoding="utf-8") as f:
        raw = f.read()

    # Keep the heading with its body by splitting *before* each `## ` line.
    parts = re.split(r"^##\s+(.+)$", raw, flags=re.MULTILINE)
    # parts = [preamble, heading1, body1, heading2, body2, ...]
    chunks = []
    preamble = parts[0].strip()
    if preamble:
        chunks.append(("(preamble)", preamble))

    for heading, body in zip(parts[1::2], parts[2::2]):
        heading = heading.strip()
        body = body.strip()
        if body:
            chunks.append((heading, f"## {heading}\n\n{body}"))

    return chunks


def build_collection(client, openai_client, chunks):
    """Embed the chunks and load them into a fresh in-memory collection."""
    collection = client.create_collection(name="docs")

    texts = [text for _, text in chunks]
    response = openai_client.embeddings.create(model=EMBED_MODEL, input=texts)
    embeddings = [item.embedding for item in response.data]

    collection.add(
        ids=[f"chunk-{i}" for i in range(len(chunks))],
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"heading": heading} for heading, _ in chunks],
    )
    return collection


def retrieve(collection, openai_client, question, k=TOP_K):
    """Return the k chunks closest to the question."""
    query_embedding = openai_client.embeddings.create(
        model=EMBED_MODEL, input=[question]
    ).data[0].embedding

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(k, collection.count()),
    )
    return list(
        zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    )


def answer(openai_client, question, hits):
    context = "\n\n---\n\n".join(doc for doc, _, _ in hits)
    response = openai_client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"CONTEXT:\n{context}\n\nQUESTION: {question}",
            },
        ],
    )
    return response.choices[0].message.content.strip()


def main():
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set (put it in a .env file next to this script).")
    if not os.path.exists(DOCS_PATH):
        sys.exit(f"Missing {DOCS_PATH}")

    openai_client = OpenAI()

    chunks = chunk_markdown(DOCS_PATH)
    if not chunks:
        sys.exit(f"No `##` sections found in {DOCS_PATH}")
    print(f"Indexing {len(chunks)} chunks from {DOCS_PATH} ...")

    chroma = chromadb.EphemeralClient()  # in-memory, nothing persisted to disk
    collection = build_collection(chroma, openai_client, chunks)

    question = " ".join(sys.argv[1:]).strip()
    if not question:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            sys.exit("\nCancelled.")
    if not question:
        sys.exit("No question given.")

    hits = retrieve(collection, openai_client, question)

    print("\n" + "=" * 70)
    print("RETRIEVED CONTEXT")
    print("=" * 70)
    for i, (doc, meta, distance) in enumerate(hits, 1):
        print(f"\n[{i}] {meta['heading']}  (distance {distance:.4f})\n")
        print(doc)

    print("\n" + "=" * 70)
    print("ANSWER")
    print("=" * 70)
    print(answer(openai_client, question, hits))


if __name__ == "__main__":
    try:
        main()
    except APIError as exc:
        sys.exit(f"\nOpenAI API error: {getattr(exc, 'message', exc)}")
