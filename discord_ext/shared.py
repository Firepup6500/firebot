# pylint: disable=missing-module-docstring
import logging
from discord.utils import _ColourFormatter, stream_supports_colour

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
