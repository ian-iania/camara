import os
from flask import Flask, request, jsonify
from flask_cors import CORS
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
ENVIRONMENT = os.getenv("ENVIRONMENT")

# Initialize the Pinecone client
pinecone.init(api_key=PINECONE_API_KEY, environment=ENVIRONMENT, default_index=INDEX_NAME)
index = pinecone.Index(INDEX_NAME)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
    # First, process markdown formatting
    # Convert markdown bold to HTML
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Convert markdown italic to HTML
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    
    # Now identify paragraphs (text blocks separated by double newlines)
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
                    num, content = line.split(".", 1)
                    formatted_lines.append(f'<li><strong>{num}.</strong>{content}</li>')
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
            # Regular paragraph - convert newlines to <br>
            paragraph = paragraph.replace('\n', '<br>')
            formatted_paragraphs.append(f'<p>{paragraph}</p>')
    
    # Join all formatted paragraphs
    formatted_html = ''.join(formatted_paragraphs)
    
    # Escape any remaining HTML except our tags
    safe_html = formatted_html
    
    return safe_html

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

@app.route('/', methods=['GET'])
def home():
    return "Câmara Espanhola Chatbot API is running!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
