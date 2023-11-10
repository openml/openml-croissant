import mlcroissant as mlc
import openml


def convert(openml_metadata: openml.datasets.OpenMLDataset) -> mlc.nodes.Metadata:
    return mlc.nodes.Metadata(
        name=openml_metadata.name,
        url=openml_metadata.url,
        citation=openml_metadata.citation,
        license=openml_metadata.licence,
    )
