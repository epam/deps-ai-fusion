import math
from collections import defaultdict

import numpy as np

from ..model.string_matcher.models import QueryWord
from ..model.string_matcher.types import (
    BaseCases,
    OcrWordIndex,
    PositionCostEntry,
    WordToPositions,
)
from .utils import binary_search_first_higher, binary_search_last_lower

DefaultIndexCost: PositionCostEntry = (0, -1)
MAX_GAP = 50
_NUMPY_THRESHOLD = 400


def _build_word_to_positions(words: list[str]) -> WordToPositions:
    """
    Build an inverted index mapping each unique word to all OCR positions where it appears.

    Example:
        ["lot", "4", "block", "lot"] -> {"lot": [0, 3], "4": [1], "block": [2]}
    """
    word2positions = defaultdict(list)
    for idx, word in enumerate(words):
        word2positions[word].append(idx)
    return word2positions


def _build_base_cases(positions: list[OcrWordIndex]) -> BaseCases:
    """
    Build the DP base-case entries for the first matched query word.

    Each position gets cost=0 and prev_index=-1, meaning it is a valid
    starting point with no predecessor.

    Example:
        positions=[0, 3] -> {0: (0, -1), 3: (0, -1)}
    """
    return {position: DefaultIndexCost for position in positions}


def find_first_match(
    substring_words: list[str],
    word2positions: WordToPositions,
) -> tuple[list[QueryWord], list[QueryWord], int]:
    """
    Scan query words from left to right and stop at the first one that has any
    occurrence in the OCR document.

    All query words before that first match are recorded as unmatched. The first
    matching query word is recorded as matched with base-case DP entries (cost=0,
    prev=-1 for every candidate OCR position).

    Returns:
        matched_words:    list containing only the first matched QueryWord (or empty).
        unmatched_words:  list of all QueryWords before the first match.
        first_match_idx:  index in substring_words of the first matched word (0 if
                          no match was found, but matched_words will be empty).
    """
    matched_words, unmatched_words = [], []
    first_match_idx = 0

    for idx in range(len(substring_words)):
        subword = substring_words[idx]
        base_cases = _build_base_cases(word2positions.get(subword, []))
        word = QueryWord(
            value=subword,
            position=idx,
            index_cost=base_cases,
        )

        if not base_cases:
            unmatched_words.append(word)
        else:
            matched_words.append(word)
            first_match_idx = idx
            break

    return matched_words, unmatched_words, first_match_idx


def extend_matched_path(
    substring_words: list[str],
    word_to_positions: WordToPositions,
    matched_words: list[QueryWord],
    unmatched_words: list[QueryWord],
    first_match_idx: int,
) -> None:
    """
    Run the DP forward pass from first_match_idx+1 to the end of the query.

    For each subsequent query word, consider every OCR position where it appears.
    For each candidate position, find the cheapest way to arrive from any candidate
    position of the most-recently matched query word:

        cost = prev_cost + (curr_position - prev_position - 1)

    The "-1" means adjacent words (gap of 0 skipped words) cost zero.
    A gap of k skipped OCR words costs k.

    For large inputs uses numpy with searchsorted to limit each prev-position window
    to MAX_GAP entries instead of the full C×P matrix. For small inputs uses a
    pure-Python binary-search path to avoid numpy allocation overhead.

    Mutates matched_words and unmatched_words in place.
    Returns both lists (same objects) for convenience.
    """
    m = len(substring_words)
    for i in range(first_match_idx + 1, m):
        curr_word = substring_words[i]
        curr_positions = word_to_positions.get(curr_word, [])

        if not curr_positions or not matched_words[-1].index_cost:
            word = QueryWord(value=curr_word, position=i, index_cost={})
            unmatched_words.append(word)
            continue

        prev_index_cost = matched_words[-1].index_cost
        prev_pos_list = list(prev_index_cost.keys())  # sorted by construction
        effective_window = min(len(prev_pos_list), MAX_GAP)
        temporal_row = {}

        if len(curr_positions) * effective_window >= _NUMPY_THRESHOLD:
            prev_pos_arr = np.array(prev_pos_list, dtype=np.int64)
            prev_cost_arr = np.array([prev_index_cost[p][0] for p in prev_pos_list], dtype=np.float64)
            curr_pos_arr = np.array(curr_positions, dtype=np.int64)
            lo_arr = np.searchsorted(prev_pos_arr, curr_pos_arr - MAX_GAP)
            hi_arr = np.searchsorted(prev_pos_arr, curr_pos_arr)
            for idx, curr_pos in enumerate(curr_positions):
                lo, hi = int(lo_arr[idx]), int(hi_arr[idx])  # type: ignore
                if lo >= hi:
                    continue
                window_pos = prev_pos_arr[lo:hi]
                costs = prev_cost_arr[lo:hi] + (curr_pos - window_pos - 1)
                best_j = int(np.argmin(costs))
                temporal_row[curr_pos] = (float(costs[best_j]), int(window_pos[best_j]))
        else:
            for curr_pos in curr_positions:
                lo = binary_search_first_higher(prev_pos_list, curr_pos - MAX_GAP - 1)
                hi = binary_search_last_lower(prev_pos_list, curr_pos)
                if lo == -1 or hi == -1 or lo > hi:
                    continue
                best_cost = math.inf
                best_prev = None
                for p in prev_pos_list[lo : hi + 1]:
                    cost = prev_index_cost[p][0] + (curr_pos - p - 1)
                    if cost < best_cost:
                        best_cost = cost
                        best_prev = p
                if best_prev is not None:
                    temporal_row[curr_pos] = (best_cost, best_prev)

        word = QueryWord(value=curr_word, position=i, index_cost=temporal_row)
        if not temporal_row:
            unmatched_words.append(word)
        else:
            matched_words.append(word)

    return matched_words, unmatched_words  # type: ignore


