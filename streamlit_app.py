import streamlit as st
import os
from dotenv import load_dotenv
import pinecone
from openai import OpenAI
import httpx

# Configuração da página Streamlit
st.set_page_config(
    page_title="Assistente da Câmara Espanhola",
    page_icon="🇪🇸",
    layout="wide"
)

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar API keys
PINECONE_API_KEY = st.secrets.get("PINECONE_API_KEY", os.getenv("PINECONE_API_KEY"))
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
PINECONE_ENVIRONMENT = st.secrets.get("PINECONE_ENVIRONMENT", os.getenv("PINECONE_ENVIRONMENT", "us-east-1"))
INDEX_NAME = "pdf"

# Verificar se as chaves de API estão definidas
if not PINECONE_API_KEY:
    st.error("PINECONE_API_KEY não está definida. Configure esta variável no Streamlit Cloud.")
    st.stop()

if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY não está definida. Configure esta variável no Streamlit Cloud.")
    st.stop()

# Inicializar o cliente Pinecone com tratamento de erros
try:
    # Inicializar o cliente Pinecone
    pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
    
    # Verificar se o índice existe
    indexes = [index.name for index in pc.list_indexes()]
    if INDEX_NAME not in indexes:
        st.error(f"Índice '{INDEX_NAME}' não encontrado no Pinecone. Verifique o nome do índice ou crie-o primeiro.")
        st.stop()
    
    # Conectar ao índice
    index = pc.Index(INDEX_NAME)
    
except Exception as e:
    st.error(f"Erro ao inicializar o Pinecone: {str(e)}")
    st.write("Detalhes técnicos:")
    st.exception(e)
    st.stop()

# Inicializar o cliente OpenAI com tratamento de erros
try:
    # Tentar inicializar normalmente
    client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    try:
        # Tentar inicializar com cliente HTTP personalizado
        http_client = httpx.Client(
            proxies=None,  # Desabilitar proxies
            transport=httpx.HTTPTransport(local_address="0.0.0.0")
        )
        client = OpenAI(api_key=OPENAI_API_KEY, http_client=http_client)
    except Exception as e:
        st.error(f"Erro ao inicializar o OpenAI: {str(e)}")
        st.write("Detalhes técnicos:")
        st.exception(e)
        st.stop()

# Função para obter embeddings do OpenAI
def get_embedding(text):
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-large"
        )
        return response.data[0].embedding
    except Exception as e:
        st.error(f"Erro ao gerar embedding: {str(e)}")
        return None

# Função para buscar documentos no Pinecone
def search_documents(query, top_k=5):
    # Gerar embedding para a consulta
    query_embedding = get_embedding(query)
    
    if not query_embedding:
        return []
    
    try:
        # Buscar no Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Extrair e retornar os documentos relevantes
        documents = []
        for match in results['matches']:
            documents.append({
                'text': match['metadata']['text'],
                'source': match['metadata']['source'],
                'score': match['score']
            })
        
        return documents
    except Exception as e:
        st.error(f"Erro ao buscar documentos: {str(e)}")
        return []

# Função para gerar resposta usando OpenAI
def generate_response(query, documents, chat_history=None):
    if chat_history is None:
        chat_history = []
    
    if not documents:
        return "Desculpe, não consegui encontrar informações relevantes para responder à sua pergunta. Poderia reformular ou fazer outra pergunta?"
    
    # Preparar contexto a partir dos documentos recuperados
    context = "\n\n".join([f"Documento de {doc['source']} (relevância: {doc['score']:.2f}):\n{doc['text']}" for doc in documents])
    
    # Preparar mensagens para o chat
    messages = [
        {"role": "system", "content": f"Você é um assistente útil da Câmara Oficial Espanhola de Comércio no Brasil. Responda perguntas com base nos documentos fornecidos. Use apenas as informações dos documentos para responder. Se a informação não estiver nos documentos, diga que não tem essa informação. Contexto dos documentos:\n\n{context}"},
    ]
    
    # Adicionar histórico do chat
    for message in chat_history:
        messages.append(message)
    
    # Adicionar a consulta atual
    messages.append({"role": "user", "content": query})
    
    try:
        # Gerar resposta
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.2,
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao gerar resposta: {str(e)}")
        return "Desculpe, ocorreu um erro ao gerar a resposta. Por favor, tente novamente mais tarde."

