# pylint: disable=missing-module-docstring,missing-function-docstring
import logging
from functools import wraps
from discord.utils import _ColourFormatter, stream_supports_colour


def withTyping():
    def decorator(func):
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            async with ctx.typing():
                return await func(ctx, *args, **kwargs)

        return wrapper

    return decorator


handler = logging.StreamHandler()
if isinstance(handler, logging.StreamHandler) and stream_supports_colour(
    handler.stream
):
    formatter = _ColourFormatter()
else:
    formatter = logging.Formatter(
        "{asctime} {levelname:<8} {name} {message}", "%Y-%m-%d %H:%M:%S", style="{"
    )
handler.setFormatter(formatter)
