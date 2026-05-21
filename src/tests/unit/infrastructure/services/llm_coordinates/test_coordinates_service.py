import json
from pathlib import Path

import pytest

from deps_ai_fusion.infrastructure.services import CoordinatesService
from deps_ai_fusion.infrastructure.services.llm_coordinates.model.string_matcher import (
    InputWord,
)
from deps_ai_fusion.infrastructure.services.llm_coordinates.string_matcher import (
    LayoutStringMatcherFactory,
)

_DATA_DIR = Path(__file__).parent / "data"

FIELD_RESPONSES = {
    "field_victoria": "Victoria Stokes",
    "field_enough": "are already enough",
    "field_dream": "dreamscrolling",
    "field_georgina": "Georgina believes",
    "field_screentime": "Screentime shame",
}

FIELD_RESPONSES_COORDINATES = [
    [
        {"x": 0.48583333333333334, "y": 0.3944799730730394, "w": 0.047083333333333366, "h": 0.008414675193537557},
        {"x": 0.5366666666666666, "y": 0.39481656008078087, "w": 0.040000000000000036, "h": 0.008078088185796028},
    ],
    [
        {"x": 0.735, "y": 0.9185459441265568, "w": 0.022083333333333344, "h": 0.007068327162571553},
        {"x": 0.7620833333333333, "y": 0.9151800740491417, "w": 0.053749999999999964, "h": 0.013800067317401576},
        {"x": 0.82, "y": 0.9151800740491417, "w": 0.057916666666666616, "h": 0.013463480309660047},
    ],
    [
        {"x": 0.15083333333333335, "y": 0.7034668461797374, "w": 0.12041666666666664, "h": 0.013463480309660047},
    ],
    [
        {"x": 0.10541666666666667, "y": 0.8091551666105689, "w": 0.12916666666666665, "h": 0.013126893301918519},
        {"x": 0.17625, "y": 0.8091551666105689, "w": 0.05833333333333332, "h": 0.010434197239986509},
    ],
    [
        {"x": 0.09625, "y": 0.5250757320767419, "w": 0.17041666666666666, "h": 0.012117132278694043},
        {"x": 0.20708333333333334, "y": 0.5257489060922248, "w": 0.05958333333333332, "h": 0.011443958263210985},
    ],
]


def _make_word(content: str, x: float = 0.0, y: float = 0.0, w: float = 0.1, h: float = 0.05) -> InputWord:
    # polygon as flat [x1,y1, x2,y2, x3,y3, x4,y4] for a rectangle
    return InputWord(
        content=content,
        page=0,
        polygon=[x, y, x + w, y, x + w, y + h, x, y + h],
        confidence=0.99,
    )


@pytest.fixture
def service():
    return CoordinatesService()


@pytest.fixture
def words():
    return [
        _make_word("Lot", x=0.10, y=0.20),
        _make_word("4", x=0.20, y=0.20),
        _make_word("Block", x=0.30, y=0.20),
        _make_word("12", x=0.40, y=0.20),
        _make_word("Oak", x=0.10, y=0.30),
        _make_word("Park", x=0.20, y=0.30),
    ]


# ── exact match ────────────────────────────────────────────────────────────────


def test_find_coordinates__exact_match_returns_words_in_order(service, words):
    result = service.find_coordinates(words, {"description": "Lot 4 Block 12"})

    assert [w["content"] for w in result["description"]] == ["Lot", "4", "Block", "12"]


def test_find_coordinates__result_words_carry_spatial_metadata(service, words):
    result = service.find_coordinates(words, {"field": "Lot"})
    word = result["field"][0]

    assert word["content"] == "Lot"
    assert "polygon" in word
    assert "page" in word
    assert "confidence" in word


# ── no match ───────────────────────────────────────────────────────────────────


def test_find_coordinates__unknown_text_returns_empty_list(service, words):
    result = service.find_coordinates(words, {"date": "January 2024"})

    assert result["date"] == []


# ── edge cases ─────────────────────────────────────────────────────────────────


def test_find_coordinates__empty_fields_returns_empty_dict(service, words):
    result = service.find_coordinates(words, {})

    assert result == {}


def test_find_coordinates__empty_words_returns_empty_list_per_field(service):
    result = service.find_coordinates([], {"description": "Lot 4"})

    assert result["description"] == []


def test_find_coordinates__empty_field_text_returns_empty_list(service, words):
    result = service.find_coordinates(words, {"field": ""})

    assert result["field"] == []


# ── multiple fields ─────────────────────────────────────────────────────────────


