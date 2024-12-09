import sqlite3
from sqlalchemy.orm import Session, class_mapper
from pydantic import BaseModel, Field, create_model
from typing import Dict, Optional, Union, List
from sqlalchemy.orm import Session, DeclarativeMeta
from pydantic import BaseModel
from pydantic.fields import FieldInfo
import os
from sqlalchemy import Operators


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


def random_string(length=10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def random_int(min_val=0, max_val=10):
    return random.randint(min_val, max_val)


def random_float(min_val=0.0, max_val=10.0):
    return random.uniform(min_val, max_val)


def random_bool():
    return random.choice([True, False])


def random_datetime(start_date=datetime(2000, 1, 1), end_date=datetime(2024, 7, 4)):
    return start_date + timedelta(days=random.randint(0, (end_date - start_date).days))


def random_date(start_date=date(1970, 1, 1), end_date=date.today()):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)
