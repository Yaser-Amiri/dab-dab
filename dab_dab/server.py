import logging
import re
from functools import partial
from typing import Dict, Any, Optional, List, Union
import traceback
import json
import subprocess
from urllib.parse import urlparse, parse_qs
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

from . import execution


class Handler(BaseHTTPRequestHandler):
    def __init__(self, authorized_users: List[str], *args, **kwargs):
        self.authorized_users = authorized_users
        super().__init__(*args, **kwargs)

    def _return_response(
        self, body: Dict[str, Any], status_code: int = 200
    ) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Credentials", "*")
        self.end_headers()
        output = json.dumps(body)
        self.wfile.write(output.encode())
        return

    def _is_interactive(self) -> bool:
        qs = parse_qs(urlparse(self.path).query).get("interactive", [])
        return bool(qs and qs[0].lower() == "true")

    def _get_user(self) -> Optional[str]:
        cmd = "lsof -i -P -n"
        lsof_result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True
        )
        if lsof_result.returncode != 0:
            logging.error(
                "can not find the user, result of 'lsof' command is: '%s'"
                % lsof_result.stderr
            )
            return None

        pattern = r"%s:%s->" % self.client_address
        user = None
        for line in lsof_result.stdout.split("\n"):
            if pattern in line:
                se = re.search(r"(\S+)\s+(\S+)\s+(\S+).+", line)
                if se:
                    user = se.group(3)
        return user

    def _is_user_authorized(self, user: str) -> bool:
        return user in self.authorized_users

    def _parse_body(self) -> Optional[Union[List[Any], Dict[str, Any]]]:
        content_len = int(self.headers.get("Content-Length"))
        raw_body = self.rfile.read(content_len)
        try:
            return json.loads(raw_body)
        except json.decoder.JSONDecodeError:
            return None

    def _get_url_parts(self) -> List[str]:
        url = urlparse(self.path).path
        return list(filter(lambda x: bool(x), url.split("/")))

    def do_POST(self) -> None:
        try:
            # check request content type
            if self.headers.get("Content-Type") != "application/json":
                self._return_response(
                    {"messge": "content-type must be application/json"}, 400
                )
                return

            # get user
            user = self._get_user()
            if not user:
                self._return_response({"messge": "Unauthorized"}, 401)
                return

            # check authorization
            if not self._is_user_authorized(user):
                self._return_response({"messge": "Unauthorized"}, 403)
                return

            # check authorization
            body = self._parse_body()
            if body is None:
                self._return_response(
                    {"messge": "can not parse the body as json"}, 400
                )
                return

            # parse URL and decide about next action
            url_parts = self._get_url_parts()
            is_interactive = self._is_interactive()
            if len(url_parts) == 2 and url_parts[0] == "scripts":
                succeed, result = execution.run(user, url_parts[1], body)
                code = 200 if succeed else 500
                non_interactinve_messages = {True: "OK", False: "Failed"}
                msg = (
                    result
                    if is_interactive
                    else non_interactinve_messages[succeed]
                )
                self._return_response({"message": msg}, code)
                return

            # not found
            self._return_response({"message": "Not Found"}, 404)
            return
        except Exception:
            traceback.print_exc()
            self.send_error(500, "Something bad happend! check the logs.")

    def do_OPTIONS(self) -> None:
        self._return_response({})
        return


def run_server(host: str, port: int, authorized_users: List[str]) -> None:
    logging.info("Trying to create a HTTP server on %s:%s" % (host, port))
    handler = partial(Handler, authorized_users)
    server = ThreadingHTTPServer((host, port), handler)
    logging.info(
        "HTTP server started successfully, address: %s:%s" % (host, port)
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
        logging.info("Bye!")