def test_find_coordinates__multiple_fields_mapped_independently(service, words):
    result = service.find_coordinates(words, {"lot": "Lot 4", "location": "Oak Park"})

    assert [w["content"] for w in result["lot"]] == ["Lot", "4"]
    assert [w["content"] for w in result["location"]] == ["Oak", "Park"]


def test_find_coordinates__all_fields_present_in_result(service, words):
    fields = {"a": "Lot", "b": "January 2024", "c": "Oak Park"}

    result = service.find_coordinates(words, fields)

    assert set(result.keys()) == {"a", "b", "c"}


# ── matcher interaction ──────────────────────────────────────────────────────────


def test_find_coordinates__returns_result_for_each_field(service, words):
    result = service.find_coordinates(words, {"f1": "Lot", "f2": "Block", "f3": "Oak"})

    assert len(result) == 3


def test_find_coordinates__matched_word_content_preserved(service):
    word = _make_word("Lot")

    result = service.find_coordinates([word], {"field": "Lot"})

    assert result["field"][0]["content"] == "Lot"


# ── real layout fixture ─────────────────────────────────────────────────────────


def test_find_coordinates__real_layout(service):
    dirr = "/app/tests/data/layout_response_text"
    with open(dirr) as f:
        layout = json.load(f)

    words = LayoutStringMatcherFactory._extract_words(layout)
    result = service.find_coordinates(words, FIELD_RESPONSES)
    print("RESULT", result)
    assert set(result.keys()) == set(FIELD_RESPONSES.keys())
    for field_name, matched_words in result.items():
        assert matched_words, f"{field_name!r}: expected matches for {FIELD_RESPONSES[field_name]!r}, got none"
        assert all("page" in w and "polygon" in w and "confidence" in w for w in matched_words)


def test_find_coordinates__real_layout_coordinates(service):
    dirr = "/app/tests/data/layout_response_text"
    with open(dirr) as f:
        layout = json.load(f)

    words = LayoutStringMatcherFactory._extract_words(layout)
    result = service.find_coordinates(words, FIELD_RESPONSES)
    print("RESULT", result)
    for field_name, expected_polygons in zip(FIELD_RESPONSES, FIELD_RESPONSES_COORDINATES):
        matched_words = result[field_name]
        assert len(matched_words) == len(
            expected_polygons
        ), f"{field_name!r}: expected {len(expected_polygons)} words, got {len(matched_words)}"
        for word, expected in zip(matched_words, expected_polygons):
            assert word["polygon"] == pytest.approx(
                expected
            ), f"{field_name!r}: polygon mismatch for word {word['content']!r}"


# ── input / output format ────────────────────────────────────────────────────────


def test_find_coordinates__input_accepts_flat_polygon(service):
    """find_coordinates() must accept words with polygon as list[float]."""
    word: InputWord = InputWord(
        content="Lot",
        page=0,
        polygon=[0.1, 0.2, 0.3, 0.2, 0.3, 0.4, 0.1, 0.4],
        confidence=0.99,
    )

    result = service.find_coordinates([word], {"field": "Lot"})

    assert result["field"] != []


def test_find_coordinates__output_polygon_is_bbox(service):
    """Each word in the result must have polygon as a Bbox dict (x, y, w, h)."""
    word: InputWord = InputWord(
        content="Lot",
        page=0,
        polygon=[0.1, 0.2, 0.3, 0.2, 0.3, 0.4, 0.1, 0.4],
        confidence=0.99,
    )

    result = service.find_coordinates([word], {"field": "Lot"})
    polygon = result["field"][0]["polygon"]

    assert set(polygon.keys()) == {"x", "y", "w", "h"}
    assert all(isinstance(v, float) for v in polygon.values())


def test_find_coordinates__output_bbox_values_correct(service):
    """Output Bbox must match the bounding box of the input flat polygon."""
    # Rectangle: (0.1, 0.2) to (0.3, 0.4) → w=0.2, h=0.2
    word: InputWord = InputWord(
        content="Lot",
        page=0,
        polygon=[0.1, 0.2, 0.3, 0.2, 0.3, 0.4, 0.1, 0.4],
        confidence=0.99,
    )

    result = service.find_coordinates([word], {"field": "Lot"})
    polygon = result["field"][0]["polygon"]

    assert polygon["x"] == pytest.approx(0.1)
    assert polygon["y"] == pytest.approx(0.2)
    assert polygon["w"] == pytest.approx(0.2)
    assert polygon["h"] == pytest.approx(0.2)
