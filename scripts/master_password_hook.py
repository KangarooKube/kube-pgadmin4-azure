#!/usr/bin/env python3
"""
MASTER_PASSWORD_HOOK helper for pgAdmin.

This script exposes a callable `master_password_hook` and can also be executed
directly. It returns / prints the pgAdmin master password sourced from a file
or environment variable. Designed to be used by pgAdmin's MASTER_PASSWORD_HOOK
mechanism or as an executable hook invoked by the server.

Behavior:
  - When imported by pgAdmin as a callable, `master_password_hook()` returns
    the master password string or None.
  - When executed as a script, it prints the password to stdout and exits 0 on
    success, or exits 1 if no password is available.

Environment Variables:
    PGADMIN_MASTER_PASSWORD_FILE  - (optional) path to a file containing the master password.
                                    Recommended: mount a Kubernetes Secret as a file here.
    PGADMIN_MASTER_PASSWORD       - (optional) fallback environment variable containing the password.

Usage (executable):
    master_password_hook.py

Usage (callable from config):
    # in config_system.py
    from scripts.master_password_hook import master_password_hook
    MASTER_PASSWORD_HOOK = master_password_hook

Arguments:
    None

Output:
    - Executable: prints the password to stdout when found.
    - Callable: returns the password string or None.

Dependencies:
    - Python stdlib only (no external packages required)

Exceptions:
    SystemExit:
        - Exit code 0 on success, 1 on missing password when executed as a script.
    General exceptions:
        - Any unexpected error will be logged to stderr and cause a non-zero exit
          when executed as a script.

Examples:
    # Run inside the container using the virtualenv python
    /venv/bin/python /pgadmin4/scripts/master_password_hook.py

    # Example config_system.py usage:
    from scripts.master_password_hook import master_password_hook
    MASTER_PASSWORD_HOOK = master_password_hook
"""
import os
import sys
import logging
from typing import Optional

# configure basic logger to stderr (module-level but not depending on Flask)
LOG = logging.getLogger("master_password_hook")
if not LOG.handlers:
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    LOG.addHandler(handler)
LOG.setLevel(logging.INFO)

def _read_file(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            val = fh.read().strip()
            return val if val else None
    except Exception as e:
        LOG.debug("Unable to read file %s: %s", path, e)
        return None

def get_master_password() -> Optional[str]:
    """
    Return the master password string or None.

    Order:
      1. PGADMIN_MASTER_PASSWORD_FILE (if set)
      2. PGADMIN_MASTER_PASSWORD env var
    """
    # Preferred: file (mount a Kubernetes secret)
    file_path = os.getenv("PGADMIN_MASTER_PASSWORD_FILE")
    if file_path:
        pw = _read_file(file_path)
        if pw:
            LOG.info("Master password loaded from file")
            return pw
        else:
            LOG.warning("PGADMIN_MASTER_PASSWORD_FILE set but no password read: %s", file_path)

    # Fallback to env var
    pw = os.getenv("PGADMIN_MASTER_PASSWORD")
    if pw:
        LOG.info("Master password loaded from PGADMIN_MASTER_PASSWORD env var")
        return pw

    LOG.info("No master password provided via file or env")
    return None

# Name expected by pgAdmin when using a callable hook import
master_password_hook = get_master_password

def _main():
    pw = get_master_password()
    if pw:
        # Print only the password to stdout for pgAdmin exec usage
        sys.stdout.write(pw)
        sys.stdout.flush()
        sys.exit(0)
    else:
        # No value found -> non-zero so callers know there is no password
        sys.exit(1)

if __name__ == "__main__":
    _main()