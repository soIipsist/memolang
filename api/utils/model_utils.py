from sqlalchemy.orm import Session, class_mapper
from pydantic import BaseModel, Field, create_model
from typing import Dict, Optional, Union, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pydantic.fields import FieldInfo


from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    inspect,
)
import random
import string
from datetime import date, datetime, timedelta
from typing import List

from utils.func_utils import (
    get_callable_args,
    get_class_fields_and_types,
    get_required_args,
)
from utils.random_utils import (
    random_string,
    random_bool,
    random_date,
    random_datetime,
    random_float,
    random_int,
)


def insert_model_to_db(
    db: Session, schemas: Union[BaseModel, List[BaseModel]], model_type: type
):
    """
    Inserts a new record or records into the database based on the provided schema(s) and model type.
    """

    if not isinstance(schemas, list):
        schemas = [schemas]

    instances = []

    for schema in schemas:
        if not isinstance(schema, BaseModel):  # this is a model, not a schema
            schema = convert_model_to_schema(schema)

        model_data = schema.model_dump()
        model_instance = model_type(**model_data)
        db.add(model_instance)
        instances.append(model_instance)
        db.commit()

    for instance in instances:
        db.refresh(instance)

    return instances if len(instances) > 1 else instances[0]


def upsert_model_to_db(
    db: Session,
    schema: BaseModel,
    model_type: type,
    condition: tuple,
    excluded_keys=["id"],
) -> BaseModel:
    """
    Inserts a new record or updates an existing record in the database based on the provided schema, model type, and condition.
    """

    instance = (
        db.query(model_type).filter(*condition).first()
        if isinstance(condition, tuple)
        else db.query(model_type).filter(condition).first()
    )

    if not isinstance(schema, BaseModel):
        schema = convert_model_to_schema(schema)

    if instance:
        # Update existing instance
        for key, value in schema.model_dump().items():
            if key not in excluded_keys:
                setattr(instance, key, value)
    else:
        # Create new instance
        model_data = schema.model_dump()
        instance = model_type(**model_data)
        db.add(instance)

    db.commit()
    db.refresh(instance)

    return instance


def upsert_models_to_db(
    db: Session,
    schemas: Union[BaseModel, List[BaseModel]],
    model_type: type,
    conditions: Optional[Union[dict, List[dict]]] = None,
    excluded_keys: List[str] = ["id"],
) -> Union[BaseModel, List[BaseModel]]:
    """
    Inserts new records or updates existing records in the database for multiple schemas using the upsert_model_to_db function.
    """

    if not isinstance(schemas, list):
        schemas = [schemas]

    if conditions and not isinstance(conditions, list):
        conditions = [conditions]

    updated_instances = []

    for idx, schema in enumerate(schemas):
        condition = conditions[idx] if idx < len(conditions) else None

        instance = upsert_model_to_db(
            db=db,
            schema=schema,
            model_type=model_type,
            condition=condition,
            excluded_keys=excluded_keys,
        )
        updated_instances.append(instance)

    return updated_instances if len(updated_instances) > 1 else updated_instances[0]


def get_multiple_filter_conditions(
    model, schemas: List[BaseModel], attribute: str, operator: str = "=="
) -> List[Dict[str, Union[str, int]]]:
    """
    Generate filter conditions for multiple schemas based on the given attribute and operator.

    """

    op_map = {
        "==": lambda col, val: col == val,
        "!=": lambda col, val: col != val,
        ">": lambda col, val: col > val,
        "<": lambda col, val: col < val,
        ">=": lambda col, val: col >= val,
        "<=": lambda col, val: col <= val,
    }

    if operator not in op_map:
        raise ValueError(f"Unsupported operator: {operator}")

    conditions = []
    for schema in schemas:
        value = getattr(schema, attribute, None)
        if value is not None:
            column = getattr(model, attribute)
            condition = op_map[operator](column, value)
            conditions.append(condition)

    return conditions


def is_column_of_type(model, column_name, column_type):
    """
    Checks if a given column in the model is of ARRAY type.
    """
    mapper = inspect(model)
    for column in mapper.columns:
        if column.name == column_name:
            return isinstance(column.type, column_type)
    return False


def parse_array_string(array_str: str):
    """
    Converts a string representation of an array into a Python list.
    """
    if "[" in array_str:
        array_str = array_str.replace("[", "")

    if "]" in array_str:
        array_str = array_str.replace("]", "")

    if "," in array_str:
        return array_str.split(",")

    return [array_str]


