"""Json (De-)serialization of the Croissant format

Typical usage:
    croissant_dict = json.load(f, object_hook=deserialize_croissant)
    json.dump(croissant_dict, f, default=serialize_croissant)
"""


import datetime
from collections import OrderedDict
from typing import Any

import dateutil.parser


def deserialize_croissant(dct: dict[str, Any]) -> dict[str, Any]:
    """
    In-place deserialization of a dictionary into their datatypes.

    Args:
        dct: a DCF dictionary containing raw values (e.g. a string instead of a datetime).

    Returns:
        a dictionary containing the proper datatypes (e.g. datetime instead of string).
    """
    deserialized = OrderedDict()
    for field, value in dct.items():
        if field.startswith("date"):
            datetime_ = dateutil.parser.parse(value)
            if len(value) == len("YYYY-MM-DD"):
                deserialized[field] = datetime_.date()
            else:
                deserialized[field] = datetime_
        else:
            deserialized[field] = value
    return deserialized


def serialize_croissant(obj: Any) -> str:
    """
    Serialize a field into the proper string representation

    Args:
        obj: any object that is not json serializable by default.

    Returns:
        the String representation of the object

    Raises:
        ValueError Object of type [type] not serializable
    """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    msg = f"Object of type {type(obj)} not serializable."
    raise ValueError(msg)
