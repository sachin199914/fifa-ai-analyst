import json
import chromadb
from sentence_transformers import SentenceTransformer

# Load chunks
with open('data/chunks.json', 'r') as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} chunks")

# Load embedding model (downloads ~90MB first time, cached after)
print("Loading embedding model... (first time takes 1-2 mins)")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Model loaded")

# Setup ChromaDB (saves to disk, persists between runs)
client = chromadb.PersistentClient(path="data/chromadb")

# Fresh start — delete if exists
try:
    client.delete_collection("fifa_data")
    print("Deleted old collection")
except:
    pass

collection = client.create_collection(
    name="fifa_data",
    metadata={"hnsw:space": "cosine"}
)

# Embed and store in batches of 100
BATCH_SIZE = 100
total = len(chunks)

for i in range(0, total, BATCH_SIZE):
    batch = chunks[i:i + BATCH_SIZE]
    texts = [c['text'] for c in batch]
    ids = [c['id'] for c in batch]
    metadatas = [c['metadata'] for c in batch]

    print(f"Processing batch {i // BATCH_SIZE + 1}/{(total + BATCH_SIZE - 1) // BATCH_SIZE}...")
    embeddings = model.encode(texts, show_progress_bar=False).tolist()

    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )

print(f"\n✅ Done! {collection.count()} chunks stored in ChromaDB")