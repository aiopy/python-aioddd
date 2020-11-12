import sys
from typing import Any, Dict, List, Optional, Union
from unittest.mock import MagicMock, Mock, patch

if sys.version_info >= (3, 8):
    from unittest.mock import AsyncMock
else:

    class AsyncMock(MagicMock):
        async def __call__(self, *args, **kwargs):
            return super(AsyncMock, self).__call__(*args, **kwargs)


SanitizeObject = Union[Dict[Any, Any], List[Any]]


def sanitize_objects(source: SanitizeObject, affected: SanitizeObject) -> SanitizeObject:
    for key, value in list(affected.items()) if isinstance(affected, dict) else enumerate(affected):
        if not isinstance(affected, list) and key not in source:
            affected.pop(key)
        elif isinstance(value, (dict, list)):
            affected[key] = sanitize_objects(source[key], value)
    return affected


def mock(target: Union[str, object], attributes: Optional[List[str]] = None) -> Mock:
    target_async_mock = AsyncMock()
    if not attributes:
        patch(
            target=f'{target.__module__}.{target.__name__}' if isinstance(target, object) else target,  # type: ignore
            side_effect=target_async_mock,
        )
        return target_async_mock
    for attribute in attributes:
        attribute_async_mock = AsyncMock()
        patch.object(
            target=target,
            attribute=attribute,
            side_effect=attribute_async_mock,
        )
        target_async_mock[attribute] = attribute_async_mock
    return target_async_mock
