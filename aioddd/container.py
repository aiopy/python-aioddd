from inspect import signature
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union, cast

_T = TypeVar('_T')

_primitives = (bytes, bytearray, bool, int, float, str, dict, tuple, list, set, slice, map, zip)


def _is_primitive(val: Any) -> bool:
    return isinstance(val, _primitives)  # type: ignore


def _is_object(val: Any) -> bool:
    return isinstance(val, object) and not isinstance(val, type) and not _is_primitive(val)


def _is_simple(val: Any) -> bool:
    return not _is_object(val)


ContainerKey = Union[str, Type[Any], object]
ContainerValue = _T  # type: ignore


class Container(dict):
    def resolve(self, items: List[Union[ContainerKey, Tuple[ContainerKey, ContainerValue]]]) -> None:  # type: ignore
        items_ = items.copy()
        while items_:
            for index, item in enumerate(items_):
                # Sanitize item
                item_ = item
                if not isinstance(item_, tuple):
                    item_ = (item_, item_)
                if len(item_) < 2:
                    item_ = (item_[0], item_[0])
                # Check if already exist
                if item_[1] in self:
                    del items_[index]
                    continue
                # Resolve 2nd arg if is a primitive or instance
                if not isinstance(item_[1], type):
                    self.set(item_[0], item_[1])
                    del items_[index]
                    continue
                # Resolve or Postpone 2nd arg if is a type
                parameters = signature(item_[1]).parameters.items()
                kwargs: Dict[str, Any] = {}
                for parameter in parameters:
                    typ: Type[Any] = parameter[1].annotation
                    if typ in _primitives:
                        raise TypeError(f'Parameter {parameter[0]} can not be primitive to self-resolve')
                    if typ in self:
                        kwargs.update({parameter[0]: self.get(typ)})
                        continue
                    items_.append(typ)
                    kwargs = {}
                    break
                # Resolve 2nd arg when all args are ready
                if len(parameters) == len(kwargs.keys()):
                    self.set(item_[0], item_[1](**kwargs))
                    del items_[index]

    def set(self, key: ContainerKey, val: ContainerValue = ...) -> None:  # type: ignore
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
        if isinstance(key, type):
            key = f'{key.__module__}.{key.__name__}'
        if _is_object(key):
            val = key
            key = f'{key.__class__.__module__}.{key.__class__.__name__}'
        keys = cast(str, key).split('.')
        for key in keys[:-1]:
            here = here.setdefault(key, {})
        here[keys[-1]] = val

    def get(self, key: ContainerKey, typ: Optional[Type[ContainerValue]] = None) -> ContainerValue:  # type: ignore
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
