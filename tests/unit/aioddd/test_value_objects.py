import pytest

from aioddd import Id, IdInvalidError


def test_id_fails_with_invalid_uuid() -> None:
    pytest.raises(IdInvalidError, lambda: Id('0'))


def test_id_is_not_valid() -> None:
    assert not Id.validate('0')


def test_id_generated_is_valid() -> None:
    id_ = Id.generate()
    assert Id.validate(id_.value())


def test_id_str_returns_value() -> None:
    id_ = Id.generate()
    assert id_.value() == id_.__str__()
