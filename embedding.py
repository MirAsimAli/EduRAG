import os
import chromadb
from sentence_transformers import SentenceTransformer

# Initialize HF model and Chroma
model = SentenceTransformer('all-MiniLM-L6-v2')  # Hugging Face embeddings
chroma_client = chromadb.PersistentClient(path="./chroma_db")  # stored locally
collection = chroma_client.get_or_create_collection("books_embeddings")

# Function to parse filename
def parse_filename(filename):
    name = filename.replace(".txt", "")
    if "_" in name:  # case: subject_book
        subject, book = name.split("_", 1)
    else:  # case: mathematics1, mathematics2
        subject = ''.join([c for c in name if not c.isdigit()])
        book = ''.join([c for c in name if c.isdigit()])
        if book == "":  # if no digit, just mark as book1
            book = "1"
    return subject.lower(), book.lower()

# Function to embed and store text
def embed_and_store(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    subject, book = parse_filename(os.path.basename(file_path))

    # Create embeddings using HF model
    embedding = model.encode(text)

    # Store in Chroma with metadata
    collection.add(
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"subject": subject, "book": book}],
        ids=[os.path.basename(file_path)]
    )
    print(f"Stored: {file_path} → subject={subject}, book={book}")

# Main pipeline
def process_folder(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            embed_and_store(os.path.join(folder_path, file))

# Run
process_folder("")

