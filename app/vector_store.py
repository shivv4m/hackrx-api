import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

if not all([PINECONE_API_KEY, PINECONE_INDEX_NAME]):
    raise EnvironmentError("Missing environment variables.")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Check if the index exists
if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    raise ValueError(f"Pinecone index '{PINECONE_INDEX_NAME}' does not exist.")

# Connect to the index
index = pc.Index(PINECONE_INDEX_NAME)

# Load SentenceTransformer model locally
model = SentenceTransformer("paraphrase-albert-small-v2")  # ~45MB
  # 384-dimensional embeddings

def get_embedding(text: str) -> list:
    embedding = model.encode(text).tolist()
    return embedding

def upsert_chunks_to_pinecone(chunks: list, namespace: str = "default"):
    vectors = []
    for i, chunk in enumerate(chunks):
        chunk = chunk.strip()
        if chunk:
            vector_id = f"{namespace}-chunk-{i}"
            embedding = get_embedding(chunk)
            vectors.append((vector_id, embedding, {"text": chunk}))
    if vectors:
        index.upsert(vectors=vectors, namespace=namespace)

def query_pinecone(question: str, namespace: str = "default"):
    embedding = get_embedding(question)
    results = index.query(vector=embedding, top_k=3, include_metadata=True, namespace=namespace)
    return [match['metadata']['text'] for match in results['matches']]
