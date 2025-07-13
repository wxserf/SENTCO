# sentience_cli.py
"""
Command-line interface for testing Sentience locally
Provides OAuth flow handling and interactive querying
"""

import os
import sys
import json
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

from sentience_core import SentienceCore, EVECharacter


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback"""
    
    def log_message(self, format, *args):
        """Suppress default HTTP log messages"""
        pass
        
    def do_GET(self):
        """Handle OAuth callback"""
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/callback':
            query_params = parse_qs(parsed_url.query)
            
            if 'code' in query_params:
                # Store the authorization code
                self.server.auth_code = query_params['code'][0]
                self.server.state = query_params.get('state', [''])[0]
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                success_html = """
                <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #4CAF50;">Authentication Successful!</h1>
                    <p>You can now close this window and return to the terminal.</p>
                    <script>window.setTimeout(function(){window.close()}, 3000);</script>
                </body>
                </html>
                """
                self.wfile.write(success_html.encode())
            else:
                # Handle error
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                error_html = """
                <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #f44336;">Authentication Failed</h1>
                    <p>Please try again.</p>
                </body>
                </html>
                """
                self.wfile.write(error_html.encode())
        else:
            self.send_response(404)
            self.end_headers()


class SentienceCLI:
    """Command-line interface for Sentience"""
    
    def __init__(self):
        # Load configuration
        self.config = self.load_config()
        
        # Initialize core
        self.sentience = SentienceCore(
            client_id=self.config['client_id'],
            client_secret=self.config['client_secret'],
            callback_url=self.config['callback_url'],
            openai_api_key=self.config['openai_api_key']
        )
        
        # Storage for auth flow
        self.current_code_verifier = None
        self.current_character = None
        
    def load_config(self) -> dict:
        """Load configuration from environment or config file"""
        config_path = 'config.json'
        
        # Try to load from config file first
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Fall back to environment variables
        return {
            'client_id': os.getenv('EVE_CLIENT_ID', ''),
            'client_secret': os.getenv('EVE_CLIENT_SECRET', ''),
            'callback_url': os.getenv('EVE_CALLBACK_URL', 'http://localhost:8765/callback'),
            'openai_api_key': os.getenv('OPENAI_API_KEY', '')
        }
        
    def save_config(self, config: dict):
        """Save configuration to file"""
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
            
    def setup_wizard(self):
        """Interactive setup for first-time configuration"""
        print("\n=== Sentience Setup Wizard ===\n")
        
        print("You'll need to register an application at https://developers.eveonline.com")
        print("Set the callback URL to: http://localhost:8765/callback\n")
        
        self.config['client_id'] = input("Enter your EVE application Client ID: ").strip()
        self.config['client_secret'] = input("Enter your EVE application Secret Key: ").strip()
        self.config['openai_api_key'] = input("Enter your OpenAI API key: ").strip()
        
        print("\nSaving configuration...")
        self.save_config(self.config)
        
        # Reinitialize with new config
        self.sentience = SentienceCore(
            client_id=self.config['client_id'],
            client_secret=self.config['client_secret'],
            callback_url=self.config['callback_url'],
            openai_api_key=self.config['openai_api_key']
        )
        
        print("Setup complete! You can now authenticate.\n")
        
    def authenticate(self):
        """Handle OAuth authentication flow"""
        scopes = [
            "esi-wallet.read_character_wallet.v1",
            "esi-assets.read_assets.v1",
            "esi-skills.read_skills.v1",
            "esi-industry.read_character_jobs.v1",
            "esi-markets.read_character_orders.v1"
        ]
        
        # Generate auth URL
        auth_url, code_verifier = self.sentience.esi_client.generate_auth_url(scopes)
        self.current_code_verifier = code_verifier
        
        print("\nOpening browser for EVE SSO authentication...")
        print(f"If browser doesn't open, visit: {auth_url}\n")
        
        # Start local server for callback
        server = HTTPServer(('localhost', 8765), OAuthCallbackHandler)
        server.auth_code = None
        
        # Open browser
        webbrowser.open(auth_url)
        
        # Wait for callback
        print("Waiting for authentication callback...")
        server_thread = threading.Thread(target=server.handle_request)
        server_thread.start()
        server_thread.join(timeout=120)  # 2 minute timeout
        
        if server.auth_code:
            print("Authorization code received!")
            
            try:
                # Add character
                character = self.sentience.add_character(server.auth_code, self.current_code_verifier)
                self.current_character = character
                
                print(f"\n✓ Successfully authenticated as {character.character_name}")
                print(f"  Character ID: {character.character_id}")
                print(f"  Scopes: {', '.join(character.scopes[:3])}...")
                
                # Save character data for persistence
                self.save_character(character)
                
            except Exception as e:
                print(f"\n✗ Authentication failed: {e}")
        else:
            print("\n✗ No authorization code received. Authentication timeout.")
            
        server.server_close()
        
    def save_character(self, character: EVECharacter):
        """Save character data for persistence"""
        char_file = f"character_{character.character_id}.json"
        char_data = {
            'character_id': character.character_id,
            'character_name': character.character_name,
            'refresh_token': character.refresh_token,
            'scopes': character.scopes,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        with open(char_file, 'w') as f:
            json.dump(char_data, f, indent=2)
            
    def load_characters(self) -> list:
        """Load saved characters"""
        characters = []
        for filename in os.listdir('.'):
            if filename.startswith('character_') and filename.endswith('.json'):
                with open(filename, 'r') as f:
                    char_data = json.load(f)
                    characters.append(char_data)
        return characters
        
    def interactive_query(self):
        """Interactive query mode"""
        if not self.current_character:
            print("No character authenticated. Please run 'auth' first.")
            return
            
        print(f"\nQuerying as {self.current_character.character_name}")
        print("Type 'exit' to return to main menu\n")
        
        while True:
            query = input("Sentience> ").strip()
            
            if query.lower() in ['exit', 'quit', 'back']:
                break
                
            if not query:
                continue
                
            print("\nProcessing query...")
            
            try:
                response = self.sentience.query_assistant(
                    str(self.current_character.character_id),
                    query
                )
                print(f"\n{response}\n")
            except Exception as e:
                print(f"\nError: {e}\n")
                
    def show_data_preview(self):
        """Show raw data preview for debugging"""
        if not self.current_character:
            print("No character authenticated.")
            return
            
        print(f"\nFetching data for {self.current_character.character_name}...\n")
        
        try:
            # Fetch wallet
            wallet = self.sentience.esi_client.get_character_wallet(self.current_character)
            print(f"Wallet Balance: {wallet.balance:,.2f} ISK")
            
            # Fetch assets summary
            assets = self.sentience.esi_client.get_character_assets(self.current_character)
            print(f"Total Assets: {len(assets)} items")
            
            # Show first few assets
            print("\nFirst 5 assets:")
            for asset in assets[:5]:
                print(f"  - Item {asset.item_id}: {asset.quantity}x Type {asset.type_id}")
                
            # Fetch skills summary
            skills = self.sentience.esi_client.get_character_skills(self.current_character)
            total_sp = sum(s.skillpoints for s in skills)
            print(f"\nTotal Skillpoints: {total_sp:,}")
            print(f"Skills Trained: {len(skills)}")
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            
    def main_menu(self):
        """Display main menu"""
        while True:
            print("\n=== Sentience AI Co-Pilot ===")
            print("1. Setup wizard (configure API keys)")
            print("2. Authenticate EVE character")
            print("3. Interactive query mode")
            print("4. Show data preview")
            print("5. List saved characters")
            print("6. Exit")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.setup_wizard()
            elif choice == '2':
                self.authenticate()
            elif choice == '3':
                self.interactive_query()
            elif choice == '4':
                self.show_data_preview()
            elif choice == '5':
                chars = self.load_characters()
                if chars:
                    print("\nSaved characters:")
                    for char in chars:
                        print(f"  - {char['character_name']} (ID: {char['character_id']})")
                else:
                    print("\nNo saved characters found.")
            elif choice == '6':
                print("\nFly safe o7")
                break
            else:
                print("\nInvalid option. Please try again.")


if __name__ == "__main__":
    cli = SentienceCLI()
    
    # Check if config exists
    if not cli.config.get('client_id'):
        print("No configuration found. Starting setup wizard...")
        cli.setup_wizard()
        
    cli.main_menu()
