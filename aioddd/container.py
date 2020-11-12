from typing import Optional, Type, TypeVar

_T = TypeVar('_T')


class Container(dict):
    def set(self, key: str, val: _T) -> None:
        """
        e.g. 1
        container = Container()
        container.set('config', 'hello world')  # {'config': 'hello world'}
        e.g. 2
        container = Container({'config': {}})
        container.set('config.version', '0.1.0')  # {'config': {'version': '0.1.0'}}
        """
        here = self
        keys = key.split('.')
        for key in keys[:-1]:
            here = here.setdefault(key, {})
        here[keys[-1]] = val

    def get(self, key: str, typ: Optional[Type[_T]] = None) -> _T:  # type: ignore
        """
        e.g. 1
        container = Container({'config': {'version': '0.1.0'})
        container.get('config.version')  # '0.1.0'
        e.g. 2
        container = Container({'config': {'version': '0.1.0'})
        container.get('config.version', typ=str)  # Checks type
        """
        here = self
        keys = key.split('.')
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
        except IndexError:
            return False
