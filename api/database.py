from pprint import pprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

import uvicorn
from api import *
from utils.hash_utils import *
from utils.file_utils import read_file
from utils.parser import BoolArgument, Parser, Argument, PathArgument

import tempfile
import stat
import subprocess

# main database connection
SQLALCHEMY_DATABASE_URL = get_connection_string()
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative bases
Base = declarative_base()


def init_db():
    from models.user import User, Role

    db = SessionLocal()
    roles = ["admin", "user"]
    for role_name in roles:
        role = db.query(Role).filter(Role.name == role_name).first()
        if role is None:
            new_role = Role(name=role_name)
            db.add(new_role)
            db.commit()

    db.commit()
    db.close()

    return roles


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_object():
    db = SessionLocal()
    return db


def replace_script_with_args(args: dict, script_path: str):
    sql_script = read_file(script_path)

    if isinstance(args, dict):
        for k, v in args.items():
            v = str(v)
            sql_script = sql_script.replace(f"{{{k}}}", v)

    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".sql"
    ) as temp_file:
        temp_file.write(sql_script)
        temp_file_path = temp_file.name

    return temp_file_path


def run_python_script(script_path: str, args: dict):
    a = []

    for k, v in args.items():
        if v is not None:
            a.append("--" + k)
            a.append(str(v))

    cmd = ["python", script_path]
    cmd.extend(a)

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running the script: {e}")
        print("Script error output:", e.stderr)


def run_postgres_script(
    script_path: str,
    args: dict = None,
    is_super_command: bool = False,
):
    global database_name, database_username, database_hostname

    if not os.path.exists(script_path):
        raise ValueError(f"script {script_path} does not exist.")

    original_script_path = script_path

    if args:
        script_path = replace_script_with_args(args, script_path)

    create_pg_pass("root")

    script_name = os.path.basename(original_script_path)
    if script_name == "create_db.sql" or script_name == "drop_db.sql":
        is_super_command = True

    arguments = [
        "psql",
        "-h",
        database_hostname,
        "-d",
        database_name,
        "-U",
        database_username,
        "-p",
        database_port,
        "<",
        script_path,
    ]
    if is_super_command:
        arguments[4] = "postgres"

    os.system(" ".join(arguments))


def create_pg_pass(password: str):
    pgpass_line = f"{database_hostname}:{database_port}:{database_name}:{database_username}:{password}\n"
    pgpass_path = os.path.join(os.path.expanduser("~"), ".pgpass")

    lines = []
    if os.path.exists(pgpass_path):
        with open(pgpass_path, "r") as f:
            lines = f.readlines()

    updated = False
    with open(pgpass_path, "w") as f:
        for line in lines:
            if line.startswith(
                f"{database_hostname}:{database_port}:{database_name}:{database_username}:"
            ):
                f.write(pgpass_line)
                updated = True
            else:
                f.write(line)

        if not updated:
            f.write(pgpass_line)

    os.chmod(pgpass_path, stat.S_IRUSR | stat.S_IWUSR)


def get_script_path(script: str):
    root_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(root_directory, "scripts", script)
    return script_path


if __name__ == "__main__":
    default_script_path = get_script_path(base_script)
    parser_arguments = [
        Argument(name=("-s", "--script"), default=None),
        PathArgument(name=("-p", "--script_path"), default=default_script_path),
        Argument(name=("-d", "--database_name"), default=database_name),
        Argument(name=("-t", "--table_name"), default=None),
        Argument(name=("-i", "--sequence_id"), default="id"),
        Argument(name=("-m", "--model"), default=None),
        Argument(
            name=("-a", "--action"),
            default="list",
            choices=["insert", "delete", "list"],
        ),
        BoolArgument(name=("--is_super_command"), default=False),
        Argument(name=("-l", "--length"), default=None),
        BoolArgument(name="--start_server", default=False),
    ]

    parser = Parser(parser_arguments)
    args = parser.get_command_args()

    script = args.get("script")
    script_path = args.get("script_path")
    database_name = args.get("database_name")
    is_super_command = args.get("is_super_command")
    start_server = args.get("start_server")

    model = args.get("model")

    if model:
        script = "dummy.py"

    if script:
        script_path = get_script_path(script)

    print(f"Executing {script_path} \n")
    print("Arguments: ")
    pprint(args)

    if script_path.endswith(".sql"):
        run_postgres_script(script_path, args, is_super_command)
    else:
        run_python_script(script_path, args)

    if start_server:
        uvicorn.run("api.main:app")
