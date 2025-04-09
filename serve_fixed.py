import http.server
import socketserver
import os
import subprocess
import threading
import webbrowser
import time

# Configuration
PORT = 8000
CHATBOT_PORT = 8501
DIRECTORY = "static"

# Ensure the static directory exists
os.makedirs(DIRECTORY, exist_ok=True)

# Function to start the Streamlit chatbot
def start_chatbot():
    print("Starting chatbot on port", CHATBOT_PORT)
    subprocess.Popen(["streamlit", "run", "chatbot_embed_fixed.py", "--server.port", str(CHATBOT_PORT)])

# Start the chatbot in a separate thread
chatbot_thread = threading.Thread(target=start_chatbot)
chatbot_thread.daemon = True
chatbot_thread.start()

# Wait a moment for the chatbot to start
time.sleep(2)

# Create a simple HTTP server
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

# Start the HTTP server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    
    # Open the browser
    webbrowser.open(f"http://localhost:{PORT}")
    
    # Serve until interrupted
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
