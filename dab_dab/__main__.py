import sys
import os
import logging
import json

from . import server
from . import utils

log_level = os.environ.get("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-d %H:%M:%S",
)


def main() -> None:
    args = sys.argv[1:]
    logging.info("Args: %s" % args)
    with open("/tmp/dabdab_config.json") as f:
        config = json.load(f)
    group = config.get("group", "dab-dab")
    if "--pass-initialization" not in args:
        if not utils.create_group(group):
            exit(1)
        for user in utils.get_members(group):
            if not utils.create_venv_for_user(user):
                exit(2)
    server.run_server(
        host=config.get("host", "localhost"),
        port=config.get("port", 9669),
        authorized_users=utils.get_members(group),
    )
    return


main()
