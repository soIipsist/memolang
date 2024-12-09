from inspect import Parameter, getmembers, signature
from typing import Any, List, get_type_hints

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    Integer,
    String,
    Tuple,
)
from sqlalchemy.ext.hybrid import hybrid_property


def get_class_args(cls) -> dict:

    if not isinstance(cls, type):
        return vars(cls)
    else:
        return {
            key: val
            for key, val in cls.__dict__.items()
            if not key.startswith("_") and not key.startswith("__")
        }


def is_hybrid_property(cls, attr_name: str):
    model_attr = getattr(cls, attr_name)
    val = getattr(model_attr, "descriptor", None)
    return isinstance(val, hybrid_property) if val else False


def get_hybrid_properties(cls):
    properties = []

    if not isinstance(cls, type):
        cls = cls.__class__

    for attr_name, attr in getmembers(cls):
        if is_hybrid_property(cls, attr_name):
            properties.append(attr_name)

    return list(set(properties))


def get_callable_args(func, args: dict = None) -> dict:
    """Given a function, return all of its arguments with default values included."""

    if not callable(func):
        raise ValueError("not a function")

    func_signature = signature(func)
    func_params = {param.name: param for param in func_signature.parameters.values()}

    func_dict = {}
    for key, param in func_params.items():
        if key != "self" and key != "kwargs" and key != "args":
            p = None if param.default == param.empty else param.default
            if args and args.get(key):
                p = args.get(key)
            func_dict.update({key: p})
    return func_dict


def get_required_args(func):
    """Get only the required arguments of a method, excluding 'self' and optional ones."""
    sig = signature(func)
    required_args = {
        k: v.default if v.default is not v.empty else None
        for k, v in sig.parameters.items()
        if v.default is v.empty
        and v.kind in {Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD}
        and k != "self"
    }
    return required_args


def populate_object(obj: object, args: dict):
    """Populates an object with arguments or instantiates an object of the specified type."""

    if not isinstance(args, dict):
        raise ValueError("not a dictionary")

    if isinstance(obj, type):
        obj = obj(**args)

    if not isinstance(obj, object):
        raise ValueError("not an object")

    for key, val in args.items():
        setattr(obj, key, val)

    return obj


def get_common_object_args(obj1: object, obj2: object):
    """Returns common arguments between two objects."""

    vars1 = vars(obj1)
    vars2 = vars(obj2)

    common_attributes = set(vars1.keys()) & set(vars2.keys())

    common_args = {attr: vars1[attr] for attr in common_attributes}
    return common_args


def get_common_callable_args(callables: list):
    """Given a list of callables, return all parameters that have a common name."""

    if not isinstance(callables, list):
        callables = [callables]

    params = [set(signature(c).parameters.keys()) for c in callables]

    common_params = set.intersection(*params) if params else set()

    return list(common_params)


def get_object_of_type(
    obj_type: type,
    obj: object = None,
):
    """Given a type, return an object of that type. If an object is provided, set common attributes between the newly created object and the target."""
    init_args = get_required_args(obj_type)
    new_obj = obj_type(**init_args) if init_args else obj_type()

    if obj is not None:
        for attr in dir(obj):
            if not attr.startswith("__") and hasattr(new_obj, attr):
                setattr(new_obj, attr, getattr(obj, attr))

    return new_obj


def get_class_fields_and_types(cls):
    from sqlalchemy.inspection import inspect

    field_names = []
    field_types = []

    mapper = inspect(cls)
    for column in mapper.columns:

        column_name = column.key
        # Map column types to Python types manually
        if isinstance(column.type, String):
            column_type = str
        elif isinstance(column.type, Integer):
            column_type = int
        elif isinstance(column.type, Boolean):
            column_type = bool
        elif isinstance(column.type, Float):
            column_type = float
        elif isinstance(column.type, Date):
            column_type = str  # Date might be converted to string
        elif isinstance(column.type, DateTime):
            column_type = str  # DateTime might be converted to string
        elif isinstance(column.type, Enum):
            column_type = str  # Enum is usually mapped to string
        else:
            # Default to Any if we can't determine the type
            column_type = Any

        if column_name.startswith("_"):  # this is a hybrid property
            column_name = column_name.replace("_", "", 1)

        if column.primary_key and "id" in column.key:
            continue
        field_names.append(column_name)
        field_types.append(column_type)
    return field_names, field_types
