"""Converting OpenML Dataset into a Croissant representation.

Typical usage:
    metadata_openml = openml.datasets.get_dataset(
        identifier,
        download_data=False,
        download_qualities=False,
        download_features_meta_data=True
    )
    croissant = converter.convert(metadata_openml)
"""

import re
from typing import Any, Iterator

import mlcroissant as mlc
from openml import OpenMLDataFeature, OpenMLDataset

from openml_croissant._src import conversion_outside_mlcroissant
from openml_croissant._src.settings import Settings

BOOLEAN_STRING_VALUES = ({"TRUE", "FALSE"}, {"1", "0"}, {"True", "False"}, {"true", "false"})
DATA_FILE_UID = "data-file"


def convert(dataset: OpenMLDataset, settings: Settings) -> dict[str, Any]:
    """
    Convert an openml dataset into a DCF (Croissant) representation.

    Args:
        dataset: The OpenML dataset metadata
        settings: The conversion configuration

    Returns
        a (validated) croissant json

    Raises:
        mlcroissant.ValidationError: error while validating the mlcroissant Metadata
        ValueError: Unknown datatype: [openml_datatype].
        ValueError: Weird datafile format
    """
    if not dataset.url or not dataset.url.endswith("arff"):
        msg = "Weird datafile format"
        raise ValueError(msg)

    distributions = [
        mlc.FileObject(
            name=DATA_FILE_UID,
            description="Data file belonging to the dataset.",
            content_url=dataset.url,
            encoding_format="text/plain",  # No official arff mimetype exist
            md5=dataset.md5_checksum,
        ),
    ]

    if len(dataset.features) <= settings.max_features:
        fields = [_field(dataset, feature, settings) for feature in dataset.features.values()]
        enum_record_sets = list(_enum_recordsets(dataset, settings))
    else:
        fields = []
        enum_record_sets = []

    data_file_recordset = mlc.RecordSet(
        name="data-file-description",
        description="Listing the fields of the data."
        if fields
        else "The fields are omitted, " "because this dataset has too " "many.",
        fields=fields,
    )
    record_sets = enum_record_sets + [data_file_recordset]

    metadata = mlc.Metadata(
        name=_sanitize_name_string(dataset.name),
        description=dataset.description,
        url=f"https://www.openml.org/search?type=data&id={dataset.dataset_id}",
        citation=dataset.citation or dataset.paper_url,
        license=dataset.licence,
        distribution=distributions,
        record_sets=record_sets,
    )
    croissant_json = metadata.to_json()
    croissant_json.update(conversion_outside_mlcroissant.metadata(dataset))
    return conversion_outside_mlcroissant.sorted_croissant(croissant_json)


def _sanitize_name_string(name: str) -> str:
    """Replace special characters with underscores.

    Args:
        name: a name of a json-ld object.

    Returns:
        a sanitized version of the name
    """
    return re.sub("[^a-zA-Z0-9\\-_.]", "_", name)


def _enum_recordsets(dataset: OpenMLDataset, settings: Settings) -> Iterator[mlc.RecordSet]:
    """Create a recordset for each feature that has nominal_values (an enumeration)"""
    for feature in dataset.features.values():
        if (
            feature.nominal_values
            and not _is_boolean(feature)
            and len(feature.nominal_values) <= settings.max_categories_per_enumeration
        ):
            name = _sanitize_name_string(feature.name)
            yield mlc.RecordSet(
                name=f"enumeration_{name}",  # prefix to avoid duplicate with dataset name
                description=f"Possible values for {name}",
                fields=[
                    mlc.Field(
                        name="value",
                        description=f"The value of {name}.",
                        data_types=[mlc.DataType.TEXT],
                    ),
                ],
                data=[{"value": value} for value in feature.nominal_values],
            )


def _field(dataset: OpenMLDataset, feature: OpenMLDataFeature, settings) -> mlc.Field:
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
    name = _sanitize_name_string(feature.name)
    datatype = _convert_datatype(feature)
    is_enumeration = (
        feature.nominal_values is not None
        and len(feature.nominal_values) > 0
        and datatype != mlc.DataType.BOOL
    )

    enumeration_omitted = (
        is_enumeration and len(feature.nominal_values) > settings.max_categories_per_enumeration
    )
    kwargs = {
        "name": f"feature_{feature.index}-{name}",  # the index assures the name is unique
        "description": _field_description(dataset, feature, enumeration_omitted),
        "data_types": datatype,
        "is_enumeration": is_enumeration,
        "source": mlc.Source(
            uid=DATA_FILE_UID,
            node_type="distribution",
            extract=mlc.Extract(column=feature.name),
        ),
    }
    if is_enumeration and not enumeration_omitted:
        kwargs["references"] = mlc.Source(uid=f"enumeration_{name}/value", node_type="field")
    return mlc.Field(**kwargs)


def _field_description(
    dataset: OpenMLDataset,
    feature: OpenMLDataFeature,
    enumeration_omitted: bool,
) -> str:
    """
    A field description for a feature.

    Args:
        dataset: The OpenML dataset metadata
        feature: The OpenML feature metadata
        enumeration_omitted: if true, this field is an enumeration, but it is not shown.

    Returns:
        A string that can be used as a description of the feature.
    """
    if dataset.default_target_attribute and feature.name in dataset.default_target_attribute.split(
        ",",
    ):
        field_type = "the default target field"
    elif dataset.row_id_attribute and feature.name in dataset.row_id_attribute:
        field_type = "the field that uniquely identifies each record, this field should be ignored"
    elif dataset.ignore_attribute and feature.name in dataset.ignore_attribute:
        field_type = "this field should be ignored"
    else:
        field_type = "a field"
    postfix = (
        (
            " - this field is configured as an enumeration, but the enumeration is omitted "
            "because there are too many values"
        )
        if enumeration_omitted
        else ""
    )
    return f"{feature.name} - {field_type}{postfix}."


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
    if _is_boolean(feature):
        return mlc.DataType.BOOL

    d_type = {
        "numeric": [mlc.DataType.FLOAT, mlc.DataType.INTEGER],
        "string": mlc.DataType.TEXT,
        "nominal": mlc.DataType.TEXT,
        "date": mlc.DataType.DATE,
    }.get(feature.data_type, None)
    if d_type is None:
        msg = f"Unknown datatype: {feature.data_type}."
        raise ValueError(msg)
    return d_type


def _is_boolean(feature) -> bool:
    """Return true if this feature is boolean"""
    return feature.nominal_values and any(
        set(feature.nominal_values).issubset(booleans) for booleans in BOOLEAN_STRING_VALUES
    )
