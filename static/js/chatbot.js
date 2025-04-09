// Chatbot functionality
document.addEventListener('DOMContentLoaded', function() {
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

    // Chat functionality
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
    
    // Function to send a message to the backend
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessage(message, true);
        userInput.value = '';
        
        // Show loading indicator
        loading.style.display = 'block';
        
        try {
            // Send request to the API
            // In production, this will be redirected to the actual backend by Netlify
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
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            // Add assistant response to chat with HTML formatting
            addMessage(data.formatted_response, false);
        } catch (error) {
            console.error('Error:', error);
            addMessage('Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente mais tarde.', false);
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
    
    // Add initial message
    addMessage('Olá! Sou o assistente da Câmara Espanhola. Como posso ajudar você hoje?', false);
});