def convert_sqlalchemy_column_to_default(column: Column):
    if column.default is not None and column.default.is_scalar:
        return column.default.arg
    elif column.nullable:
        return None
    else:
        if isinstance(column.type, String):
            return random_string()
        elif isinstance(column.type, Integer):
            return random_int()
        elif isinstance(column.type, Float):
            return random_float()
        elif isinstance(column.type, Boolean):
            return random_bool()
        elif isinstance(column.type, DateTime):
            return random_datetime()
        elif isinstance(column.type, Date):
            return random_date()
        else:
            return None


def get_field_value(target_schema_or_model, field, field_type: type):
    value = None
    if field_type == str:
        value = random_string()
    elif field_type == int:
        value = random_int()
    elif field_type == float:
        value = random_float()
    elif field_type == bool:
        value = random_bool()
    elif field_type == datetime:
        value = random_datetime()
    elif field_type == date:
        value = random_date()
    elif field_type == List[str]:
        value = [random_string() for _ in range(random_int(1, 5))]
    elif field_type == List[int]:
        value = [random_int() for _ in range(random_int(1, 5))]
    elif field_type == List[float]:
        value = [random_float() for _ in range(random_int(1, 5))]
    elif field_type == List[bool]:
        value = [random_bool() for _ in range(random_int(1, 5))]
    elif field_type == List[datetime]:
        value = [random_datetime() for _ in range(random_int(1, 5))]
    else:
        if hasattr(target_schema_or_model, "__fields__"):
            fields = target_schema_or_model.__fields__
            val = fields.get(field)
            val: FieldInfo
            value = val.default  # default to FieldInfo default for unsupported types
        else:
            model_columns = [c for c in class_mapper(target_schema_or_model).columns]

            for column in model_columns:
                field_name = column.name
                default_value = convert_sqlalchemy_column_to_default(column)
                value = default_value
    return value


def generate_dummy_data(target_schema_or_model: type, length: int = 1):
    if length <= 0:
        length = 1

    def generate_dummy_instance():
        dummy_instance = {}

        fields, field_types = get_class_fields_and_types(target_schema_or_model)

        for field, field_type in zip(fields, field_types):
            dummy_instance[field] = get_field_value(
                target_schema_or_model, field, field_type
            )

        required_args = get_required_args(target_schema_or_model.__init__)

        data = target_schema_or_model(**required_args)

        for k, v in dummy_instance.items():
            setattr(data, k, v)
        return data

    if length > 1:
        return [generate_dummy_instance() for _ in range(0, length)]
    else:
        return generate_dummy_instance()


def get_default_value(column: Column):
    """
    Get the default value of a column if specified, otherwise return None.
    """
    if column.default is not None and column.default.is_scalar:
        return column.default.arg
    if column.nullable:
        return None
    return ...


def convert_model_to_schema(model_instance):
    if isinstance(model_instance, BaseModel):
        return model_instance

    model_class = model_instance.__class__
    model_fields = {
        column.name: (
            (
                Optional[column.type.python_type]
                if column.nullable
                else column.type.python_type
            ),
            Field(default=get_default_value(column)),
        )
        for column in class_mapper(model_class).columns
    }
    TempSchema = create_model(f"TempSchema_{model_class.__name__}", **model_fields)

    instance_data = {
        column.name: getattr(model_instance, column.name)
        for column in class_mapper(model_class).columns
    }
    return TempSchema(**instance_data)


def convert_schema_to_model(schema, target_model_type):
    if isinstance(schema, BaseModel):
        return target_model_type(**schema.model_dump())

    raise TypeError("schema is not an instance of BaseModel.")


def get_schema_to_model_mapping(schemas: list, models: list) -> Dict[str, str]:
    schema_to_model_mapping = {}

    model_lookup = {model.__name__: model for model in models}

    for schema in schemas:
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            schema_name = schema.__name__

            for model_name in model_lookup:
                if model_name in schema_name:
                    schema_to_model_mapping[schema_name] = model_lookup[model_name]

    return schema_to_model_mapping


def get_model_table(
    target_schema_or_model: type,
    schema_to_model_mapping: dict,
):

    if hasattr(target_schema_or_model, "__tablename__"):
        return getattr(target_schema_or_model, "__tablename__")
    else:
        target_schema_or_model: BaseModel
        return schema_to_model_mapping.get(target_schema_or_model).__tablename__


def get_model_sequence_id(
    target_schema_or_model: type, schema_to_model_mapping: dict, sequence_id: str = None
):
    if isinstance(target_schema_or_model, BaseModel):  # this is a schema
        target_schema_or_model = schema_to_model_mapping.get(target_schema_or_model)

    if sequence_id is None:
        sequence_id = "id"

    id_column = next(
        (
            c
            for c in class_mapper(target_schema_or_model).columns
            if c.name == sequence_id
        ),
        None,
    )

    return id_column.name
