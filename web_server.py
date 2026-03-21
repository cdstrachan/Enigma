"""
Simple web server for Enigma frontend and API.
Run with: python web_server.py
"""
from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from web_controller import EnigmaSessionStore


ROOT_DIR = Path(__file__).parent
WEB_DIR = ROOT_DIR / "web"
SESSION_STORE = EnigmaSessionStore()


class EnigmaRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, file_path: Path) -> None:
        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return

        content_type = "text/plain"
        if file_path.suffix == ".html":
            content_type = "text/html"
        elif file_path.suffix == ".css":
            content_type = "text/css"
        elif file_path.suffix == ".js":
            content_type = "application/javascript"

        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length) if content_length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def _get_session(self, body: dict):
        session_id = body.get("sessionId")
        if not session_id:
            return None
        return SESSION_STORE.get(session_id)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self._send_file(WEB_DIR / "index.html")
            return

        if path.startswith("/web/"):
            relative = path.replace("/web/", "", 1)
            self._send_file(WEB_DIR / relative)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Route not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            body = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
            return

        if path == "/api/session":
            num_rotors = int(body.get("numRotors", 3))
            seed_value = body.get("seed")
            seed = int(seed_value) if seed_value is not None and str(seed_value).strip() != "" else None
            randomize_positions = bool(body.get("randomizePositions", False))
            session = SESSION_STORE.create(
                num_rotors=num_rotors,
                seed=seed,
                randomize_positions=randomize_positions,
            )
            self._send_json({"sessionId": session.session_id, "state": session.snapshot()})
            return

        session = self._get_session(body)
        if session is None:
            self._send_json({"error": "Invalid or missing sessionId"}, status=HTTPStatus.BAD_REQUEST)
            return

        if path == "/api/state":
            self._send_json({"state": session.snapshot()})
            return

        if path == "/api/keypress":
            letter = body.get("letter", "")
            self._send_json(session.encrypt_keypress(letter))
            return

        if path == "/api/encrypt":
            message = body.get("message", "")
            self._send_json(session.encrypt_message(message))
            return

        if path == "/api/reset":
            self._send_json(session.reset_rotors())
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Route not found")


def run() -> None:
    host = "0.0.0.0"
    port = 8000
    server = ThreadingHTTPServer((host, port), EnigmaRequestHandler)
    print(f"Enigma web app running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
