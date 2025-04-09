import streamlit as st
import os
from dotenv import load_dotenv
import pinecone
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import Pinecone as LangchainPinecone

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Chatbot Câmara",
    page_icon="📚",
    layout="centered"
)

# Initialize Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = "pdf"

# Initialize the Pinecone client
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)

# Function to initialize the conversational chain
@st.cache_resource
def get_conversation_chain():
    # Initialize OpenAI embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    
    # Create a Langchain vectorstore from the Pinecone index
    # Note: LangchainPinecone expects a different format than what we're using
    # We need to pass the index name instead of the index object
    vectorstore = LangchainPinecone.from_existing_index(
        index_name=INDEX_NAME,
        embedding=embeddings,
        text_key="text"
    )
    
    # Initialize the language model
    llm = ChatOpenAI(
        model_name="gpt-4o",
        temperature=0.2
    )
    
    # Create conversation memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Create the conversational chain
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        memory=memory,
        verbose=True
    )
    
    return conversation_chain

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
        
        # Get the conversation chain
        conversation_chain = get_conversation_chain()
        
        # Get response from conversation chain
        with st.spinner("Pensando..."):
            response = conversation_chain.invoke({"question": prompt})
            answer = response["answer"]
        
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
    - LangChain para conectar os componentes
    
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
