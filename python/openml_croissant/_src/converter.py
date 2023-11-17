import re

import mlcroissant as mlc
from openml import OpenMLDataFeature, OpenMLDataset

BOOLEAN_STRING_VALUES = ({"TRUE", "FALSE"}, {"1", "0"})
DATA_FILE_UID = "data-file"


def convert(dataset: OpenMLDataset) -> mlc.Metadata:
    """
    Convert an openml dataset into a DCF (Croissant) representation.

    Args:
        dataset: The OpenML dataset metadata

    Returns
        a (validated) croissant Metadata object.

    Raises:
        ValueError: Unknown datatype: [openml_datatype].
        ValueError: Weird datafile format
    """
    if not dataset.data_file or not dataset.data_file.endswith("arff"):
        msg = "Weird datafile format"
        raise ValueError(msg)

    distributions = [
        mlc.FileObject(
            name=DATA_FILE_UID,
            description="Data file belonging to the dataset.",
            content_url=dataset.data_file,
            encoding_format="text/plain",  # No official arff mimetype exist
            md5=dataset.md5_checksum,
        ),
    ]

    record_sets = [
        mlc.RecordSet(
            name="data-file-description",
            fields=[_field(dataset, feature) for feature in dataset.features.values()],
        ),
    ]

    return mlc.Metadata(
        name=dataset.name,
        description=dataset.description,
        url=f"https://www.openml.org/search?type=data&id={dataset.dataset_id}",
        citation=dataset.citation,
        license=dataset.licence,
        distribution=distributions,
        record_sets=record_sets,
    )


def _sanitize_name_string(name: str) -> str:
    """Replace special characters with underscores, and transform to lower case.

    Args:
        name: a name of a json-ld object.

    Returns:
        a sanitized version of the name
    """
    return re.sub("[^A-Za-z0-9]", "_", name).lower()


def _field(dataset: OpenMLDataset, feature: OpenMLDataFeature) -> mlc.Field:
    """
    A croissant field description for this OpenML feature.


    Args:
        dataset: The OpenML dataset metadata
        feature: The OpenML feature metadata

    Returns:
        A croissant Field

    Raises:
        ValueError: Unknown datatype: [openml_datatype].
    """
    datatypes = _convert_datatype(feature)
    is_enumeration = feature.nominal_values and datatypes != mlc.DataType.BOOL
    description = _field_description(dataset, feature)

    return mlc.Field(
        name=_sanitize_name_string(feature.name),
        description=description,
        data_types=datatypes,
        is_enumeration=is_enumeration,
        source=mlc.Source(
            uid=DATA_FILE_UID,
            node_type="distribution",
            extract=mlc.Extract(column=feature.name),
        ),
    )


def _field_description(dataset: OpenMLDataset, feature: OpenMLDataFeature) -> str:
    """
    A field description for a feature.

    Args:
        dataset: The OpenML dataset metadata
        feature: The OpenML feature metadata

    Returns:
        A string that can be used as a description of the feature.
    """
    if dataset.default_target_attribute and feature.name in dataset.default_target_attribute.split(
        ",",
    ):
        # TODO: should Field.default_target be part of croissant?
        field_type = "the default target field"
    elif dataset.row_id_attribute and feature.name in dataset.row_id_attribute:
        field_type = "the field that uniquely identifies each record, this field should be ignored"
    elif dataset.ignore_attribute and feature.name in dataset.ignore_attribute:
        # TODO: should Field.ignored be part of croissant?
        field_type = "this field should be ignored"
    else:
        field_type = "a field"
    return f"{feature.name} - {field_type}."


def _convert_datatype(feature: OpenMLDataFeature) -> mlc.DataType | list[mlc.DataType]:
    """
    Convert the datatype according to OpenML to a croissant datatype.

    Args:
        feature: The OpenML Feature

    Returns:
        The croissant datatype, or a list of possible croissant datatypes

    Raises:
        ValueError: Unknown datatype: [openml_datatype].
    """
    if feature.nominal_values and any(
        set(feature.nominal_values).issubset(booleans) for booleans in BOOLEAN_STRING_VALUES
    ):
        return mlc.DataType.BOOL

    d_type = {
        "numeric": [mlc.DataType.FLOAT, mlc.DataType.INTEGER],
        "string": mlc.DataType.TEXT,
        "nominal": mlc.DataType.TEXT,  # TODO: where to add the possible values?
    }.get(feature.data_type, None)
    if d_type is None:
        msg = f"Unknown datatype: {feature.data_type}."
        raise ValueError(msg)
    return d_type
