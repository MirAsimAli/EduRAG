import os
import chromadb
import textwrap
from groq import Groq

# 1. Load Chroma DB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection("books_embeddings")  # change name if needed

# 2. Initialize Retriever (search function)
def retrieve_context(query, k=3):
    results = collection.query(
        query_texts=[query],
        n_results=k
    )
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    return list(zip(docs, metas))

# Format retrieved chunks neatly with wrapping + numbering
def format_context(chunks_with_meta, width=100):
    formatted = []
    for i, (chunk, meta) in enumerate(chunks_with_meta, start=1):
        ref = f"[{meta.get('subject','Unknown')} | {meta.get('book','Book')}]"
        wrapped = textwrap.fill(chunk.strip(), width=width)
        formatted.append(f"Context {i} {ref}\n{wrapped}")
    return "\n\n".join(formatted)

# 3. Initialize LLM (Groq API)
groq_client = Groq(api_key="your_groq_api_key_here")  # replace with your Groq API key
    
def ask_llm(question, context):
    prompt = f"""
You are a helpful assistant. Use the context provided below to answer the question.
- Always ground your answer in the context. 
- If the context does not fully answer the question, say so and give the closest possible explanation. 
- Provide a clear, concise, and conclusive answer in 3-5 sentences. 
- Structure your response so it: (1) Restates the relevant part of the context, (2) Explains it in simple words, (3) Gives a final conclusion.

Context:
{context}

Question: {question}
Answer:
"""
    completion = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return completion.choices[0].message.content


# 4. Take dynamic user query
if __name__ == "__main__":
    user_query = input("Enter your question: ")

    # 5. Retrieve top documents
    context_docs = retrieve_context(user_query, k=3)

    # 6. Format context + limit size
    context_text = format_context(context_docs, width=100)
    if len(context_text.split()) > 1500:   # ~1500 words ≈ 5000 tokens
        context_text = " ".join(context_text.split()[:1500])

    answer = ask_llm(user_query, context_text)

    # 7. Return results
    print("\n📖 Retrieved Context:\n", context_text)
    print("\n🤖 LLM Answer:\n", answer)
