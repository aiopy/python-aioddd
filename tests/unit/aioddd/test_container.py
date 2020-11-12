import pytest

from aioddd import Container


def test_container() -> None:
    env = 'development'
    container = Container(
        {
            'config': {'environment': env},
            'services': {},
        }
    )

    assert container.__contains__('config')
    assert container.__contains__('config.environment')
    assert container.__contains__('services')

    class _Test:
        value: str = 'foo'

    tz = 'UTC'
    svc = _Test()

    container.set(key='config.tz', val=tz)
    container.set(key='services.foo', val=svc)

    assert container.__contains__('config.tz')
    assert container.__contains__('services.foo')

    assert container.get(key='config.environment', typ=str) == env
    assert container.get(key='config.tz', typ=str) == tz
    assert container.get(key='services.foo', typ=_Test) is svc

    pytest.raises(TypeError, lambda: container.get(key='services.foo', typ=str))
    pytest.raises(KeyError, lambda: container.get(key='services.bar'))

    assert not container.__contains__('')
