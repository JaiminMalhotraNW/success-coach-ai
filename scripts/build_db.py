import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def build_database():
    # 1. Load the document
    print("Loading setup_guide.md...")
    loader = TextLoader("data/setup_guide.md")
    documents = loader.load()

    # 2. Split the document into bite-sized chunks
    print("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # 500 characters per chunk
        chunk_overlap=50 # 50 characters of overlap so sentences aren't cut in half
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    # 3. Create embeddings (Translating text to numbers)
    # We use a free, local model from HuggingFace so you don't need API keys!
    print("Downloading embedding model (this might take a minute on the first run)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. Save everything to ChromaDB
    print("Saving to ChromaDB...")
    db_path = "data/chroma_db"
    db = Chroma.from_documents(chunks, embeddings, persist_directory=db_path)
    
    print(f"Success! Database built at {db_path}")

if __name__ == "__main__":
    build_database()