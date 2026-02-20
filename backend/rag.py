import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv('../.env')

print("Loading models...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path="../data/chromadb")
collection = chroma_client.get_collection("fifa_data")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print(f"✅ Ready — {collection.count()} chunks loaded")


def query_fifa(question: str, n_results: int = 5) -> dict:

    # Step 1: Embed the question
    question_embedding = embedding_model.encode(question).tolist()

    # Step 2: Retrieve relevant chunks from ChromaDB
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=n_results
    )

    retrieved_docs = results['documents'][0]
    retrieved_metadata = results['metadatas'][0]

    # Step 3: Build context string
    context = "\n\n---\n\n".join(retrieved_docs)

    # Step 4: Call Groq LLM with context
    prompt = f"""You are a FIFA World Cup expert analyst.
Answer the user's question using ONLY the context provided below.
If the context doesn't contain enough information, say so honestly.
Do not make up statistics or results.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": retrieved_metadata
    }


# Test when run directly
if __name__ == "__main__":
    questions = [
        "Who won the 2014 FIFA World Cup?",
        "How many World Cups has Brazil won?",
        "Who won the 2022 World Cup final and what was the score?"
    ]

    for q in questions:
        print(f"\n❓ {q}")
        result = query_fifa(q)
        print(f"🤖 {result['answer']}")
        print("-" * 60)