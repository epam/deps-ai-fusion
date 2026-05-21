import pytest

from deps_ai_fusion.domain.exceptions import InvariantViolationError
from deps_ai_fusion.domain.model import Cardinality, DataShape, DataType


def test_data_shape_not_applicable_cardinality__error():
    with pytest.raises(InvariantViolationError):
        DataShape(data_type=DataType.STRING, cardinality=Cardinality.SCALAR, include_aliases=True)
