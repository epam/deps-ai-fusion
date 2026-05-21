import logging
from functools import wraps
from time import sleep

__all__ = ["backoff"]

logger = logging.getLogger(__name__)


def backoff(
    start_sleep_time: float = 0.1,
    factor: int = 2,
    max_sleep_time: int = 6,
    times: int = 5,
):
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            time = start_sleep_time
            attempts = times
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    if not attempts:
                        raise
                    time = (time * 2**factor) if time < max_sleep_time else max_sleep_time
                    attempts -= 1
                    logger.error(
                        f"Error occured in {func.__name__}: {err}.\nTry to repeat {func.__name__}, "
                        + f"attempt # {times - attempts}. Delay before attempt: {time} sec.",
                    )
                sleep(time)

        return inner

    return func_wrapper
