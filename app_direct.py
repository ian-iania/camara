import streamlit as st
import os
from dotenv import load_dotenv
import pinecone
from openai import OpenAI
import time

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Chatbot Câmara",
    page_icon="📚",
    layout="centered"
)

# Initialize API keys
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = "pdf"

# Initialize the Pinecone client
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Function to get embeddings from OpenAI
def get_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-large"
    )
    return response.data[0].embedding

# Function to search Pinecone and get relevant documents
def search_documents(query, top_k=5):
    # Generate embedding for the query
    query_embedding = get_embedding(query)
    
    # Search Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    # Extract and return the relevant documents
    documents = []
    for match in results['matches']:
        documents.append({
            'text': match['metadata']['text'],
            'source': match['metadata']['source'],
            'score': match['score']
        })
    
    return documents

# Function to generate response using OpenAI
def generate_response(query, documents, chat_history=None):
    if chat_history is None:
        chat_history = []
    
    # Prepare context from retrieved documents
    context = "\n\n".join([f"Document from {doc['source']} (relevance: {doc['score']:.2f}):\n{doc['text']}" for doc in documents])
    
    # Prepare messages for the chat
    messages = [
        {"role": "system", "content": f"Você é um assistente útil que responde perguntas com base nos documentos fornecidos. Use apenas as informações dos documentos para responder. Se a informação não estiver nos documentos, diga que não tem essa informação. Contexto dos documentos:\n\n{context}"},
    ]
    
    # Add chat history
    for message in chat_history:
        messages.append(message)
    
    # Add the current query
    messages.append({"role": "user", "content": query})
    
    # Generate response
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.2,
    )
    
    return response.choices[0].message.content

# App title and description
st.title("📚 Chatbot Câmara")
st.markdown("""
Este chatbot responde perguntas com base nos documentos da Câmara que foram indexados.
Faça perguntas sobre os guias de negócios, guia institucional, informe anual ou internacionalização.
""")

# Initialize session state for chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Faça sua pergunta aqui..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Search for relevant documents
        with st.spinner("Buscando documentos relevantes..."):
            documents = search_documents(prompt)
        
        # Generate response
        with st.spinner("Gerando resposta..."):
            # Extract chat history for context
            chat_history = [{"role": msg["role"], "content": msg["content"]} 
                           for msg in st.session_state.messages[-4:] if msg["role"] != "assistant"]
            
            answer = generate_response(prompt, documents, chat_history)
        
        # Display the response
        message_placeholder.markdown(answer)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": answer})

# Sidebar with information
with st.sidebar:
    st.title("Sobre")
    st.markdown("""
    Este chatbot utiliza:
    - Pinecone para armazenar embeddings dos documentos
    - OpenAI para gerar embeddings e respostas
    
    Os documentos indexados incluem:
    - Guias de negócios
    - Guia institucional
    - Informe anual
    - Documentos de internacionalização
    """)
    
    # Add a reset button to clear the conversation
    if st.button("Reiniciar Conversa"):
        st.session_state.messages = []
        st.experimental_rerun()
