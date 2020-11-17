from inspect import signature
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

_T = TypeVar('_T')

_primitives = (bytes, bytearray, bool, int, float, str, dict, tuple, list, set, slice, map, zip)


def _is_primitive(val: Any) -> bool:
    return isinstance(val, _primitives)  # type: ignore


def _is_object(val: Any) -> bool:
    return isinstance(val, object) and not isinstance(val, type) and not _is_primitive(val)


def _is_simple(val: Any) -> bool:
    return not _is_object(val)


ContainerKey = Union[str, Type[Any], object]


class Container(dict):
    debug: bool = False
    _parameter_resolvers: List[Callable[['Container'], Any]] = []

    def __init__(
        self,
        items: Optional[
            Union[
                Dict[str, Any], List[Union[ContainerKey, Tuple[ContainerKey, _T, Dict[str, Any]]]]  # hardcoded
            ]  # magic
        ] = None,
        debug: bool = False,
    ) -> None:
        items = items or {}
        self.debug = debug
        if isinstance(items, dict):
            super(Container, self).__init__(items)
        else:
            super(Container, self).__init__({})
            self.resolve(items)

    def resolve_parameter(self, fn: Callable[['Container'], Any]) -> Tuple[int, Callable[['Container'], Any]]:
        self._parameter_resolvers.append(fn)
        return len(self._parameter_resolvers) - 1, fn

    def resolve(self, items: List[Union[ContainerKey, Tuple[ContainerKey, _T, Dict[str, Any]]]]) -> None:
        items_ = list(map(self._sanitize_item_before_resolve, items))
        while items_:
            for index, item in enumerate(items_):
                # Check if already exist
                if item[0] in self or item[1] in self:
                    if self.debug:
                        print('Ignoring {} - {}'.format(item[0], item[1]))
                    del items_[index]
                    continue
                # Resolve 2nd arg if is a primitive or instance
                if not isinstance(item[1], type):
                    if self.debug:
                        print('Adding {} - {}'.format(item[0], item[1]))
                    self.set(item[0], item[1])
                    del items_[index]
                    continue
                # Resolve or Postpone 2nd arg if is a type
                kwargs = self._resolve_or_postpone_item(item, items_)
                if kwargs is not None:
                    if self.debug:
                        print('Resolving {}'.format(item[1]))
                    inst = item[1](**kwargs)
                    if self.debug:
                        print('Adding {} - {}'.format(item[0], item[1]))
                    self.set(item[0], inst)
                    del items_[index]

    def set(self, key: ContainerKey, val: _T = ...) -> None:  # type: ignore
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
            val = key  # type: ignore
            key = f'{key.__class__.__module__}.{key.__class__.__name__}'
        keys = cast(str, key).split('.')
        for key in keys[:-1]:
            here = here.setdefault(key, {})
        here[keys[-1]] = val

    def get(self, key: ContainerKey, typ: Optional[Type[_T]] = None, instance_of: bool = False) -> _T:  # type: ignore
        """
        e.g. 1
        container = Container({'config': {'version': '0.1.0'}, 'app.libs.MyClass': '...'})
        container.get('config.version')  # '0.1.0'
        container.get(MyClass)  # '...'
        container.get(Service, instance_of=True)  # List[Service]
        e.g. 2
        container = Container({'config': {'version': '0.1.0'})
        container.get('config.version', typ=str)  # Checks type
        """
        here = self
        if instance_of:
            key: Type[Any] = key if isinstance(key, type) else type(key) if _is_object(key) else None  # type: ignore
            if not key:
                raise ValueError('key parameter must be a type or object non-primitive to use instance_of parameter')
            return self._get_instance_of(here, key)  # type: ignore
        if isinstance(key, type):
            typ = None
            key = '{}.{}'.format(key.__module__, key.__name__)
        if _is_object(key):
            typ = None
            key = '{}.{}'.format(key.__class__.__module__, key.__class__.__name__)
        if not isinstance(key, str):
            raise KeyError('<{}> does not exist in container'.format(key))
        keys = key.split('.')
        original_key = key
        for key in keys[:-1]:
            if key in here and isinstance(here[key], dict):
                here = here[key]
        try:
            val = here[keys[-1]]
            if typ and not isinstance(val, (typ,)):
                raise TypeError('<{}: {}> does not exist in container'.format(original_key, typ.__name__))
            return val
        except KeyError:
            raise KeyError('<{}> does not exist in container'.format(original_key))

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

    @staticmethod
    def _sanitize_item_before_resolve(
        item: Union[ContainerKey, Tuple[ContainerKey, _T, Dict[str, Any]]]
    ) -> Tuple[ContainerKey, _T, Dict[str, Any]]:
        if not isinstance(item, tuple):
            return item, item, {}  # type: ignore
        length = len(item)
        if length == 1:
            return item[0], item[0], {}
        if length == 2:
            return item[0], item[1], {}
        if length >= 3:
            return item[:3]  # type: ignore
        raise ValueError('Tuple must be at least of one item')

    def _resolve_or_postpone_item(
        self,
        item: Tuple[ContainerKey, _T, Dict[str, Any]],
        items: List[Tuple[ContainerKey, _T, Dict[str, Any]]],
    ) -> Optional[Dict[str, Any]]:
        parameters = signature(item[1]).parameters.items()  # type: ignore
        kwargs: Dict[str, Any] = {}
        for parameter in parameters:
            name: str = parameter[0]
            typ: Type[Any] = parameter[1].annotation
            if typ in _primitives:
                if name not in item[2]:
                    raise TypeError('Parameter {} can not be primitive to self-resolve'.format(name))
                val = item[2].get(name)
                if isinstance(val, tuple) and len(val) == 2 and callable(val[1]):
                    try:
                        if self.debug:
                            print('Trying resolve parameter {} of {}'.format(name, item[1]))
                        item[2][name] = val[1](self)
                        del self._parameter_resolvers[val[0]]
                        val = item[2][name]
                    except (KeyError, ValueError):
                        if self.debug:
                            print('Postponing parameter resolver {}'.format(typ))
                        kwargs = {}
                        break
                if not isinstance(val, typ):
                    raise TypeError('<{}: {}> wrong type <{}> given'.format(name, typ.__name__, type(val).__name__))
                kwargs.update({name: val})
                continue
            if typ in self:
                kwargs.update({name: self.get(typ)})
                continue
            if typ not in [i[0] for i in items]:
                if self.debug:
                    print('Postponing {}'.format(typ))
                items.append((typ, typ, {}))  # type: ignore
                kwargs = {}
                break
        if len(parameters) == len(kwargs.keys()):
            return kwargs
        return None

    @classmethod
    def _get_instance_of(cls, items: Dict[str, Any], typ: Type[Any]) -> List[Any]:
        instances = []
        for _, val in items.items():
            if isinstance(val, typ):
                instances.append(val)
            elif isinstance(val, dict):
                instances = [*instances, *cls._get_instance_of(val, typ)]
            elif isinstance(val, list):
                for val_ in val:
                    instances = [*instances, *cls._get_instance_of({'': val_}, typ)]
        return list(set(instances))
