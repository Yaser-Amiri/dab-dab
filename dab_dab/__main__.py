import sys
import os
import logging

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
    host: str = args[0]
    port: int = int(args[1])
    group: str = os.environ.get("GROUP", "dab-dab")
    if "--pass-initialization" not in args:
        if not utils.create_group(group):
            exit(1)
        for user in utils.get_members(group):
            if not utils.create_venv_for_user(user):
                exit(2)
    server.run_server(
        host=host, port=port, authorized_users=utils.get_members(group),
    )
    return


main()
