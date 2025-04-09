import os
import re
import unicodedata
from dotenv import load_dotenv
import pinecone
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm
import time

# Load environment variables
load_dotenv()

# Initialize Pinecone
PINECONE_API_KEY = "pcsk_5sEFet_FzLpiV1UZt6so4oXhKkLR4ZwRaUzv1sPhSQLUZFw9RVFaBxZcWrFaB1buj48jYh"
PINECONE_ENVIRONMENT = "us-east-1"  # This is based on the image showing AWS us-east-1 region

# Initialize Pinecone with the new API format
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)

# Check if the index exists, if not create it
INDEX_NAME = "pdf"
DIMENSION = 3072  # Updated to match the existing index dimension

# List all indexes
existing_indexes = [index.name for index in pc.list_indexes()]

if INDEX_NAME not in existing_indexes:
    # Create a new index
    pc.create_index(
        name=INDEX_NAME,
        dimension=DIMENSION,
        metric="cosine"
    )
    print(f"Created new Pinecone index: {INDEX_NAME}")
else:
    print(f"Using existing Pinecone index: {INDEX_NAME}")

# Connect to the index
index = pc.Index(INDEX_NAME)

# Initialize OpenAI embeddings with the correct model for 3072 dimensions
# We need to use a model that produces 3072-dimensional embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Function to normalize text to ASCII
def normalize_to_ascii(text):
    # Normalize to NFD form and remove diacritics
    normalized = unicodedata.normalize('NFD', text)
    ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
    # Replace any remaining non-alphanumeric characters with underscores
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', ascii_text)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    print(f"Extracting text from {pdf_path}...")
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Function to split text into chunks
def split_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(text)

# Function to create embeddings and upload to Pinecone
def upload_to_pinecone(chunks, pdf_name):
    # Normalize the PDF name to ASCII for use in IDs
    ascii_pdf_name = normalize_to_ascii(pdf_name)
    print(f"Creating embeddings and uploading chunks from {pdf_name} to Pinecone...")
    batch_size = 100
    
    for i in tqdm(range(0, len(chunks), batch_size)):
        batch_chunks = chunks[i:i+batch_size]
        
        # Create embeddings for the batch
        batch_embeddings = embeddings.embed_documents(batch_chunks)
        
        # Prepare vectors for Pinecone
        vectors = []
        for j, (chunk, embedding) in enumerate(zip(batch_chunks, batch_embeddings)):
            vector_id = f"{ascii_pdf_name}_{i+j}"
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "text": chunk,
                    "source": pdf_name
                }
            })
        
        # Upsert to Pinecone
        index.upsert(vectors=vectors)
        
        # Sleep to avoid rate limiting
        time.sleep(0.5)

# Main function
def main():
    pdf_folder = "PDFs"
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        
        # Split text into chunks
        chunks = split_text(text)
        print(f"Split {pdf_file} into {len(chunks)} chunks")
        
        # Upload chunks to Pinecone
        upload_to_pinecone(chunks, pdf_file)
        
        print(f"Completed processing {pdf_file}")
    
    # Get and print index stats
    stats = index.describe_index_stats()
    print(f"Pinecone index stats: {stats}")

if __name__ == "__main__":
    main()
