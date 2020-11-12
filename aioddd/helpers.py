import sys
from datetime import datetime

if sys.version_info.major == 3 and sys.version_info.minor <= 6:
    from backports.datetime_fromisoformat import MonkeyPatch

    MonkeyPatch.patch_fromisoformat()


datetime_fromisoformat = getattr(datetime, 'fromisoformat')