def find_best_ending(matched_words: list[QueryWord]) -> int | None:
    """
    Identify the OCR position of the last matched query word that produces the
    globally lowest total path cost.

    Returns None if matched_words is empty or no valid ending exists.
    """
    min_total = math.inf
    end_pos = None
    for pos, (cost, _) in matched_words[-1].index_cost.items():
        if cost < min_total:
            min_total = cost
            end_pos = pos
    return end_pos


def backfill_optimal_indices(
    matched_words: list[QueryWord],
    end_pos: int,
) -> list[QueryWord]:
    """
    Walk backwards through matched_words following prev_index pointers and assign
    optimal_index on each QueryWord.

    After this step, matched_words[i].optimal_index holds the OCR word index that
    word i maps to in the best-cost alignment.

    Mutates matched_words in place and returns it.
    """
    for i in range(len(matched_words) - 1, -1, -1):
        matched_words[i].optimal_index = end_pos  # type: ignore
        end_pos = matched_words[i].index_cost[end_pos][1]
    return matched_words


def mark_invalid_neighbors(
    matched_words: list[QueryWord],
    unmatched_words: list[QueryWord],
) -> list[QueryWord]:
    """
    Flag matched words that are adjacent to an unmatched word in the query sequence.

    An unmatched word between two matched words signals that the surrounding matches
    may be imprecise (OCR gap, misread word, etc.). For each unmatched word, binary
    search locates the nearest matched word on each side:

    - The matched word immediately to the right gets  invalid_left_string=True.
    - The matched word immediately to the left gets   invalid_right_string=True.

    These flags are later used by StringMatcher to set confidence=0.01 on the
    corresponding OCR Word objects returned to the postprocessor.

    Mutates matched_words in place and returns it.
    """

    if not matched_words:
        return matched_words

    matched_positions = [m.position for m in matched_words]

    for unmatched_word in unmatched_words:
        position = unmatched_word.position
        first_higher_position = binary_search_first_higher(matched_positions, position)
        last_lower_position = binary_search_last_lower(matched_positions, position)

        if -1 != first_higher_position:
            matched_words[first_higher_position].invalid_left_string = True
        if -1 != last_lower_position:
            matched_words[last_lower_position].invalid_right_string = True

    return matched_words


def construct_optimal_path(
    original_words: list[str],
    substring_words: list[str],
    highlight_invalid_neighbors: bool = True,
    word2positions: WordToPositions | None = None,
) -> list[QueryWord]:
    """
    Align a sequence of query words against a sequence of OCR words using dynamic
    programming, and return the matched QueryWords with their optimal OCR indices set.

    Args:
        original_words:             Normalised OCR words (document, in order).
        substring_words:            Normalised query words (LLM output, in order).
        highlight_invalid_neighbors: When True, call mark_invalid_neighbors so that
                                     matched words adjacent to unmatched ones are
                                     flagged for confidence penalisation.
        word2positions:             Pre-built inverted index (word -> OCR positions).
                                     If None, built on the fly from original_words.

    Returns:
        A list of matched QueryWords. Each has optimal_index pointing to its best
        OCR position in original_words. Returns an empty list if no alignment is
        possible (e.g. no query word exists in the document at all).

    Algorithm summary:

        1. Build an inverted index: word -> [OCR positions].
        # 1. Build an inverted index: word -> [OCR positions] (or reuse pre-built one).
        2. Find the first query word that appears in the document (base cases).
        3. Extend the DP forward: for each subsequent query word, compute the minimum
           cost to reach each candidate OCR position from the previous matched word.
           Cost = total number of OCR words skipped between consecutive matches.
        4. Backtrack from the lowest-cost ending to assign optimal_index values.
        5. Optionally flag neighbours of unmatched words.
    """

    if word2positions is None:
        word2positions = _build_word_to_positions(original_words)

    matched_words, unmatched_words, first_match_idx = find_first_match(substring_words, word2positions)

    if not matched_words:
        return []

    matched_words, unmatched_words = extend_matched_path(  # type: ignore
        substring_words,
        word2positions,
        matched_words,
        unmatched_words,
        first_match_idx,
    )

    end_pos = find_best_ending(matched_words)

    if end_pos is None:
        return []

    matched_words = backfill_optimal_indices(matched_words, end_pos)

    if highlight_invalid_neighbors:
        matched_words = mark_invalid_neighbors(matched_words, unmatched_words)

    return matched_words
