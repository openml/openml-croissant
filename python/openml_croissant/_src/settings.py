from pydantic import BaseModel


class Settings(BaseModel):
    """
    Configuration for the OpenML Croissant Converter.

    Args:
        max_categories_per_enumeration(int): if a categorical variable has more categories than
        this, the categories will not be described in a Croissant RecordSet.
        max_features(int): if an OpenML Dataset has more features than this, the features will
        not be described in the Croissant.
    """

    max_categories_per_enumeration: int = 50
    max_features: int = 200
