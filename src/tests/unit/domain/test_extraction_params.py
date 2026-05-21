import pytest

from deps_ai_fusion.domain.exceptions import IllegalArgument
from deps_ai_fusion.domain.model import ExtractionParams


def test_extraction_params__create_updated():
    extraction_params = ExtractionParams()
    updated_extraction_params = extraction_params.create_updated(
        custom_instruction=(custom_instruction := extraction_params.custom_instruction + "test instruction"),
        grouping_factor=(grouping_factor := extraction_params.grouping_factor + 10),
        temperature=(temperature := 0.5),
        top_p=(top_p := 0.5),
    )

    assert updated_extraction_params.custom_instruction == custom_instruction
    assert updated_extraction_params.grouping_factor == grouping_factor
    assert updated_extraction_params.temperature == temperature
    assert updated_extraction_params.top_p == top_p


def test_extraction_params__with_all_parameters__ok():
    params = ExtractionParams(
        custom_instruction="Extract data",
        grouping_factor=3,
        temperature=0.5,
        top_p=0.9,
        max_tokens=1000,
        stop=["END"],
        seed=42,
    )

    assert params.custom_instruction == "Extract data"
    assert params.grouping_factor == 3
    assert params.temperature == 0.5
    assert params.top_p == 0.9
    assert params.max_tokens == 1000
    assert params.stop == ["END"]
    assert params.seed == 42


def test_extraction_params__default_to_none__ok():
    params = ExtractionParams(
        custom_instruction="Extract",
        temperature=0.5,
    )

    assert params.max_tokens is None
    assert params.stop is None
    assert params.seed is None


def test_extraction_params__max_tokens_validation__error():
    with pytest.raises(IllegalArgument):
        ExtractionParams(max_tokens=0)

    with pytest.raises(IllegalArgument):
        ExtractionParams(max_tokens=-100)
