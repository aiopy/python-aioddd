from typing import Any, Dict, List, Optional, Type, Union
from unittest.mock import AsyncMock, MagicMock, Mock, patch


SanitizeObject = Union[Dict[Any, Any], List[Any]]


def sanitize_objects(source: SanitizeObject, affected: SanitizeObject) -> SanitizeObject:  # pragma: no cover
    for key, value in list(affected.items()) if isinstance(affected, dict) else enumerate(affected):
        if not isinstance(affected, list) and key not in source:
            affected.pop(key)
        elif isinstance(value, (dict, list)):
            affected[key] = sanitize_objects(source[key], value)
    return affected


def mock(
    target: Union[str, object],
    attributes: Optional[List[str]] = None,
    target_mock_type: Type[Mock] = AsyncMock,
    attribute_mock_type: Type[Mock] = AsyncMock,
) -> Mock:
    target_async_mock = target_mock_type()
    if not attributes:
        patch(
            target=f'{target.__module__}.{target.__name__}' if isinstance(target, object) else target,  # type: ignore
            side_effect=target_async_mock,
        )
        return target_async_mock
    for attribute in attributes:
        attribute_async_mock = attribute_mock_type()
        patch.object(
            target=target,
            attribute=attribute,
            side_effect=attribute_async_mock,
        )
        target_async_mock[attribute] = attribute_async_mock
    return target_async_mock


async_mock = mock


def sync_mock(
    target: Union[str, object],
    attributes: Optional[List[str]] = None,
    target_mock_type: Type[Mock] = MagicMock,
    attribute_mock_type: Type[Mock] = MagicMock,
) -> Mock:
    return mock(
        target=target,
        attributes=attributes,
        target_mock_type=target_mock_type,
        attribute_mock_type=attribute_mock_type,
    )
