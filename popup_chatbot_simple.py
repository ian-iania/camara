import streamlit as st
import os
from dotenv import load_dotenv
import pinecone
from openai import OpenAI
import time

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

# Custom CSS for the pop-up chatbot
def get_custom_css():
    return """
    <style>
        /* Main page styles */
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        
        /* Hide Streamlit components */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Chatbot container */
        .chat-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            max-height: 500px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            z-index: 1000;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        /* Chat header */
        .chat-header {
            background-color: #c60b1e;
            color: white;
            padding: 15px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chat-title {
            font-size: 16px;
        }
        
        .chat-toggle {
            cursor: pointer;
            font-size: 16px;
        }
        
        /* Minimized state */
        .chat-widget.minimized {
            max-height: 50px;
        }
        
        .chat-content {
            padding: 15px;
            overflow-y: auto;
            max-height: 400px;
        }
        
        /* Streamlit element customization */
        .stTextInput > div > div > input {
            border-radius: 20px;
        }
        
        .stButton > button {
            background-color: #c60b1e;
            color: white;
            border-radius: 20px;
            border: none;
        }
        
        /* Main content area */
        .main-content {
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background-color: #c60b1e;
            color: white;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .content-section {
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        h1, h2 {
            color: #c60b1e;
        }
    </style>
    """

# JavaScript to control the chatbot behavior
def get_custom_js():
    return """
    <script>
        // Function to toggle the chatbot visibility
        function toggleChat() {
            const chatWidget = document.querySelector('.chat-widget');
            chatWidget.classList.toggle('minimized');
            
            const toggleButton = document.querySelector('.chat-toggle');
            if (chatWidget.classList.contains('minimized')) {
                toggleButton.innerHTML = '+';
            } else {
                toggleButton.innerHTML = '−';
            }
        }
        
        // Add event listener when the document is loaded
        document.addEventListener('DOMContentLoaded', function() {
            // Find the toggle button and add click event
            const toggleButton = document.querySelector('.chat-toggle');
            if (toggleButton) {
                toggleButton.addEventListener('click', toggleChat);
            }
        });
    </script>
    """

# HTML for the main page content
def get_main_content_html():
    return """
    <div class="header">
        <h1>Câmara Oficial Espanhola de Comércio no Brasil</h1>
        <p>Facilitando negócios e fortalecendo laços entre Espanha e Brasil desde 1959</p>
    </div>
    
    <div class="main-content">
        <div class="content-section">
            <h2>Sobre a Câmara</h2>
            <p>A Câmara Oficial Espanhola de Comércio no Brasil é uma instituição sem fins lucrativos que tem como objetivo fomentar as relações comerciais entre Espanha e Brasil, oferecendo suporte às empresas espanholas no mercado brasileiro e às empresas brasileiras interessadas no mercado espanhol.</p>
            <p>Fundada em 1959, a Câmara representa um importante canal de comunicação e intercâmbio entre os dois países, promovendo eventos, missões comerciais, rodadas de negócios e oferecendo serviços de consultoria especializada.</p>
        </div>
        
        <div class="content-section">
            <h2>Nossos Serviços</h2>
            <p>Oferecemos uma ampla gama de serviços para empresas espanholas e brasileiras:</p>
            <ul>
                <li>Assessoria em internacionalização</li>
                <li>Estudos de mercado</li>
                <li>Missões comerciais</li>
                <li>Rodadas de negócios</li>
                <li>Eventos de networking</li>
                <li>Formação empresarial</li>
                <li>Consultoria jurídica e fiscal</li>
            </ul>
        </div>
        
        <div class="content-section">
            <h2>Eventos</h2>
            <p>Acompanhe nossos próximos eventos e participe das oportunidades de networking e negócios:</p>
            <ul>
                <li>Seminário sobre Oportunidades de Investimento - 15/05/2025</li>
                <li>Rodada de Negócios Setor Tecnológico - 22/06/2025</li>
                <li>Missão Comercial Brasil-Espanha - 10/07/2025</li>
                <li>Jantar de Confraternização Anual - 25/11/2025</li>
            </ul>
        </div>
    </div>
    """

# Main function
def main():
    # Set page config
    st.set_page_config(
        page_title="Câmara Espanhola",
        page_icon="🇪🇸",
        layout="wide"
    )
    
    # Apply custom CSS and JavaScript
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    st.markdown(get_custom_js(), unsafe_allow_html=True)
    
    # Display the main content
    st.markdown(get_main_content_html(), unsafe_allow_html=True)
    
    # Create the chat widget container
    chat_widget_html = """
    <div class="chat-widget">
        <div class="chat-header">
            <div class="chat-title">Assistente da Câmara Espanhola</div>
            <div class="chat-toggle">−</div>
        </div>
        <div class="chat-content">
            <!-- Streamlit chat components will be inserted here -->
        </div>
    </div>
    """
    st.markdown(chat_widget_html, unsafe_allow_html=True)
    
    # Create a container for the chat content
    with st.container():
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
            
            # Force a rerun to update the UI
            st.experimental_rerun()

if __name__ == "__main__":
    main()
