import streamlit as st
import os
from dotenv import load_dotenv
import pinecone
from openai import OpenAI
import time
import streamlit.components.v1 as components

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

# Load HTML template
def read_html_template():
    with open('templates/index.html', 'r', encoding='utf-8') as file:
        return file.read()

# Custom CSS for the pop-up chatbot
def get_chatbot_css():
    return """
    <style>
        /* Chatbot container */
        .chat-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            height: 500px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            z-index: 1000;
            transition: all 0.3s ease;
        }
        
        /* Chat header */
        .chat-header {
            background-color: #c60b1e;
            color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chat-title {
            font-weight: bold;
            font-size: 16px;
        }
        
        .chat-controls {
            display: flex;
            gap: 10px;
        }
        
        .chat-control-btn {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            font-size: 16px;
        }
        
        /* Chat messages area */
        .chat-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .message {
            max-width: 80%;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 5px;
        }
        
        .user-message {
            align-self: flex-end;
            background-color: #e1f5fe;
        }
        
        .bot-message {
            align-self: flex-start;
            background-color: #f5f5f5;
        }
        
        /* Chat input area */
        .chat-input-container {
            padding: 15px;
            border-top: 1px solid #eee;
            display: flex;
        }
        
        .chat-input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 20px;
            outline: none;
        }
        
        .chat-send-btn {
            background-color: #c60b1e;
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            margin-left: 10px;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        /* Minimized state */
        .chat-container.minimized {
            height: 60px;
            width: 60px;
            border-radius: 50%;
            overflow: hidden;
        }
        
        .chat-container.minimized .chat-header {
            height: 100%;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chat-container.minimized .chat-title,
        .chat-container.minimized .chat-messages,
        .chat-container.minimized .chat-input-container {
            display: none;
        }
        
        /* Chat toggle button for minimized state */
        .chat-toggle {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            height: 100%;
            color: white;
            font-size: 24px;
            cursor: pointer;
        }
    </style>
    """

# JavaScript for the chatbot functionality
def get_chatbot_js():
    return """
    <script>
        // Initialize chat state
        let chatState = {
            minimized: false,
            messages: []
        };
        
        // Function to toggle chat minimization
        function toggleChat() {
            const chatContainer = document.querySelector('.chat-container');
            chatState.minimized = !chatState.minimized;
            
            if (chatState.minimized) {
                chatContainer.classList.add('minimized');
            } else {
                chatContainer.classList.remove('minimized');
            }
        }
        
        // Function to add a message to the chat
        function addMessage(text, isUser = false) {
            const messagesContainer = document.querySelector('.chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message');
            messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
            messageDiv.textContent = text;
            messagesContainer.appendChild(messageDiv);
            
            // Save to state
            chatState.messages.push({
                text: text,
                isUser: isUser
            });
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            
            // If this is a user message, send to Streamlit
            if (isUser) {
                // Use Streamlit's communication mechanism
                window.parent.postMessage({
                    type: "streamlit:setComponentValue",
                    value: {
                        message: text,
                        timestamp: Date.now()
                    }
                }, "*");
            }
        }
        
        // Function to handle sending a message
        function sendMessage() {
            const inputElement = document.querySelector('.chat-input');
            const message = inputElement.value.trim();
            
            if (message) {
                addMessage(message, true);
                inputElement.value = '';
            }
        }
        
        // Function to receive messages from Streamlit
        function receiveMessage(data) {
            if (data && data.message) {
                addMessage(data.message, false);
            }
        }
        
        // Add event listener for the Streamlit message
        window.addEventListener("message", function(event) {
            if (event.data.type === "streamlit:render") {
                const data = event.data.args.data;
                if (data && data.botMessage) {
                    receiveMessage(data);
                }
            }
        });
        
        // Initialize with a welcome message
        document.addEventListener('DOMContentLoaded', function() {
            addMessage("Olá! Sou o assistente da Câmara Espanhola. Como posso ajudar você hoje?");
            
            // Set up event listeners
            document.querySelector('.chat-send-btn').addEventListener('click', sendMessage);
            document.querySelector('.chat-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            document.querySelector('.chat-minimize-btn').addEventListener('click', toggleChat);
            document.querySelector('.chat-toggle').addEventListener('click', toggleChat);
        });
    </script>
    """

# HTML for the chatbot UI
def get_chatbot_html():
    return """
    <div class="chat-container">
        <div class="chat-header">
            <div class="chat-title">Assistente da Câmara Espanhola</div>
            <div class="chat-controls">
                <button class="chat-control-btn chat-minimize-btn">−</button>
            </div>
            <div class="chat-toggle">💬</div>
        </div>
        <div class="chat-messages">
            <!-- Messages will be added here dynamically -->
        </div>
        <div class="chat-input-container">
            <input type="text" class="chat-input" placeholder="Digite sua mensagem...">
            <button class="chat-send-btn">➤</button>
        </div>
    </div>
    """

# Custom component for the chatbot
def chatbot_component():
    # Create a unique key for the component
    key = "chatbot_" + str(int(time.time()))
    
    # Combine all HTML, CSS, and JS
    component_html = f"""
    {get_chatbot_css()}
    {get_chatbot_html()}
    {get_chatbot_js()}
    """
    
    # Render the component
    component_value = components.html(
        component_html,
        height=0,  # Set to 0 to make it not take up space in the Streamlit app
        key=key
    )
    
    return component_value

# Main function to run the app
def main():
    # Set page config to wide mode and remove the Streamlit branding
    st.set_page_config(
        page_title="Câmara Espanhola",
        page_icon="🇪🇸",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Hide Streamlit elements
    hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stApp {
            margin: 0;
            padding: 0;
        }
        header {display: none !important;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Load the HTML template
    html_content = read_html_template()
    
    # Display the HTML content
    st.components.v1.html(html_content, height=2000, scrolling=True)
    
    # Initialize session state for chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Render the chatbot component
    chatbot_value = chatbot_component()
    
    # Process user messages
    if chatbot_value and 'message' in chatbot_value:
        user_message = chatbot_value['message']
        
        # Add to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        
        # Search for relevant documents
        documents = search_documents(user_message)
        
        # Generate response
        chat_history = [{"role": msg["role"], "content": msg["content"]} 
                       for msg in st.session_state.chat_history[-6:]]
        
        bot_response = generate_response(user_message, documents, chat_history)
        
        # Add bot response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
        
        # Send the response back to the component
        st.components.v1.html(
            f"""
            <script>
                window.parent.postMessage({{
                    type: "streamlit:setComponentValue",
                    value: {{ botMessage: "{bot_response.replace('"', '\\"')}" }}
                }}, "*");
            </script>
            """,
            height=0
        )

if __name__ == "__main__":
    main()
