import sys
import logging
import json

from . import server

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
    server.run(config.get("host", "localhost"), config.get("port", 9669))


main()
