#!/usr/bin/env python3
"""
ForgeOS Captive Portal & Provisioning Backend
Simple, clean HTTP server for writing /boot/forge/ configs.
"""
import http.server
import socketserver
import json
import os
import sys
from pathlib import Path

PORT = 80
STATIC_DIR = Path(__file__).parent.resolve()

API_BASE_URLS = {
    "groq": "https://api.groq.com/openai/v1",
    "cerebras": "https://api.cerebras.ai/v1"
}

class CaptivePortalHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self):
        path = self.path

        if path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            status_data = {
                "soc": "Amlogic S905X2 (G12A)",
                "kernel": "Linux 6.18.29-meson64",
                "ram_free_mb": 1588,
                "ram_total_mb": 2048,
                "emmc_free_gb": 6.2,
                "emmc_total_gb": 8.0,
                "drm_status": "connected",
                "wifi_chip": "Realtek RTL8189FTV",
                "temp_c": 47.5
            }
            self.wfile.write(json.dumps(status_data).encode('utf-8'))
            return

        # Redirect any canary request to captive portal
        if not path.startswith('/api') and not (STATIC_DIR / path.lstrip('/')).exists():
            self.send_response(302)
            self.send_header('Location', f'http://192.168.4.1:{PORT}/')
            self.end_headers()
            return

        super().do_GET()

    def do_POST(self):
        if self.path == '/api/provision':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                config = json.loads(post_data.decode('utf-8'))
                print(f"[FORGEOS PROVISION] Config: {config}")

                provider = config.get('apiProvider', 'groq')
                base_url = API_BASE_URLS.get(provider, API_BASE_URLS['groq'])

                # Save configs on Linux
                forge_boot = Path('/boot/forge')
                if os.name == 'posix':
                    forge_boot.mkdir(parents=True, exist_ok=True)
                    
                    # 1. Write network.yaml
                    with open(forge_boot / 'network.yaml', 'w', encoding='utf-8') as f:
                        f.write(f"ssid: '{config.get('wifiSSID', '')}'\n")
                        f.write(f"passphrase: '{config.get('wifiPass', '')}'\n")
                        f.write(f"dhcp: {str(config.get('dhcp', True)).lower()}\n")

                    # 2. Write mina.yaml
                    with open(forge_boot / 'mina.yaml', 'w', encoding='utf-8') as f:
                        f.write(f"api_provider: '{provider}'\n")
                        f.write(f"api_base_url: '{base_url}'\n")
                        f.write(f"api_key: '{config.get('apiKey', '')}'\n")
                        f.write(f"window_mode: '{config.get('windowMode', '-g right')}'\n")

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "Provisioned successfully"}).encode('utf-8'))

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
            return

        self.send_error(404, "Endpoint Not Found")

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    with socketserver.TCPServer(("", port), CaptivePortalHandler) as httpd:
        print(f"[FORGEOS] Server running at http://0.0.0.0:{port}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == '__main__':
    main()
