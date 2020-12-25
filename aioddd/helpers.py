import sys
import typing
from datetime import datetime

if sys.version_info.major == 3 and sys.version_info.minor <= 6:
    from backports.datetime_fromisoformat import MonkeyPatch

    MonkeyPatch.patch_fromisoformat()

datetime_fromisoformat = getattr(datetime, 'fromisoformat')

typing_get_args = getattr(
    typing, 'get_args', lambda t: getattr(t, '__args__', ()) if t is not typing.Generic else typing.Generic
)
typing_get_origin = getattr(typing, 'get_origin', lambda t: getattr(t, '__origin__', None))
