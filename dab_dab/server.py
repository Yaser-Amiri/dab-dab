from typing import Dict, Any
import traceback
import json
from urllib.parse import urlparse, parse_qs
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler


class Handler(BaseHTTPRequestHandler):
    def _return_response(self, body: Dict[str, Any], status_code: int = 200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Credentials", "*")
        self.end_headers()
        output = json.dumps(body)
        self.wfile.write(output.encode())

    def _is_interactive(self) -> bool:
        qs = parse_qs(urlparse(self.path).query).get("interactive", [])
        return bool(qs and qs[0].lower() == "true")

    def do_POST(self):
        print(self.path)
        try:
            if self.headers.get("Content-Type") != "application/json":
                self._return_response(
                    {"error": "content-type must be application/json"}, 400
                )
                return

            content_len = int(self.headers.get("Content-Length"))
            raw_body = self.rfile.read(content_len)
            try:
                payload = json.loads(raw_body)
                print(payload)
            except json.decoder.JSONDecodeError:
                self._return_response(
                    {"error": "can not parse the body as json"}, 400
                )
                return
            self._return_response({"message": "OK"})
            return
        except Exception:
            traceback.print_exc()
            self.send_error(500, "Something bad happend! check the logs.")

    def do_OPTIONS(self):
        self._return_response({})
        return


def run(host: str = "localhost", port: int = 9669):
    server = ThreadingHTTPServer((host, port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
