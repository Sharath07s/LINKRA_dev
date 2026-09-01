import os
import sys
from glob import glob
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.ai.rag.vector_search import VectorStore

def ingest_pdfs(directory_path: str):
    """
    Scans a directory for PDF files, parses them, splits them into chunks,
    and inserts the chunks into the VectorStore.
    """
    print(f"Scanning directory: {directory_path} for PDFs...")
    pdf_files = glob(os.path.join(directory_path, "*.pdf"))
    
    if not pdf_files:
        print("No PDF files found.")
        return

    from app.core.config import settings
    vector_store = VectorStore(connection_string=settings.SQLALCHEMY_DATABASE_URI)
    
    # We use a character text splitter.
    # Chunk size of 1000 with 200 overlap is standard for LLM RAG pipelines.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    
    total_chunks = 0
    
    for file_path in pdf_files:
        print(f"Processing {file_path}...")
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Extract basic metadata
            filename = Path(file_path).name
            source_id = filename.replace(".pdf", "")
            
            # Split documents into chunks
            chunks = text_splitter.split_documents(documents)
            
            for i, chunk in enumerate(chunks):
                metadata = chunk.metadata
                metadata["chunk_index"] = i
                metadata["source"] = filename
                
                success = vector_store.index_document(
                    source_id=source_id,
                    text=chunk.page_content,
                    metadata=metadata
                )
                if success:
                    total_chunks += 1
                    
        except Exception as e:
            print(f"Error parsing PDF {file_path}: {e}")
            
    print(f"Ingestion complete. Successfully inserted {total_chunks} chunks.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest FIR PDF documents into pgvector.")
    parser.add_argument("--dir", type=str, default="./data/pdfs", help="Directory containing PDF files")
    args = parser.parse_args()
    
    # Make sure the directory exists
    os.makedirs(args.dir, exist_ok=True)
    
    ingest_pdfs(args.dir)
