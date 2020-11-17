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
        def __init__(self, value: str):
            self.value = value

    class _MyService(_Test):
        pass

    class _MyAnotherService(_Test):
        pass

    tz = 'UTC'
    my_svc = _MyService('foo_my_svc')
    my_another_svc = _MyAnotherService('foo_my_another_svc')

    container.set(key='config.tz', val=tz)
    container.set(key='foo', val='foo')
    container.resolve(
        [
            ('services.foo', _Test, {'value': container.resolve_parameter(lambda di: di.get('foo'))}),
            (_MyService, my_svc),
            my_another_svc,
        ]
    )

    assert container.__contains__('config.tz')
    assert container.__contains__('services.foo')
    assert container.__contains__(_MyService)
    assert container.__contains__(my_svc)
    assert container.__contains__(_MyService)
    assert container.__contains__(my_another_svc)

    assert container.get(key='config.environment', typ=str) == env
    assert container.get(key='config.tz', typ=str) == tz
    assert container.get(key='services.foo', typ=_Test)
    assert container.get(_MyService) is my_svc
    assert container.get(my_svc) is my_svc
    assert container.get(_MyAnotherService) is my_another_svc
    assert container.get(my_another_svc) is my_another_svc
    assert len(container.get(_Test, instance_of=True)) == 3

    pytest.raises(TypeError, lambda: container.get(key='services.foo', typ=str))
    pytest.raises(KeyError, lambda: container.get(key='services.bar'))

    assert not container.__contains__('')
