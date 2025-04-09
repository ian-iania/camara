import http.server
import socketserver
import os
import webbrowser

# Configuration
PORT = 8080
DIRECTORY = "static"

# Ensure the static directory exists
os.makedirs(DIRECTORY, exist_ok=True)

# Copy the complete solution to index.html
os.system("cp static/complete_solution.html static/index.html")

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
