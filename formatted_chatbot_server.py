import os
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
import pinecone
from openai import OpenAI
import re
import html

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

app = Flask(__name__, static_folder='static')

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
        {"role": "system", "content": f"""Você é um assistente útil que responde perguntas com base nos documentos fornecidos. 
Use apenas as informações dos documentos para responder. Se a informação não estiver nos documentos, diga que não tem essa informação.

Formatação das respostas:
1. Quando listar itens numerados, coloque cada item em uma linha separada, SEM linhas em branco entre os itens.
2. Se um item numerado tiver subitens com bullets, coloque-os logo abaixo do item principal.
3. Use markdown para destacar informações importantes: **negrito**, *itálico*, etc.
4. Separe parágrafos principais com linhas em branco, mas NÃO coloque linhas em branco entre itens numerados.
5. Coloque uma linha em branco apenas antes do último parágrafo conclusivo.

Contexto dos documentos:

{context}"""},
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

# Function to format the response with proper HTML
def format_response_html(text):
    # Escape HTML to prevent XSS
    text = html.escape(text)
    
    # First, identify paragraphs (text blocks separated by double newlines)
    paragraphs = re.split(r'\n\s*\n', text)
    formatted_paragraphs = []
    
    for paragraph in paragraphs:
        # Check if this paragraph contains a numbered list
        if re.search(r'^\d+\.', paragraph, re.MULTILINE):
            # This is a paragraph with a numbered list
            # Process each line
            lines = paragraph.split('\n')
            formatted_lines = []
            
            for line in lines:
                # Check if this is a numbered item
                if re.match(r'^\d+\.', line):
                    # Format numbered item
                    formatted_lines.append(f'<li><strong>{line.split(".", 1)[0]}.</strong>{line.split(".", 1)[1]}</li>')
                elif re.match(r'^\s*[\-\*]', line):
                    # This is a bullet point (sub-item)
                    formatted_lines.append(f'<li class="sub-item">{line.strip()}</li>')
                else:
                    # Regular line within a list
                    formatted_lines.append(line)
            
            # Join the lines and wrap in a list
            formatted_paragraph = '<ul class="numbered-list">' + ''.join(formatted_lines) + '</ul>'
            formatted_paragraphs.append(formatted_paragraph)
        else:
            # Regular paragraph - just wrap in <p> tags
            # Convert markdown bold to HTML
            paragraph = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', paragraph)
            # Convert markdown italic to HTML
            paragraph = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', paragraph)
            # Convert single newlines to <br>
            paragraph = paragraph.replace('\n', '<br>')
            
            formatted_paragraphs.append(f'<p>{paragraph}</p>')
    
    # Join all formatted paragraphs
    return ''.join(formatted_paragraphs)

# HTML template for the main page with embedded chatbot
MAIN_PAGE_HTML = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Câmara Espanhola</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            color: #333;
        }
        header {
            background-color: #c60b1e; /* Spanish flag red */
            color: white;
            padding: 20px 0;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .logo {
            font-size: 2em;
            font-weight: bold;
            margin: 0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .hero {
            background-color: #ffcc00; /* Spanish flag yellow */
            padding: 50px 20px;
            text-align: center;
            margin-bottom: 30px;
        }
        .hero h1 {
            font-size: 2.5em;
            margin-bottom: 20px;
        }
        .hero p {
            font-size: 1.2em;
            max-width: 800px;
            margin: 0 auto;
        }
        .content-section {
            background-color: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h2 {
            color: #c60b1e;
            border-bottom: 2px solid #ffcc00;
            padding-bottom: 10px;
        }
        footer {
            background-color: #333;
            color: white;
            text-align: center;
            padding: 20px 0;
            margin-top: 30px;
        }
        
        /* Chatbot styles */
        .chat-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            z-index: 1000;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            border-radius: 10px;
            overflow: hidden;
        }
        
        .chat-header {
            background-color: #c60b1e;
            color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }
        
        .chat-title {
            font-weight: bold;
        }
        
        .chat-toggle {
            font-weight: bold;
        }
        
        .chat-body {
            height: 400px;
            background-color: white;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: height 0.3s ease;
        }
        
        .chat-body.hidden {
            height: 0;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            display: flex;
            flex-direction: column;
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
        
        /* Improved formatting for lists */
        .assistant-message ul {
            margin: 5px 0;
            padding-left: 10px;
            list-style-type: none;
        }
        
        .assistant-message li {
            margin-bottom: 8px;
            text-indent: -20px;
            padding-left: 20px;
        }
        
        .assistant-message li.sub-item {
            margin-left: 20px;
            margin-bottom: 4px;
            text-indent: -15px;
            padding-left: 15px;
        }
        
        .assistant-message .numbered-list {
            padding-left: 0;
            margin-top: 5px;
            margin-bottom: 5px;
        }
        
        .assistant-message p {
            margin: 8px 0;
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
    <header>
        <div class="logo">Câmara Espanhola</div>
    </header>
    
    <div class="hero">
        <h1>Bem-vindo à Câmara Oficial Espanhola de Comércio no Brasil</h1>
        <p>Facilitando negócios e fortalecendo laços entre Espanha e Brasil desde 1959</p>
    </div>
    
    <div class="container">
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
    
    <footer>
        <p>&copy; 2025 Câmara Oficial Espanhola de Comércio no Brasil. Todos os direitos reservados.</p>
    </footer>

    <!-- Chatbot Widget -->
    <div class="chat-widget">
        <div class="chat-header" id="chatToggle">
            <div class="chat-title">Assistente da Câmara Espanhola</div>
            <div class="chat-toggle">−</div>
        </div>
        <div class="chat-body" id="chatBody">
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
    </div>

    <script>
        // Toggle chat visibility
        document.getElementById('chatToggle').addEventListener('click', function() {
            const chatBody = document.getElementById('chatBody');
            const chatToggle = document.querySelector('.chat-toggle');
            
            chatBody.classList.toggle('hidden');
            
            if (chatBody.classList.contains('hidden')) {
                chatToggle.textContent = '+';
            } else {
                chatToggle.textContent = '−';
            }
        });

        // Chat functionality with real backend
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
            
            if (isUser) {
                // For user messages, just use text
                messageDiv.textContent = content;
            } else {
                // For assistant messages, allow HTML formatting
                messageDiv.innerHTML = content;
            }
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Add to chat history
            chatHistory.push({
                role: isUser ? 'user' : 'assistant',
                content: content
            });
        }
        
        // Function to send a message to the real backend
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
                const response = await fetch('/api/chat', {
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
                
                // Add assistant response to chat with HTML formatting
                addMessage(data.formatted_response, false);
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
    return render_template_string(MAIN_PAGE_HTML)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    chat_history = data.get('history', [])
    
    # Search for relevant documents
    documents = search_documents(user_message)
    
    # Generate response
    response = generate_response(user_message, documents, chat_history)
    
    # Format response with HTML
    formatted_response = format_response_html(response)
    
    return jsonify({
        'response': response,
        'formatted_response': formatted_response
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
