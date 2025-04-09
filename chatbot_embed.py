import streamlit as st
import os
from dotenv import load_dotenv
import pinecone
from openai import OpenAI

# Load environment variables
load_dotenv()

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

# Set up the Streamlit page
st.set_page_config(
    page_title="Assistente da Câmara Espanhola",
    page_icon="🇪🇸",
    layout="wide"
)

# Custom CSS to make the chatbot fit well in an iframe
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove padding and margin */
    .main .block-container {
        padding: 0;
        max-width: 100%;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background-color: white;
        border-radius: 10px;
        padding: 8px;
        margin-bottom: 8px;
    }
    
    /* User message */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #e1f5fe;
    }
    
    /* Assistant message */
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #f5f5f5;
    }
    
    /* Chat input */
    .stChatInputContainer {
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o assistente da Câmara Espanhola. Como posso ajudar você hoje?"}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Digite sua mensagem..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Search for relevant documents
    with st.spinner("Buscando informações..."):
        documents = search_documents(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        # Extract chat history for context (last 6 messages)
        chat_history = [{"role": msg["role"], "content": msg["content"]} 
                       for msg in st.session_state.messages[-6:] if msg["role"] != "assistant"]
        
        # Generate and display response
        message_placeholder = st.empty()
        with st.spinner("Gerando resposta..."):
            response = generate_response(prompt, documents, chat_history)
        message_placeholder.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
