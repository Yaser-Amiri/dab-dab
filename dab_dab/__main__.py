import sys
import logging
import json

from . import server
from . import utils

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-d %H:%M:%S",
)


def main():
    args = sys.argv[1:]
    logging.info("Args: %s" % args)
    with open("/tmp/dabdab_config.json") as f:
        config = json.load(f)
    group = config.get("group", "dab-dab")
    if not utils.create_group(group):
        exit(1)
    server.run(
        host=config.get("host", "localhost"),
        port=config.get("port", 9669),
        authorized_users=utils.get_members(group),
    )


main()
