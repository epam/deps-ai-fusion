import re

from ..model.string_matcher.types import Bbox


def bbox_from_flat_polygon(polygon: list[float]) -> Bbox:
    """
    Compute an axis-aligned bounding box from a flat polygon of any size.

    Accepts [x1, y1, x2, y2, ..., xN, yN] with N >= 1 points (2, 4, 6, or more).
    If the list has an odd length the last element is ignored.

    Returns Bbox(x, y, w, h) where x/y is the top-left corner and w/h the dimensions.
    Returns a zero bbox for an empty polygon.
    """
    coords = polygon if len(polygon) % 2 == 0 else polygon[:-1]
    if not coords:
        return Bbox(x=0.0, y=0.0, w=0.0, h=0.0)
    xs = coords[0::2]
    ys = coords[1::2]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    return Bbox(x=x_min, y=y_min, w=x_max - x_min, h=y_max - y_min)


def find_substring_matches(origin_string: str, substring: str) -> list[int]:
    """
    Return the start character offsets of all whole-word occurrences of substring
    within origin_string.

    Uses word-boundary anchors (\\b) so "lot" does not match inside "allotment".
    re.escape ensures special regex characters in substring are treated literally.
    """
    start_points = []
    pattern = rf"\b{re.escape(substring)}\b"

    for match in re.finditer(pattern, origin_string):
        start_points.append(match.start())
    return start_points


def binary_search_first_higher(arr: list[int], target: int) -> int:
    """
    Return the index of the first element in arr that is strictly greater than target.

    arr must be sorted in ascending order.
    Returns -1 if no such element exists.
    """
    left, right = 0, len(arr) - 1
    result = -1

    while left <= right:
        mid = (left + right) // 2
        if arr[mid] > target:
            result = mid
            right = mid - 1
        else:
            left = mid + 1

    return result


def binary_search_last_lower(arr: list[int], target: int) -> int:
    """
    Return the index of the last element in arr that is strictly less than target.

    arr must be sorted in ascending order.
    Returns -1 if no such element exists.
    """
    low, high = 0, len(arr) - 1
    result = -1

    while low <= high:
        mid = (low + high) // 2
        if arr[mid] < target:
            result = mid
            low = mid + 1
        else:
            high = mid - 1

    return result
