# simple-rag

A minimal RAG (retrieval-augmented generation) pipeline in one Python file, with no
LangChain and no LlamaIndex. About 150 lines, so you can read the whole thing and see
exactly what a RAG pipeline does.

```
markdown file  ->  split on ## headers  ->  embed  ->  ChromaDB (in-memory)
                                                             |
                    question  ->  embed  ->  top-2 nearest chunks
                                                             |
                             strict system prompt + context  ->  LLM  ->  answer
```

## What it does

1. Reads `sample_docs.md` and splits it into chunks on `##` markdown headers, keeping
   each heading attached to its body.
2. Embeds every chunk with OpenAI `text-embedding-3-small` in a single batched call.
3. Loads them into an in-memory ChromaDB collection (nothing is written to disk).
4. Embeds your question and retrieves the 2 nearest chunks.
5. Sends those chunks to `gpt-4o-mini` under a system prompt that permits **only**
   context-grounded answers, and requires the exact reply `I don't know` otherwise.
6. Prints the retrieved chunks with their similarity distances, then the answer.

Printing the retrieved context before the answer is deliberate: when a RAG system gives
a bad answer, the cause is usually retrieval, not generation, and you cannot tell the
difference unless you can see what was retrieved.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # then put your OpenAI key in .env
```

`requirements.txt` pins the three direct dependencies. `requirements.lock.txt` pins the
full 85-package closure for an exact rebuild, but it was generated on CPython 3.13 /
win_amd64 and contains platform-specific wheels -- on Linux or macOS use
`requirements.txt` and regenerate the lock if you need one.

## Usage

```bash
python simple_rag.py                              # prompts for a question
python simple_rag.py "when are deploys allowed?"  # or pass one as an argument
```

## Example

```
$ python simple_rag.py "how many days do I have to submit travel receipts?"
Indexing 6 chunks from sample_docs.md ...

======================================================================
RETRIEVED CONTEXT
======================================================================

[1] Expense Policy  (distance 0.6913)

## Expense Policy

Employees may spend up to $75 per day on meals while travelling without
pre-approval. ... Receipts must be submitted within 14 days of returning;
claims filed later than 30 days are rejected outright. Alcohol is never
reimbursable, including on client dinners.

[2] Vacation and Leave  (distance 1.2943)
...

======================================================================
ANSWER
======================================================================
You have 14 days to submit travel receipts, and alcohol is never reimbursable.
(Sections: Expense Policy)
```

Ask something the documents do not cover and you get `I don't know` -- retrieval still
returns its two best chunks no matter how weak the match, so the grounding constraint in
the system prompt is what prevents an invented answer.

## Swapping in your own documents

Point `DOCS_PATH` at any markdown file with `##` headers. The chunker treats each `##`
section as one chunk and anything before the first header as a preamble chunk. Sections
that comfortably fit the embedding model's context window work best; for very long ones
you would want to sub-split, which this script deliberately does not do.

## Notes and limits

- Kept intentionally small. No chunk overlap, no re-ranking, no citations beyond the
  section heading, no conversation history, no persistence -- the collection is rebuilt
  on every run, which is fine for a corpus this size and wasteful for a real one.
- Retrieval is fixed at the top 2 chunks (`TOP_K`).
- Requires OpenAI API credits. Indexing this sample corpus plus one question costs a
  fraction of a cent.

## License

MIT
