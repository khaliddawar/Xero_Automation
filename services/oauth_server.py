from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import webbrowser
import json

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    received_code = None
    
    def do_GET(self):
        """Handle the callback from Microsoft OAuth"""
        # Parse the URL and query parameters
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        
        if 'code' in params:
            OAuthCallbackHandler.received_code = params['code'][0]
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            success_message = """
            <html>
                <head><title>Authentication Successful</title></head>
                <body>
                    <h1>Authentication Successful!</h1>
                    <p>You can close this window and return to the application.</p>
                    <script>window.close();</script>
                </body>
            </html>
            """
            self.wfile.write(success_message.encode())
        else:
            # Send error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authentication failed - no code received")

def start_oauth_server():
    """Start the OAuth callback server"""
    server = HTTPServer(('localhost', 8000), OAuthCallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    return server

def stop_oauth_server(server):
    """Stop the OAuth callback server"""
    server.shutdown()
    server.server_close()