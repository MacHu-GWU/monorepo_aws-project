# -*- coding: utf-8 -*-

"""
A simple schema definition system for DynamoDB item.
"""

import typing as T
import dataclasses

import polars as pl

from .sentinel import NOTHING

if T.TYPE_CHECKING:  # pragma: no cover
    from .typehint import T_SIMPLE_SCHEMA


@dataclasses.dataclass
class BaseType:
    def to_polars(self) -> T.Union[
        pl.Int64,
        pl.Float64,
        pl.Utf8,
        pl.Binary,
        pl.Boolean,
        pl.Null,
        pl.List,
        pl.Struct,
    ]:
        raise NotImplementedError

    def to_dynamodb_json_polars(self) -> pl.Struct:
        raise NotImplementedError


DATA_TYPE = T.TypeVar("DATA_TYPE", bound=BaseType)


@dataclasses.dataclass
class Integer(BaseType):
    """
    :param default_for_null: The default value for null for serialization.
    """

    default_for_null: T.Any = dataclasses.field(default=NOTHING)

    def to_polars(self) -> pl.Int64:
        return pl.Int64()

    def to_dynamodb_json_polars(self) -> pl.Struct:
        return pl.Struct({"N": pl.Utf8()})


@dataclasses.dataclass
class Float(BaseType):
    """
    :param default_for_null: The default value for null for serialization
    """

    default_for_null: T.Any = dataclasses.field(default=NOTHING)

    def to_polars(self) -> pl.Float64:
        return pl.Float64()

    def to_dynamodb_json_polars(self) -> pl.Struct:
        return pl.Struct({"N": pl.Utf8()})


DEFAULT_NULL_STRING = ""
DEFAULT_NULL_BINARY = b""


@dataclasses.dataclass
class String(BaseType):
    """
    :param default_for_null: The default value for null for serialization.
    """

    default_for_null: T.Any = dataclasses.field(default=DEFAULT_NULL_STRING)

    def to_polars(self) -> pl.Utf8:
        return pl.Utf8()

    def to_dynamodb_json_polars(self) -> pl.Struct:
        return pl.Struct({"S": pl.Utf8()})


@dataclasses.dataclass
class Binary(BaseType):
    """
    :param default_for_null: The default value for null for serialization.
    """

    default_for_null: T.Any = dataclasses.field(default=DEFAULT_NULL_BINARY)

    def to_polars(self) -> pl.Binary:
        return pl.Binary()

    def to_dynamodb_json_polars(self) -> pl.Struct:
        return pl.Struct({"B": pl.Utf8()})


@dataclasses.dataclass
class Bool(BaseType):
    """
    :param default_for_null: The default value for null for serialization
    """

    default_for_null: T.Any = dataclasses.field(default=NOTHING)

    def to_polars(self) -> pl.Boolean:
        return pl.Boolean()

    def to_dynamodb_json_polars(self) -> pl.Struct:
        return pl.Struct({"BOOL": pl.Boolean()})


@dataclasses.dataclass
class Null(BaseType):
    """
    :param default_for_null: The default value for null for serialization
    """

    default_for_null: T.Any = dataclasses.field(default=None)

    def to_polars(self) -> pl.Null:
        return pl.Null()

    def to_dynamodb_json_polars(self) -> pl.Struct:
        return pl.Struct({"NULL": pl.Boolean()})


@dataclasses.dataclass
class Set(BaseType):
    """
    Example::

        record = {"tags": ["a", "b", "c"]}

        schema = Struct({
            "tags": Set(String())
        })

    :param itype: The type of the elements in the set.
    """

    itype: BaseType = dataclasses.field(default=NOTHING)
    default_for_null: T.Any = dataclasses.field(default_factory=list)

    def __post_init__(self):
        if self.itype is NOTHING:
            raise ValueError("itype is required for Set")

    def to_polars(self) -> pl.List:
        return pl.List(self.itype.to_polars())

    def to_dynamodb_json_polars(self) -> pl.Struct:
        if isinstance(self.itype, String):
            field = "SS"
        elif isinstance(self.itype, Integer):
            field = "NS"
        elif isinstance(self.itype, Float):
            field = "NS"
        elif isinstance(self.itype, Binary):
            field = "BS"
        else:
            raise NotImplementedError
        return pl.Struct({field: pl.List(pl.Utf8())})


