import os
import sqlite3
from typing import List

from pydantic import BaseModel
from sqlalchemy.orm import Session

from api import DatabaseContext
from api.utils.parser import Parser, Argument, PathArgument
from api.utils.model_utils import (
    generate_dummy_data,
    get_model_table,
    get_model_sequence_id,
    get_schema_to_model_mapping,
)

from api.database import (
    get_db_object,
    get_db,
    run_postgres_script,
    get_script_path,
)
from api.schemas import (
    DefaultUser,
    UserCreate,
    UserOut,
    TokenCreate,
    TokenData,
)

schemas = [
    DefaultUser,
    UserCreate,
    UserOut,
    TokenCreate,
    TokenData,
]

models = [User, Role]

schema_to_model_mapping = get_schema_to_model_mapping(schemas, models)


class Dummy:
    _model = None
    _schema_to_model_mapping = None
    _current_conn = None
    _conn = None
    _current_session = None
    _session = None
    _db_context = None
    _length = None
    _sequence_id = None
    _table_name = None

    _items = {}

    def __init__(
        self,
        model: str = None,
        sequence_id: str = None,
        length: int = 1,
        table_name: str = None,
        db_context=DatabaseContext.LOCAL,
        schema_to_model_mapping: dict = None,
        *args,
        **kwargs,
    ):
        self.schema_to_model_mapping = schema_to_model_mapping
        self.model = model
        self.sequence_id = sequence_id
        self.length = length
        self.table_name = table_name
        self.db_context = db_context

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, items: dict):
        self._items = items

    @property
    def table_name(self):
        return self._table_name

    @table_name.setter
    def table_name(self, table_name):
        if table_name is None and self.model and self.schema_to_model_mapping:
            table_name = get_model_table(self.model, self.schema_to_model_mapping)
        self._table_name = table_name

    @property
    def local_table_name(self):
        if self.model:
            return getattr(self.model(), "table_name", None)

    @property
    def column_names(self):
        if self.model:
            return getattr(self.model(), "column_names", None)

    @property
    def sequence_id(self):
        return self._sequence_id

    @sequence_id.setter
    def sequence_id(self, sequence_id):
        if self.model and self.schema_to_model_mapping:
            self._sequence_id = get_model_sequence_id(
                self.model, self.schema_to_model_mapping, sequence_id
            )

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length: int):
        self._length = length

    @property
    def current_conn(self):
        self._current_conn = self.conn

        if self.db_context == DatabaseContext.SERVER:
            self._current_conn = None

        return self._current_conn

    @property
    def current_session(self):
        self._current_session = self.session

        if self.db_context == DatabaseContext.LOCAL:
            self._current_session = None

        return self._current_session

    @property
    def conn(self):
        return self._conn

    @conn.setter
    def conn(self, conn: sqlite3.Connection):
        self._conn = conn

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, session: Session):
        assert isinstance(session, Session)
        self._session = session

    @property
    def db_context(self):
        return self._db_context

    @db_context.setter
    def db_context(self, db_context: DatabaseContext):
        assert db_context in DatabaseContext
        self._db_context = db_context

    @property
    def schema_to_model_mapping(self):
        return self._schema_to_model_mapping

    @schema_to_model_mapping.setter
    def schema_to_model_mapping(self, schema_to_model_mapping: dict):
        self._schema_to_model_mapping = schema_to_model_mapping

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, model: str):
        self._model = self.get_valid_model(model)

    def get_valid_model(self, model: str = None):
        if model is None:
            return model

        for schema in schemas:
            schema_name = None

            if schema.__name__ == model:
                schema_name = schema.__name__
            elif schema == model:
                schema_name = model.__name__

            if schema_name:
                return self.schema_to_model_mapping.get(schema_name)

        for mdl in models:
            if mdl.__name__ == model or mdl == model:
                return mdl

        raise ValueError("Invalid model type.")

    def update_items(self, local_items: list = None, server_items: list = None):

        if local_items is not None:
            self.items.update({"local": local_items})

        if server_items is not None:
            self.items.update({"server": server_items})

        return self.items

    def insert_model_items(self, items: list = None):
        items = generate_dummy_data(self.model, self.length) if items is None else items

        print("Inserting items...", items)

        if self.current_session:
            if isinstance(items, List):
                for d in items:
                    try:
                        self.current_session.add(d)
                        self.current_session.commit()
                    except Exception as e:
                        print(e)

            else:
                try:
                    self.current_session.add(items)
                    self.current_session.commit()
                except Exception as e:
                    print(e)

            self.update_items(server_items=items)

        if self.current_conn:
            if not isinstance(items, list):
                items = [items]

            # insert_items(
            #     self.current_conn, self.local_table_name, items, self.column_names
            # )
            self.update_items(local_items=items)

        return self.items

    def list_model_items(self):

        if self.current_session:
            server_items = self.current_session.query(self.model).all()
            self.update_items(server_items=server_items)

        # if self.current_conn:
        #     local_items = select_items(
        #         self.current_conn,
        #         self.local_table_name,
        #         mapped_object_type=self.model,
        #         column_names=self.column_names,
        #     )
        #     self.update_items(local_items=local_items)

        return self.items

    def delete_model_items(self):

        if self.current_session:
            script_path = get_script_path("reset_table.sql")

            args = {"table_name": self.table_name, "sequence_id": self.sequence_id}
            run_postgres_script(script_path, args)

        # if self.current_conn:
        #     delete_items(
        #         self.current_conn, self.local_table_name, filter_condition=None
        #     )


if __name__ == "__main__":

    dummy_arguments = [
        Argument(name=("-m", "--model"), default="User"),
        Argument(
            name=("-a", "--action"),
            default="list",
            choices=["insert", "delete", "list"],
        ),
        Argument(name=("-l", "--length"), type=int, default=1),
        Argument(name=("-i", "--sequence_id"), type=str, default=None),
        Argument(name=("-t", "--table_name"), type=str, default=None),
    ]

    parser = Parser(parser_arguments=dummy_arguments)
    args = parser.get_command_args()

    dummy = Dummy(
        **args,
        models=models,
        schemas=schemas,
        schema_to_model_mapping=schema_to_model_mapping,
    )

    actions = {
        "insert": dummy.insert_model_items,
        "list": dummy.list_model_items,
        "delete": dummy.delete_model_items,
    }
    action = args.get("action")

    dummy.conn = conn
    dummy.session = get_db_object()
    print(actions.get(action)())
