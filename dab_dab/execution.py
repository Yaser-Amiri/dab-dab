from typing import List, Dict, Any, Union, Tuple
import json
import logging
from pathlib import Path

from .utils import get_config_dir, sh, get_venv_dir


def run(
    user, script_code: str, params: Union[List[Any], Dict[str, Any]]
) -> Tuple[bool, str]:
    """Executes scripts
    This function basically finds the script in the users config directory,
    encodes params as json and runs the script with users UID and passes
    the params json as environment variable.

    Args:
        user (str): the user
        script_code (str): directory name of the script which
            client wants to run
        params (Union[List[Any], Dict[str, Any]]): decoded json
    Returns:
        Tuple[bool, str]: First member shows the operation succeed(True)
            or not(False) and the second member is a message. It will
            contain STDOUT of the script or an internal error message.
    """
    script = Path(get_config_dir(user)) / Path(script_code) / Path("main.py")
    if not script.is_file():
        return False, "You don't have this script."

    activate_path = Path(get_venv_dir(user)) / Path("bin/activate")
    cmd = "source {venv} && python -u {script}".format(
        venv=str(activate_path), script=str(script)
    )
    envs = {"PARAMS": json.dumps(params)}
    return_code, stdout, stderr = sh(cmd, user, envs)
    logging.debug("RETURN CODE: %s" % return_code)
    logging.debug("STDOUT: %s" % stdout)
    logging.debug("STDERR: %s" % stderr)
    if return_code != 0:
        logging.error(
            (
                "{script_code} with path: '{path}' and "
                "user: '{user}' failed. exit code: {exc}"
            ).format(
                script_code=script_code,
                path=str(script),
                user=user,
                exc=return_code,
            )
        )
        return False, stdout
    return True, stdout