@dataclasses.dataclass
class List(BaseType):
    """
    Example::

        record = {"tags": ["a", "b", "c"]}

        schema = Struct({
            "tags": List(String())
        })

    :param itype: The type of the elements in the list.
    """

    itype: BaseType = dataclasses.field(default=NOTHING)
    default_for_null: T.Any = dataclasses.field(default_factory=list)

    def __post_init__(self):
        if self.itype is NOTHING:  # pragma: no cover
            raise ValueError("itype is required for List")

    def to_polars(self) -> pl.List:
        return pl.List(self.itype.to_polars())

    def to_dynamodb_json_polars(self) -> pl.Struct:
        return pl.Struct({"L": pl.List(self.itype.to_dynamodb_json_polars())})


@dataclasses.dataclass
class Struct(BaseType):
    """
    Example:

        record = {
            "details": {
                "name": "Alice",
                "age": 30,
            }
        }

        schema = Struct({
            "details": Struct({
                "name": String(),
                "age": Integer(),
            })
        }),

    :param types: The types of the fields in the struct.
    """

    types: T.Dict[str, BaseType] = dataclasses.field(default=NOTHING)

    def __post_init__(self):
        if self.types is NOTHING:  # pragma: no cover
            raise ValueError("types is required for Struct")

    def to_polars(self) -> pl.Struct:
        return pl.Struct({k: v.to_polars() for k, v in self.types.items()})

    def to_dynamodb_json_polars(self) -> pl.Struct:
        return pl.Struct(
            {
                "M": pl.Struct(
                    {k: v.to_dynamodb_json_polars() for k, v in self.types.items()}
                )
            }
        )


# ------------------------------------------------------------------------------
# Convert other data type system to simple schema
# ------------------------------------------------------------------------------
def polars_type_to_simple_type(
    p_type: T.Type[pl.DataType],
) -> DATA_TYPE:  # pragma: no cover
    if isinstance(p_type, pl.Int64):
        return Integer()
    elif isinstance(p_type, pl.Float64):
        return Float()
    elif isinstance(p_type, pl.String):
        return String()
    elif isinstance(p_type, pl.Binary):
        return Binary()
    elif isinstance(p_type, pl.Boolean):
        return Bool()
    elif isinstance(p_type, pl.Null):
        return Null()
    elif isinstance(p_type, pl.List):
        return List(itype=polars_type_to_simple_type(p_type.inner))
    elif isinstance(p_type, pl.Struct):
        schema = {
            field.name: polars_type_to_simple_type(field.dtype)
            for field in p_type.fields
        }
        return Struct(schema)
    else:
        raise NotImplementedError


def dynamodb_json_type_to_data_type(
    v: T.Dict[str, T.Any],
) -> T.Optional[DATA_TYPE]:
    """
    Convert a DynamoDB JSON type definition to a simple type.
    If we don't have enough information to determine the type, return None.
    """
    if "N" in v:
        if "." in v["N"]:
            return Float()
        else:
            return Integer()
    elif "S" in v:
        return String()
    elif "B" in v:
        return Binary()
    elif "BOOL" in v:
        return Bool()
    elif "NULL" in v:
        return Null()
    elif "NS" in v:
        lst = v["NS"]
        if lst:
            if "." in lst[0]:
                return Set(itype=Float())
            else:
                return Set(itype=Integer())
        else:
            return Set(itype=Float())
    elif "SS" in v:
        return Set(itype=String())
    elif "BS" in v:
        return Set(itype=Binary())
    elif "L" in v:
        lst = v["L"]
        if lst:
            return List(itype=dynamodb_json_type_to_data_type(lst[0]))
        else:
            return None
    elif "M" in v:
        schema = dict()
        for k, v in v["M"].items():
            schema[k] = dynamodb_json_type_to_data_type(v)
        return Struct(types=schema)
    else:  # pragma: no cover
        raise NotImplementedError


