"""Part of the converting of OpenML Dataset into a Croissant representation, that is not
integrated into mlcroissant package.

Currently, many fields are not implemented in the mlcroissant package, see
https://github.com/mlcommons/croissant/discussions/370. We need to discuss that, and probably add
extra fields to mlcroissant. TODO: once that is done, we can integrate the functions of this file
into the converter.
"""

import datetime
from collections import OrderedDict
from functools import partial
from typing import Any, Callable

import dateutil.parser
import langcodes
from mlcroissant._src.core.json_ld import remove_empty_values
from openml import OpenMLDataset

LARGE_FIELDS = ("distribution", "recordSet")


def metadata(dataset: OpenMLDataset) -> dict[str, Any]:
    """Return a dictionary with the schema.org/Dataset fields and values that are not yet
    integrated into the mlcroissant package."""
    _ds = partial(_get_field, obj=dataset)  # get field from the openml dataset
    return remove_empty_values(
        {
            "version": dataset.version,
            "creator": _ds(
                field="creator",
                transform=lambda v: [_person(p) for p in v.split(", ")],
            ),
            "contributor": _ds(field="contributor", transform=_person),
            "dateCreated": _ds(field="upload_date", transform=dateutil.parser.parse),
            "dateModified": _ds(field="processing_date", transform=dateutil.parser.parse),
            "datePublished": _ds(field="collection_date", transform=_lenient_date_parser),
            "inLanguage": _ds(field="language", transform=lambda v: langcodes.find(v).language),
            "isAccessibleForFree": True,
            "license": _ds(field="licence"),
            "creativeWorkStatus": _ds(field="status"),
            "keywords": _ds(field="tag"),
            "sameAs": _ds(field="original_data_url"),
        },
    )


def _get_field(obj: object, field: str, transform: Callable | None = None) -> Any | None:
    """
    Get a field from an object optionally perform the transformation. This is a convenience
    function.

    Args:
        obj: Any object.
        field: A string containing the field name
        transform: A function to be applied to the resulting value. If None, no transformation
          will be applied.

    Returns:
        The value of the field, whereby the transformation (if any) is applied, or None if the
        field is not present and not required.

    Raises:
        Any error from the transformation function
    """
    val = getattr(obj, field, None)
    if val and transform is not None:
        return transform(val)
    return val


def _person(name: str) -> dict | None:
    """
    A dictionary with json-ld fields for a https://schema.org/Person

    Args:
        name: The name of the person

    Returns:
        A dictionary with json-ld fields for a schema.org Person, or None if the name is not
        present.
    """
    if not name:
        return None
    person = OrderedDict()
    person["@type"] = "sc:Person"
    person["name"] = name
    return person


def _lenient_date_parser(value: str) -> datetime.date | datetime.datetime:
    """
    Try to parse the value as a date or datetime.

    This can handle any string that dateutil.parser can parse, such as "2000-01-01T00:00:00",
    but also only a year, such as "2000"

    Args:
        value: a date-like string

    Returns:
        A datetime if the date and time are specified, or a date if the time is not specified.

    Raises:
        dateutil.parser.ParserError: Unknown date/datetime format.
    """
    if len(value) == len("YYYY") and (value.startswith("19") or value.startswith("20")):
        year = int(value)
        return datetime.date(year, 1, 1)
    return dateutil.parser.parse(value)


def sorted_croissant(croissant_json: dict[str, Any]) -> dict[str, Any]:
    """
    Make sure that the croissant is sorted consistently: first all the fields sorted
    alphabetically, except the two large fields (distribution and recordSet). Then the two large
    fields.

    Args:
        value: a date-like string

    Returns:
        A datetime if the date and time are specified, or a date if the time is not specified.

    Raises:
        dateutil.parser.ParserError: Unknown date/datetime format.
    """
    sorted_croissant_json = OrderedDict(
        [
            (key, croissant_json[key])
            for key in sorted(croissant_json.keys())
            if key not in LARGE_FIELDS
        ],
    )
    for field_name in LARGE_FIELDS:
        sorted_croissant_json[field_name] = croissant_json[field_name]
    return sorted_croissant_json
