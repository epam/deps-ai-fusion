from ...shared import Guard, ImmutableCheck, RangeCheck
from ..raw_extraction_params import RawPageSpan
from .context_attachments import ContextAttachments
from .page_span import PageSpan

__all__ = [
    "ExtractionParams",
    "DEFAULT_CUSTOM_INSTRUCTION",
    "DEFAULT_GROUPING_FACTOR",
    "DEFAULT_TEMPERATURE",
    "DEFAULT_TOP_P",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_STOP",
    "DEFAULT_SEED",
]


DEFAULT_CUSTOM_INSTRUCTION: str = """\
For the provided document context and based on the specific user instructions, analyze and extract relevant insights.
Focus on identifying actionable, relevant, and concise information that fulfills the purpose of the instructions.
Ensure that the extracted insights are accurate, adhere to specified constraints and respond strictly in the format requested.\
"""  # noqa: E501
DEFAULT_GROUPING_FACTOR: int = 3
DEFAULT_TEMPERATURE: float = 0.0  # noqa: WPS358
DEFAULT_TOP_P: float = 1.0
DEFAULT_MAX_TOKENS: int | None = None
DEFAULT_STOP: list[str] | None = None
DEFAULT_SEED: int | None = None


class ExtractionParams:  # noqa: WPS230
    custom_instruction = Guard[str](str, ImmutableCheck())
    grouping_factor = Guard[int](int, ImmutableCheck(), RangeCheck(min_value=1))
    temperature = Guard[float](float, ImmutableCheck(), RangeCheck(min_value=0, max_value=2))
    top_p = Guard[float](float, ImmutableCheck(), RangeCheck(min_value=0, max_value=1))
    max_tokens = Guard[int](int, ImmutableCheck(), RangeCheck(min_value=1))
    stop = Guard[list](list, ImmutableCheck())
    seed = Guard[int](int, ImmutableCheck())
    page_span = Guard[PageSpan](PageSpan, ImmutableCheck())
    context_attachments = Guard[ContextAttachments](ContextAttachments, ImmutableCheck())

    def __init__(
        self,
        custom_instruction: str | None = None,
        grouping_factor: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
        stop: list[str] | None = None,
        seed: int | None = None,
        page_span: PageSpan | None = None,
        context_attachments: ContextAttachments | None = None,
    ) -> None:
        self.custom_instruction = DEFAULT_CUSTOM_INSTRUCTION if custom_instruction is None else custom_instruction
        self.grouping_factor = DEFAULT_GROUPING_FACTOR if grouping_factor is None else grouping_factor
        self.temperature = DEFAULT_TEMPERATURE if temperature is None else temperature
        self.top_p = DEFAULT_TOP_P if top_p is None else top_p
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if stop is not None:
            self.stop = stop
        if seed is not None:
            self.seed = seed
        if page_span:
            self.page_span = page_span
        if context_attachments:
            self.context_attachments = context_attachments

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ExtractionParams)
            and other.custom_instruction == self.custom_instruction
            and other.grouping_factor == self.grouping_factor
            and other.temperature == self.temperature
            and other.top_p == self.top_p
            and other.max_tokens == self.max_tokens
            and other.stop == self.stop
            and other.seed == self.seed
            and other.page_span == self.page_span
            and other.context_attachments == self.context_attachments
        )

    def __repr__(self) -> str:
        return "\n".join(
            (
                f"<class '{self.__class__.__name__}':",
                f"{self.custom_instruction = },",
                f"{self.grouping_factor = },",
                f"{self.temperature = },",
                f"{self.top_p = },",
                f"{self.max_tokens = },",
                f"{self.stop = },",
                f"{self.seed = },",
                f"{self.page_span = },",
                f"{self.context_attachments = }>",
            ),
        )

    def create_updated(
        self,
        custom_instruction: str,
        grouping_factor: int,
        temperature: float,
        top_p: float,
        max_tokens: int | None = None,
        stop: list[str] | None = None,
        seed: int | None = None,
        page_span: RawPageSpan | None = None,
        context_attachments: ContextAttachments | None = None,
    ) -> "ExtractionParams":
        return ExtractionParams(
            custom_instruction=custom_instruction,
            grouping_factor=grouping_factor,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop,
            seed=seed,
            page_span=page_span and PageSpan.from_dict(page_span),
            context_attachments=context_attachments,
        )
