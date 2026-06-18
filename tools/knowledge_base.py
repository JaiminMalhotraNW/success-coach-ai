from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def search_knowledge_base(query: str) -> str:
    """
    Searches the official product knowledge base.
    Use this tool whenever a student asks about how the portal works, 
    features like My Journey, Course Exams, LastMinute Pro, Bookmarks, or certificates.
    """
    try:
        # 1. Load the same embedding model we used to build the DB
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # 2. Connect to our Chroma database
        db_path = "data/chroma_db"
        db = Chroma(persist_directory=db_path, embedding_function=embeddings)
        
        # 3. Search for the top 3 most relevant paragraphs
        results = db.similarity_search(query, k=3)
        
        if not results:
            return "No information found in the knowledge base for this query."
            
        # 4. Stitch the paragraphs together and return them to the AI
        combined_text = "Here is the relevant information from the knowledge base:\n\n"
        for doc in results:
            combined_text += f"- {doc.page_content}\n\n"
            
        return combined_text
        
    except Exception as e:
        return f"Error accessing the knowledge base: {str(e)}"