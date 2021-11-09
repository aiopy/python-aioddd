"""
This file will be promoted as a package (aiodi) in the next major according to the semver.
"""

from inspect import signature
from logging import getLogger
from typing import (
    AbstractSet,
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

from .helpers import typing_get_args, typing_get_origin

_logger = getLogger('aiodi')

_T = TypeVar('_T')

_primitives = (bytes, bytearray, bool, int, float, str, dict, tuple, list, set, slice, map, zip)


def _is_primitive(val: Any) -> bool:
    return isinstance(val, _primitives) or val in _primitives


def _is_object(val: Any) -> bool:
    return isinstance(val, object) and not isinstance(val, type) and not _is_primitive(val)


def _is_simple(val: Any) -> bool:
    return not _is_object(val)


def _is_optional(field: Any) -> bool:  # pragma: no cover
    return typing_get_origin(field) is Union and type(None) in typing_get_args(field)


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
                        _logger.debug('Ignoring {0} - {1}'.format(item[0], item[1]))
                    del items_[index]
                    continue
                # Resolve 2nd arg if is a primitive or instance
                if not isinstance(item[1], type) and len(item[2].keys()) == 0:
                    if self.debug:
                        _logger.debug('Adding {0} - {1}'.format(item[0], item[1]))
                    self.set(item[0], item[1])
                    del items_[index]
                    continue
                # Resolve or Postpone 2nd arg if is a type
                kwargs = self._resolve_or_postpone_item(item, items_)
                if kwargs is not None:
                    if self.debug:
                        _logger.debug('Resolving {0}'.format(item[1]))
                    inst = item[1](**kwargs)  # type: ignore
                    if self.debug:
                        _logger.debug('Adding {0} - {1}'.format(item[0], item[1]))
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
            key = '{0}.{1}'.format(key.__module__, key.__name__)
        if _is_object(key):
            typ = None
            key = '{0}.{1}'.format(key.__class__.__module__, key.__class__.__name__)
        if not isinstance(key, str):
            raise KeyError('<{0}> does not exist in container'.format(key))
        keys = key.split('.')
        original_key = key
        for key in keys[:-1]:
            if key in here and isinstance(here[key], dict):
                here = here[key]
        try:
            val = here[keys[-1]]
            if typ and not isinstance(val, (typ,)):
                raise TypeError('<{0}: {1}> does not exist in container'.format(original_key, typ.__name__))
            return val
        except KeyError:
            raise KeyError('<{0}> does not exist in container'.format(original_key))

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
        item[2].update(self._sanitize_item_parameters_before_resolve_or_postpone(parameters, item[2]))
        for parameter in parameters:
            name: str = parameter[0]
            typ: Type[Any] = parameter[1].annotation
            if typ in _primitives:
                val = self._resolve_or_postpone_item_parameter(name, typ, item)
                if val is None or parameter[1].default is None:
                    kwargs = {}
                    break
                if not isinstance(val, typ):
                    raise TypeError('<{0}: {1}> wrong type <{2}> given'.format(name, typ.__name__, type(val).__name__))
                kwargs.update({name: val})
                continue
            if typ in self:
                val = self._resolve_or_postpone_item_parameter(name, typ, item)
                if val is not None:
                    kwargs.update({name: val})
                else:
                    kwargs.update({name: self.get(typ)})
                continue
            if typ not in _primitives:
                val = self._resolve_or_postpone_item_parameter(name, typ, item)
                if val is not None or _is_optional(typ):
                    kwargs.update({name: val})
                    continue
            if typ not in [i[0] for i in items]:
                if self.debug:
                    _logger.debug('Postponing {0}'.format(typ))
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

    def _resolve_or_postpone_item_parameter(
        self,
        name: str,
        typ: Type[Any],
        item: Tuple[ContainerKey, _T, Dict[str, Any]],
    ) -> Any:
        if name not in item[2]:
            return None
        val = item[2].get(name)
        if isinstance(val, tuple) and len(val) == 2 and callable(val[1]):
            try:
                if self.debug:
                    _logger.debug('Trying resolve parameter "{0}" from {1}'.format(name, item[1]))
                index = val[0]
                item[2][name] = val[1](self)
                self._parameter_resolvers = self._parameter_resolvers[:index] + self._parameter_resolvers[index + 1 :]
                return item[2][name]
            except (KeyError, ValueError):
                if self.debug:
                    _logger.debug('Postponing parameter resolver {0}'.format(typ))
                return None
        return val

    @staticmethod
    def _sanitize_item_parameters_before_resolve_or_postpone(
        meta_params: AbstractSet, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        for meta_param in meta_params:
            name: str = meta_param[0]
            typ: Type[Any] = meta_param[1].annotation
            if name not in params and (_is_primitive(typ) or _is_optional(typ)):
                val = meta_param[1].default
                params.update({name: val})
        return params
