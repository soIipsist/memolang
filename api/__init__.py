from enum import Enum
import os
import sys

database_name = "nulang"
database_username = "p"
database_password = "root"
database_hostname = "localhost"
database_port = "5432"

delete_tables_script = "delete_tables.sql"
create_db_script = "create_db.sql"
drop_db_script = "drop_db.sql"
reset_table_script = "reset_table.sql"
dummy_script = "dummy.py"
list_tables_script = "list_tables.sql"
reset_db_script = "reset_db.py"

base_script = reset_db_script


def get_connection_string(
    database_username: str = database_username,
    database_password: str = database_password,
    database_hostname: str = database_hostname,
    database_name: str = database_name,
):
    return f"postgresql://{database_username}:{database_password}@{database_hostname}/{database_name}"


root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)


class DatabaseContext(str, Enum):
    ALL = "all"
    LOCAL = "local"
    SERVER = "server"


database_context = DatabaseContext.LOCAL
user_token = None


def set_global_database_context(db_context: DatabaseContext):
    if db_context is None:
        db_context = DatabaseContext.LOCAL
    global database_context
    database_context = db_context


def get_global_database_context():
    return database_context


def set_global_user_token(token):
    global user_token
    user_token = token


def get_global_user_token():
    db_context = get_global_database_context()
    return user_token if db_context != DatabaseContext.LOCAL else None
