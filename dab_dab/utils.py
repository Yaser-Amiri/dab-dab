import logging
from pathlib import Path
from typing import List, Tuple, Callable
import os
import pwd
import grp
import subprocess


def _change_user(uid, gid) -> Callable[[], None]:
    """This is a closure to changes UID and GID of current process
    Args:
        uid (int): UID
        gid (int): GID
    Returns:
        A function to use in preexec of Popens
    """

    def result() -> None:
        os.setgid(gid)
        os.setuid(uid)

    return result


def sh(cmd: str, user: str) -> Tuple[int, str, str]:
    """Runs a command in shell
    Args:
        cmd (str): The command which we want to run
        user (str): The user that we want to run the command by his UID
            and permissions
    Returns:
        Tuple[int, str, str]: Tuple of return code, stdout and stderr
    """
    pw_record = pwd.getpwnam(user)
    process = subprocess.Popen(
        cmd,
        preexec_fn=_change_user(pw_record.pw_uid, pw_record.pw_gid),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True,
    )
    stdout, stderr = process.communicate()
    return (process.returncode, stdout.strip(), stderr.strip())


def create_group(name: str) -> bool:
    """Creates a group for users who want to use this software
    Args:
        name (str): Group name
    Returns:
        bool: True means the operation was successful
    """
    cmd = "groupadd -f %s" % name
    return_code, stdout, stderr = sh(cmd, "root")
    if return_code != 0:
        logging.error(
            "can not create the group, result of '%s' command is: '%s'"
            % (cmd, stderr)
        )
        return False
    return True


def get_members(group_name: str) -> List[str]:
    """Lists members of a group
    Args:
        group_name (str): Group name
    Returns:
        List[str]: List of users who are members of the group
    """
    return grp.getgrnam(group_name).gr_mem


def get_config_dir(user: str) -> str:
    """Returns absolute path of config directory of a user
        (in his home directory)
    Args:
        user (str): The user
    Returns:
        str: Absolute path of config directory
    """
    pw_record = pwd.getpwnam(user)
    return str(Path(pw_record.pw_dir) / Path(".config/dab-dab"))


def get_venv_dir(user: str) -> str:
    """Returns absolute path of virtual env directory of a user
    Args:
        user (str): The user
    Returns:
        str: Absolute path of the virtual env directory
    """
    return str(Path(get_config_dir(user)) / Path(".venv"))


def create_config_dir(user: str) -> bool:
    """Creates config directory for a specific user
        (in his home directory)
    Args:
        user (str): The user
    Returns:
        bool: True means the operation was successful
    """
    cmd = "mkdir -p %s" % get_config_dir(user)
    return_code, stdout, stderr = sh(cmd, user)
    if return_code != 0:
        logging.error(
            (
                "can not create config directory for "
                "user: '{user}', cmd: '{cmd}'\n"
                "stderr:\n'{stderr}'\n"
                "stdout:\n'{stdout}'"
            ).format(
                user=user, cmd=cmd, stdout=stdout, stderr=stderr,
            )
        )
        return False
    return True


def create_venv_for_user(user: str) -> bool:
    """Creates virtual env for a specific user
    Args:
        user (str): The user
    Returns:
        bool: True means the operation was successful
    """
    if not create_config_dir(user):
        return False
    cmd = "python3 -m venv %s" % get_venv_dir(user)
    return_code, stdout, stderr = sh(cmd, user)
    if return_code != 0:
        logging.error(
            (
                "can not create venv for "
                "user: '{user}', cmd: '{cmd}'\n"
                "stderr:\n'{stderr}'\n"
                "stdout:\n'{stdout}'"
            ).format(
                user=user, cmd=cmd, stdout=stdout, stderr=stderr,
            )
        )
        return False
    return True