# CSS personalizado para melhorar a aparência
st.markdown("""
<style>
    /* Respeitar preferência de tema do sistema */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background-color: #1e1e1e;
            color: #f0f0f0;
        }
        
        /* Estilo para mensagens do chat no modo escuro */
        .stChatMessage {
            background-color: #2d2d2d;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #444;
        }
        
        /* Mensagem do usuário no modo escuro */
        .stChatMessage[data-testid="stChatMessageUser"] {
            background-color: #0e4a6b;
            color: #e1f5fe;
        }
        
        /* Mensagem do assistente no modo escuro */
        .stChatMessage[data-testid="stChatMessageAssistant"] {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        
        /* Cabeçalho no modo escuro */
        .main-header {
            background-color: #c60b1e;
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin-bottom: 20px;
            text-align: center;
        }
        
        /* Rodapé no modo escuro */
        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 0.8em;
            color: #aaa;
        }
        
        /* Ajuste para o input do chat no modo escuro */
        .stChatInputContainer textarea {
            color: #f0f0f0;
            background-color: #333;
            border: 1px solid #555;
        }
        
        /* Ajuste para links no modo escuro */
        a {
            color: #4da6ff !important;
        }
        
        /* Ajuste para texto dentro de mensagens do chat no modo escuro */
        .stChatMessage[data-testid="stChatMessageAssistant"] p,
        .stChatMessage[data-testid="stChatMessageAssistant"] li,
        .stChatMessage[data-testid="stChatMessageAssistant"] h1,
        .stChatMessage[data-testid="stChatMessageAssistant"] h2,
        .stChatMessage[data-testid="stChatMessageAssistant"] h3 {
            color: #e0e0e0 !important;
        }
        
        .stChatMessage[data-testid="stChatMessageUser"] p,
        .stChatMessage[data-testid="stChatMessageUser"] li,
        .stChatMessage[data-testid="stChatMessageUser"] h1,
        .stChatMessage[data-testid="stChatMessageUser"] h2,
        .stChatMessage[data-testid="stChatMessageUser"] h3 {
            color: #e1f5fe !important;
        }
        
        /* Ajuste para links dentro de mensagens no modo escuro */
        .stChatMessage[data-testid="stChatMessageAssistant"] a {
            color: #4da6ff !important;
        }
        
        .stChatMessage[data-testid="stChatMessageUser"] a {
            color: #8ecdf9 !important;
        }
    }
    
    @media (prefers-color-scheme: light) {
        /* Estilo para mensagens do chat no modo claro */
        .stChatMessage {
            background-color: white;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #e0e0e0;
        }
        
        /* Mensagem do usuário no modo claro */
        .stChatMessage[data-testid="stChatMessageUser"] {
            background-color: #e1f5fe;
            color: #0c344b;
        }
        
        /* Mensagem do assistente no modo claro */
        .stChatMessage[data-testid="stChatMessageAssistant"] {
            background-color: #f5f5f5;
            color: #333333;
        }
        
        /* Cabeçalho no modo claro */
        .main-header {
            background-color: #c60b1e;
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin-bottom: 20px;
            text-align: center;
        }
        
        /* Rodapé no modo claro */
        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 0.8em;
            color: #666;
        }
        
        /* Ajuste para o input do chat no modo claro */
        .stChatInputContainer textarea {
            color: #333333;
            background-color: #ffffff;
            border: 1px solid #ddd;
        }
        
        /* Ajuste para links no modo claro */
        a {
            color: #0066cc !important;
        }
        
        /* Ajuste para texto dentro de mensagens do chat no modo claro */
        .stChatMessage[data-testid="stChatMessageAssistant"] p,
        .stChatMessage[data-testid="stChatMessageAssistant"] li,
        .stChatMessage[data-testid="stChatMessageAssistant"] h1,
        .stChatMessage[data-testid="stChatMessageAssistant"] h2,
        .stChatMessage[data-testid="stChatMessageAssistant"] h3 {
            color: #333333 !important;
        }
        
        .stChatMessage[data-testid="stChatMessageUser"] p,
        .stChatMessage[data-testid="stChatMessageUser"] li,
        .stChatMessage[data-testid="stChatMessageUser"] h1,
        .stChatMessage[data-testid="stChatMessageUser"] h2,
        .stChatMessage[data-testid="stChatMessageUser"] h3 {
            color: #0c344b !important;
        }
        
        /* Ajuste para links dentro de mensagens no modo claro */
        .stChatMessage[data-testid="stChatMessageAssistant"] a {
            color: #0066cc !important;
        }
        
        .stChatMessage[data-testid="stChatMessageUser"] a {
            color: #0277bd !important;
        }
    }
    
    /* Botão de envio personalizado */
    .stChatInputContainer button {
        border-radius: 20px;
    }
    
    /* Remover bordas e sombras indesejadas */
    .stApp > header {
        display: none;
    }
    
    .stApp > footer {
        display: none;
    }
    
    /* Ajuste para o modo de tema do Streamlit */
    [data-testid="stAppViewBlockContainer"] {
        background: inherit;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho personalizado
st.markdown('<div class="main-header"><h1>Assistente da Câmara Espanhola</h1></div>', unsafe_allow_html=True)

# Inicializar o estado da sessão para o histórico do chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o assistente da Câmara Oficial Espanhola de Comércio no Brasil. Como posso ajudar você hoje?"}
    ]

# Exibir mensagens do chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do chat
if prompt := st.chat_input("Digite sua mensagem..."):
    # Adicionar mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Exibir mensagem do usuário
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Buscar documentos relevantes
    with st.spinner("Buscando informações..."):
        documents = search_documents(prompt)
    
    # Gerar resposta
    with st.chat_message("assistant"):
        # Extrair histórico do chat para contexto (últimas 6 mensagens)
        chat_history = [{"role": msg["role"], "content": msg["content"]} 
                       for msg in st.session_state.messages[-6:] if msg["role"] != "assistant"]
        
        # Gerar e exibir resposta
        message_placeholder = st.empty()
        with st.spinner("Gerando resposta..."):
            response = generate_response(prompt, documents, chat_history)
        message_placeholder.markdown(response)
    
    # Adicionar resposta do assistente ao histórico
    st.session_state.messages.append({"role": "assistant", "content": response})

# Rodapé
st.markdown('<div class="footer"> 2025 Câmara Oficial Espanhola de Comércio no Brasil</div>', unsafe_allow_html=True)
