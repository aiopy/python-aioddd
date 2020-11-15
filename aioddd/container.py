from typing import Any, Optional, Type, TypeVar, Union, cast

_T = TypeVar('_T')


def _is_object(val: Any) -> bool:
    return isinstance(val, object) and not isinstance(
        val, (bytes, bytearray, bool, int, float, str, dict, tuple, list, set, slice, map, zip)  # type: ignore
    )


class Container(dict):
    def set(self, key: Union[str, Type[Any], object], val: _T = ...) -> None:  # type: ignore
        """
        e.g. 1
        container = Container()
        container.set('config', 'hello world')  # {'config': 'hello world'}
        container.set(MyClass, my_class)  # {'python.path.to.my_class': '...'}
        container.set(my_another_class)  # {'python.path.to.my_another_class': '...'}
        e.g. 2
        container = Container({'config': {}})
        container.set('config.version', '0.1.0')  # {'config': {'version': '0.1.0'}}
        """
        here = self
        if isinstance(key, type) and val is not ...:
            key = f'{key.__module__}.{key.__name__}'
        if _is_object(key) and val is ...:
            val = key  # type: ignore
            key = f'{key.__class__.__module__}.{key.__class__.__name__}'
        keys = cast(str, key).split('.')
        for key in keys[:-1]:
            here = here.setdefault(key, {})
        here[keys[-1]] = val

    def get(self, key: Union[str, Type[Any], object], typ: Optional[Type[_T]] = None) -> _T:  # type: ignore
        """
        e.g. 1
        container = Container({'config': {'version': '0.1.0'}, 'app.libs.MyClass': '...'})
        container.get('config.version')  # '0.1.0'
        container.get(MyClass)  # '...'
        e.g. 2
        container = Container({'config': {'version': '0.1.0'})
        container.get('config.version', typ=str)  # Checks type
        """
        here = self
        if isinstance(key, type) and not typ:
            key = f'{key.__module__}.{key.__name__}'
        if _is_object(key) and not typ:
            key = f'{key.__class__.__module__}.{key.__class__.__name__}'
        keys = cast(str, key).split('.')
        for key in keys[:-1]:
            if key in here and isinstance(here[key], dict):
                here = here[key]
        try:
            val = here[keys[-1]]
            if typ and not isinstance(val, (typ,)):
                raise TypeError(f'<{key}{f": {typ.__name__}" if typ else ""}> does not exist in container')
            return val
        except KeyError:
            raise KeyError(f'<{key}{f": {typ.__name__}" if typ else ""}> does not exist in container')

    def __contains__(self, *o) -> bool:  # type: ignore
        """
        e.g. 1
        container = Container({'config': '...'})
        'config' in container # True
        e.g. 2
        container = Container({'config': {'version': '0.1.0'})
        'config.version' in container # True
        'config.foo' in container # False
        """
        try:
            self.get(o[0])
            return True
        except (IndexError, KeyError, TypeError):
            return False