def dynamodb_json_to_simple_schema(
    item: T.Dict[str, T.Any],
) -> "T_SIMPLE_SCHEMA":
    schema = dict()
    for k, v in item.items():
        data_type = dynamodb_json_type_to_data_type(v)
        if data_type is not None:
            schema[k] = data_type
    return schema


class TypeNameEnum:
    int = "int"
    float = "float"
    str = "str"
    bin = "bin"
    bool = "bool"
    null = "null"
    set = "set"
    list = "list"
    map = "map"


def json_type_to_simple_type(
    json_type: T.Dict[str, T.Any],
) -> "DATA_TYPE":
    """
    Convert a JSON type definition to a simple type.

    >>> json_type_to_simple_type({"type": "int"})
    Integer()
    >>> json_type_to_simple_type({"type": "float"})
    Float()
    >>> json_type_to_simple_type({"type": "str"})
    String()
    >>> json_type_to_simple_type({"type": "bin"})
    Binary()
    >>> json_type_to_simple_type({"type": "bool"})
    Bool()
    >>> json_type_to_simple_type({"type": "null"})
    Null()

    >>> json_type_to_simple_type({"type": "set", "item": {"type": "int"}})
    Set(Integer())
    >>> json_type_to_simple_type({"type": "set", "item": {"type": "float"}})
    Set(Float())
    >>> json_type_to_simple_type({"type": "set", "item": {"type": "str"}})
    Set(String())
    >>> json_type_to_simple_type({"type": "set", "item": {"type": "bin"}})
    Set(Binary())

    >>> json_type_to_simple_type({"type": "list", "item": {"type": "int"}})
    List(Integer())
    >>> json_type_to_simple_type({"type": "list", "item": {"type": "float"}})
    List(Float())
    >>> json_type_to_simple_type({"type": "list", "item": {"type": "str"}})
    List(String())
    >>> json_type_to_simple_type({"type": "list", "item": {"type": "bin"}})
    List(Binary())

    >>> json_type_to_simple_type({
    ...     "type": "list",
    ...     "item": {"type": "map", "values": {"a_int": {"type": "int"}}}
    ... })
    List(Struct({"a_int": Integer()}))

    >>> json_type_to_simple_type({
    ...     "type": "map",
    ...     "values": {
    ...         "a_int": {"type": "int"},
    ...         "a_str": {"type": "str"},
    ...         "a_list_of_int": {"type": "list", "item": {"type": "int"}},
    ...         "a_set_of_str": {"type": "set", "item": {"type": "str"}},
    ...     },
    ... })
    Struct({
        "a_int": Integer(),
        "a_str": String(),
        "a_list_of_int": List(Integer()),
        "a_set_of_str": Set(String()),
    })
    """
    kwargs = dict()
    if "default_for_null" in json_type:
        kwargs["default_for_null"] = json_type["default_for_null"]

    if json_type["type"] == TypeNameEnum.int:
        return Integer(**kwargs)
    elif json_type["type"] == TypeNameEnum.float:
        return Float(**kwargs)
    elif json_type["type"] == TypeNameEnum.str:
        return String(**kwargs)
    elif json_type["type"] == TypeNameEnum.bin:
        return Binary(**kwargs)
    elif json_type["type"] == TypeNameEnum.bool:
        return Bool(**kwargs)
    elif json_type["type"] == TypeNameEnum.null:
        return Null(**kwargs)
    elif json_type["type"] == TypeNameEnum.set:
        return Set(itype=json_type_to_simple_type(json_type["item"]), **kwargs)
    elif json_type["type"] == TypeNameEnum.list:
        return List(itype=json_type_to_simple_type(json_type["item"]), **kwargs)
    elif json_type["type"] == TypeNameEnum.map:
        schema = dict()
        for k, v in json_type["values"].items():
            schema[k] = json_type_to_simple_type(v)
        return Struct(types=schema, **kwargs)
    else:  # pragma: no cover
        raise NotImplementedError
