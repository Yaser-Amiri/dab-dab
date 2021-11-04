from typing import List
import grp
import logging
import subprocess


def create_group(name: str) -> bool:
    cmd = "groupadd -f %s" % name
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(
            "can not create the group, result of '%s' command is: '%s'"
            % (cmd, result.stderr)
        )
        return False
    return True


def get_members(group_name: str) -> List[str]:
    return grp.getgrnam(group_name).gr_mem
