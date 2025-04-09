import http.server
import socketserver
import os
import subprocess
import threading
import webbrowser
import time

# Configuration
PORT = 8080
CHATBOT_PORT = 8502
DIRECTORY = "static"

# Ensure the static directory exists
os.makedirs(DIRECTORY, exist_ok=True)

# Copy the direct HTML file to index.html
os.system("cp static/index_direct.html static/index.html")

# Function to start the direct chatbot
def start_chatbot():
    print("Starting direct chatbot on port", CHATBOT_PORT)
    subprocess.Popen(["python", "direct_chatbot.py"])

# Start the chatbot in a separate thread
chatbot_thread = threading.Thread(target=start_chatbot)
chatbot_thread.daemon = True
chatbot_thread.start()

# Wait a moment for the chatbot to start
time.sleep(3)

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
