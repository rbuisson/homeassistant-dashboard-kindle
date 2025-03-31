import http.server
import socketserver
import requests
import json
import os
from urllib.parse import parse_qs, urlparse

# Configuration
HA_API_URL = "http://192.168.55.154:8123/api/"
PORT = 8000

# Entity IDs for devices
ENTITIES = {
    "cuisine": "light.0x842e14fffe745ca6",
    "cour": "switch.0x70b3d52b60102ad4",
    "gate_sensor": "binary_sensor.contact_sensor_door",  # Updated sensor for gate
    "gate_relay": "switch.wave_1pm"
}

def read_token():
    """Read Bearer token from 'token' file."""
    try:
        with open("token", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise RuntimeError("'token' file not found")

BEARER_TOKEN = read_token()
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle client GET requests."""
        if self.path.startswith("/get-state"):
            self.handle_get_state()
        elif self.path == "/":
            self.serve_static("public/index.html")
        else:
            self.send_error(404, "Endpoint non trouvé")

    def do_POST(self):
        """Handle client POST requests."""
        if self.path.startswith("/toggle-light"):
            self.handle_toggle_light()
        elif self.path.startswith("/toggle-gate"):
            self.handle_toggle_gate()
        else:
            self.send_error(404, "Endpoint non trouvé")

    def handle_get_state(self):
        """Fetch state for a given entity ID."""
        query = parse_qs(urlparse(self.path).query)
        entity_key = query.get("entity", [None])[0]

        if not entity_key or entity_key not in ENTITIES:
            self.send_error(400, "Paramètre d'entité invalide ou manquant")
            return

        entity_id = ENTITIES[entity_key]

        try:
            response = requests.get(
                f"{HA_API_URL}states/{entity_id}",
                headers=HEADERS
            )
            response.raise_for_status()
            self.send_json(response.json())
        except Exception as e:
            self.send_error(500, f"Erreur lors de la récupération de l'état : {str(e)}")

    def handle_toggle_light(self):
        """Toggle light state for a given entity ID."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = json.loads(self.rfile.read(content_length))
        entity_key = post_data.get("entity")

        if not entity_key or entity_key not in ENTITIES:
            self.send_error(400, "Paramètre d'entité invalide ou manquant")
            return

        entity_id = ENTITIES[entity_key]

        try:
            response = requests.get(
                f"{HA_API_URL}states/{entity_id}",
                headers=HEADERS
            )
            response.raise_for_status()
            current_state = response.json().get("state", "unknown")
            service = "turn_off" if current_state == "on" else "turn_on"

            response = requests.post(
                f"{HA_API_URL}services/{'light' if 'light' in entity_id else 'switch'}/{service}",
                headers=HEADERS,
                json={"entity_id": entity_id}
            )
            response.raise_for_status()

            new_state = "off" if current_state == "on" else "on"
            self.send_json({"success": True, "new_state": new_state})
        except Exception as e:
            self.send_error(500, f"Erreur lors du basculement de l'état : {str(e)}")

    def handle_toggle_gate(self):
        """Toggle gate relay."""
        try:
            # Toggle the gate relay
            response = requests.post(
                f"{HA_API_URL}services/switch/toggle",
                headers=HEADERS,
                json={"entity_id": ENTITIES["gate_relay"]}
            )
            response.raise_for_status()

            # Fetch updated state of the gate sensor
            sensor_response = requests.get(
                f"{HA_API_URL}states/{ENTITIES['gate_sensor']}",
                headers=HEADERS
            )
            sensor_response.raise_for_status()

            gate_state = sensor_response.json().get("state", "unknown")
            self.send_json({"success": True, "gate_state": gate_state})
        except Exception as e:
            self.send_error(500, f"Erreur lors du basculement du portail : {str(e)}")

    def send_json(self, data):
        """Send JSON response to client."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def serve_static(self, path):
        """Serve static files from public directory."""
        if not os.path.exists(path):
            self.send_error(404, "Fichier non trouvé")
            return

        self.send_response(200)
        if path.endswith(".html"):
            self.send_header("Content-Type", "text/html")
        elif path.endswith(".css"):
            self.send_header("Content-Type", "text/css")
        elif path.endswith(".js"):
            self.send_header("Content-Type", "application/javascript")
        self.end_headers()

        with open(path, "rb") as f:
            self.wfile.write(f.read())

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serveur en cours d'exécution sur http://localhost:{PORT}")
        httpd.allow_reuse_address = True  # Allow port reuse for frequent restarts
        httpd.serve_forever()
