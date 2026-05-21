import pytest

from deps_ai_fusion.infrastructure.services.llm_coordinates.model.string_matcher import (
    Bbox,
)
from deps_ai_fusion.infrastructure.services.llm_coordinates.string_matcher.utils import (
    bbox_from_flat_polygon,
)


def test_empty_polygon_returns_zero_bbox():
    result = bbox_from_flat_polygon([])
    assert result == Bbox(x=0.0, y=0.0, w=0.0, h=0.0)


def test_single_point():
    result = bbox_from_flat_polygon([3.0, 7.0])
    assert result == Bbox(x=3.0, y=7.0, w=0.0, h=0.0)


def test_rectangle_four_points():
    # Points: (1,2), (5,2), (5,8), (1,8)
    polygon = [1.0, 2.0, 5.0, 2.0, 5.0, 8.0, 1.0, 8.0]
    result = bbox_from_flat_polygon(polygon)
    assert result == Bbox(x=1.0, y=2.0, w=4.0, h=6.0)


def test_triangle_three_points():
    # Points: (0,0), (4,0), (2,3)
    polygon = [0.0, 0.0, 4.0, 0.0, 2.0, 3.0]
    result = bbox_from_flat_polygon(polygon)
    assert result == Bbox(x=0.0, y=0.0, w=4.0, h=3.0)


def test_odd_length_ignores_last_element():
    # Same triangle as above but with an extra dangling float at the end
    polygon = [0.0, 0.0, 4.0, 0.0, 2.0, 3.0, 99.0]
    result = bbox_from_flat_polygon(polygon)
    assert result == Bbox(x=0.0, y=0.0, w=4.0, h=3.0)


def test_negative_coordinates():
    # Points: (-3,-5), (2,1)
    polygon = [-3.0, -5.0, 2.0, 1.0]
    result = bbox_from_flat_polygon(polygon)
    assert result == Bbox(x=-3.0, y=-5.0, w=5.0, h=6.0)


def test_all_points_collinear_horizontally():
    # Points on same y: (1,4), (3,4), (7,4)
    polygon = [1.0, 4.0, 3.0, 4.0, 7.0, 4.0]
    result = bbox_from_flat_polygon(polygon)
    assert result == Bbox(x=1.0, y=4.0, w=6.0, h=0.0)


def test_all_points_collinear_vertically():
    # Points on same x: (2,1), (2,5), (2,9)
    polygon = [2.0, 1.0, 2.0, 5.0, 2.0, 9.0]
    result = bbox_from_flat_polygon(polygon)
    assert result == Bbox(x=2.0, y=1.0, w=0.0, h=8.0)


def test_unordered_points():
    # Points scattered: (5,3), (1,9), (8,0), (2,6)
    polygon = [5.0, 3.0, 1.0, 9.0, 8.0, 0.0, 2.0, 6.0]
    result = bbox_from_flat_polygon(polygon)
    assert result == Bbox(x=1.0, y=0.0, w=7.0, h=9.0)


def test_float_precision():
    polygon = [0.1, 0.2, 0.4, 0.5]
    result = bbox_from_flat_polygon(polygon)
    assert result["x"] == pytest.approx(0.1)
    assert result["y"] == pytest.approx(0.2)
    assert result["w"] == pytest.approx(0.3)
    assert result["h"] == pytest.approx(0.3)
