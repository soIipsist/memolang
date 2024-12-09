import os
import subprocess
import sys
import time

from api import DatabaseContext
from api.utils.hash_utils import hash_password

root_directory = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, root_directory)

from api.database import (
    get_db_object,
    run_postgres_script,
    create_db_script,
    drop_db_script,
    database_name,
)

from api.models.user import User, Role
from dummy import Dummy

from constants import *
from api.utils.parser import parse_args_to_dict

if __name__ == "__main__":

    args = parse_args_to_dict(sys.argv)

    if not args:
        args = {"database_name": database_name}

    scripts_dir = (
        os.path.dirname(args.get("script_path"))
        if args.get("script_path")
        else os.getcwd()
    )

    # drop and create postgres db
    drop_db_script = os.path.join(scripts_dir, drop_db_script)
    create_db_script = os.path.join(scripts_dir, create_db_script)

    run_postgres_script(drop_db_script, args)
    run_postgres_script(create_db_script, args)

    # RUN HERE
    uvicorn_process = subprocess.Popen(
        ["uvicorn", "api.main:app", "--reload", "--log-level", "debug"]
    )
    time.sleep(3)

    uvicorn_process.terminate()

    dummy = Dummy(model=Role, length=3, db_context=DatabaseContext.ALL)

    dummy.conn = create_connection(ss_db_path)
    dummy.session = get_db_object()

    # insert sample users

    password = "password"

    roles = [Role(name="admin"), Role(name="user")]
    dummy.insert_model_items(roles)

    default_users = [
        User(username="admin", password=password, roles=[roles[1]]),
        User(username="red", password=password, roles=[roles[0]]),
        User(username="blue", password=password, roles=[roles[0]]),
    ]

    for d in default_users:
        setattr(d, "password", hash_password(d.password))

    dummy.insert_model_items(default_users)
