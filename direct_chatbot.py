import os
from flask import Flask, request, jsonify, render_template_string
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

app = Flask(__name__)

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

# HTML template for the chatbot interface
CHATBOT_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Assistente da Câmara Espanhola</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #ffffff;
            color: #333333;
        }
        .chat-container {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            background-color: #ffffff;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
            word-wrap: break-word;
        }
        .user-message {
            background-color: #e1f5fe;
            color: #0c344b;
            align-self: flex-end;
            margin-left: auto;
        }
        .assistant-message {
            background-color: #f5f5f5;
            color: #333333;
            align-self: flex-start;
        }
        .chat-input-container {
            display: flex;
            padding: 10px;
            background-color: #ffffff;
            border-top: 1px solid #e0e0e0;
        }
        .chat-input {
            flex: 1;
            padding: 10px;
            border: 1px solid #cccccc;
            border-radius: 20px;
            font-size: 14px;
            color: #333333;
        }
        .chat-submit {
            margin-left: 10px;
            padding: 10px 15px;
            background-color: #c60b1e;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 10px;
            color: #666666;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-messages" id="chatMessages">
            <div class="message assistant-message">
                Olá! Sou o assistente da Câmara Espanhola. Como posso ajudar você hoje?
            </div>
        </div>
        <div class="loading" id="loading">Buscando informações...</div>
        <div class="chat-input-container">
            <input type="text" class="chat-input" id="userInput" placeholder="Digite sua mensagem..." autofocus>
            <button class="chat-submit" id="sendButton">Enviar</button>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        const userInput = document.getElementById('userInput');
        const sendButton = document.getElementById('sendButton');
        const loading = document.getElementById('loading');
        
        // Store chat history
        let chatHistory = [];
        
        // Function to add a message to the chat
        function addMessage(content, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = isUser ? 'message user-message' : 'message assistant-message';
            messageDiv.textContent = content;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Add to chat history
            chatHistory.push({
                role: isUser ? 'user' : 'assistant',
                content: content
            });
        }
        
        // Function to send a message
        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;
            
            // Add user message to chat
            addMessage(message, true);
            userInput.value = '';
            
            // Show loading indicator
            loading.style.display = 'block';
            
            try {
                // Send request to the server
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        history: chatHistory.slice(-6) // Send last 6 messages for context
                    })
                });
                
                const data = await response.json();
                
                // Add assistant response to chat
                addMessage(data.response, false);
            } catch (error) {
                console.error('Error:', error);
                addMessage('Desculpe, ocorreu um erro ao processar sua mensagem.', false);
            } finally {
                // Hide loading indicator
                loading.style.display = 'none';
            }
        }
        
        // Event listeners
        sendButton.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(CHATBOT_HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    chat_history = data.get('history', [])
    
    # Search for relevant documents
    documents = search_documents(user_message)
    
    # Generate response
    response = generate_response(user_message, documents, chat_history)
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8502, debug=True)
