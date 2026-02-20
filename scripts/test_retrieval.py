import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="data/chromadb")
collection = client.get_collection("fifa_data")

print(f"Total chunks in DB: {collection.count()}\n")

test_queries = [
    "Who won the 2014 World Cup?",
    "Brazil World Cup history",
    "France vs Croatia final"
]

for query in test_queries:
    embedding = model.encode(query).tolist()
    results = collection.query(query_embeddings=[embedding], n_results=2)
    
    print(f"Query: {query}")
    print(f"Top result: {results['documents'][0][0][:200]}...")
    print("-" * 60)