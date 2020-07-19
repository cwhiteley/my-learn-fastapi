import typing
from typing import List, Optional

from pydantic import BaseModel, Field, ValidationError


# pydantic is primarily a parsing library, not a validation library.

# Model
class User(BaseModel):
    # Type: integer
    # Required
    id: int

    # Type: string (inferred)
    # Not required (has a default)
    name = 'Jane Doe'


class Device(BaseModel):
    # Reference to another model
    past_users: List[User]


# Create
user = User(id='123')
assert user.id == 123  # converted from string

# Input: helper functions

User.construct#()  # create a model without validation. 30x faster
User.construct#(_fields_set=[...])  # ... can specify which fields were set by the user

User.__init__#()  # create, using keyword arguments
User.parse_obj#({'id': 123})  # create, using one argument

User.parse_raw#('')  # load json
User.parse_raw#('', content_type='application/pickle', allow_pickle=True)  # load pickle

User.parse_file#('')  # loading files

User.from_orm#()  # load from arbitrary class


# Inspect
User.__fields__  # model's fields
User.__config__  # Configuration class for the model
assert user.__fields_set__ == {'id'}  # provided by the user

# JSON schema
User.schema()  # get JSON schema
User.schema_json()  # get JSON schema as a string

# Deep copy
user.copy()

# Output: dict
assert user.dict() == dict(user) == {'id': 123, 'name': 'Jane Doe'}

# Output: json
user.json()







# Validation
from pydantic import constr, conint, validator
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper

class Location(BaseModel):
    lat = 0.1
    lng = 10.1


class Model(BaseModel):
    is_required: float
    # int constraint: >= 42
    gt_int: conint(gt=42)
    list_of_ints: List[int] = None
    a_float: float = None
    recursive_model: Location = None

    foo: str

    # Custom validator
    @validator('foo')
    def name_must_contain_space(cls, v):
        # Use ValueError, TypeError, AssertionError
        # Subclass PydanticValueError to have a custom type
        if v != 'bar':
            raise ValueError('value must be "bar"')

        return v


# pydantic will raise ValidationError
try:
    Model(
        list_of_ints=['1', 2, 'bad'],
        a_float='not a float',
        recursive_model={'lat': 4.2, 'lng': 'New York'},
        gt_int=21,
    )
except ValidationError as e:
    e.errors()  # list of errors
    e.json()  # list of errors in JSON
    str(e)  # human-redable errors

    error: ErrorWrapper = e.errors()[0]
    error['loc']  # path
    error['type']  # a computer-readable identifier of the error type.
    error['msg']  # a human readable explanation of the error.
    #error['ctx']  # (optional) values required to render the error message.








# Rename a field
class MyModel(BaseModel):
    # Rename a field
    metadata: typing.Dict[str, str] = Field(alias='metadata_')
















# Required/Optional
class Model(BaseModel):
    # A Required field: no default value, or default value = `...`
    a: int
    b: int = ...
    c: int = Field(...)

    # Optional fields
    d: Optional[int] = None
    e: int = 0

    # Required Optional
    # A field is required (has to be provided), but can be None
    f: Optional[int] = ...















# Generics
# Let's make a generic response type

from typing import TypeVar, Optional, Generic, Type, Tuple, Any
from pydantic.generics import GenericModel

DataT = TypeVar('DataT')


class Error(BaseModel):
    code: int
    message: str


class Response(GenericModel, Generic[DataT]):
    data: Optional[DataT]
    error: Optional[Error]

    # If the name of the concrete subclasses is important, you can also override the default behavior:
    @classmethod
    def __concrete_name__(cls: Type[Any], params: Tuple[Type[Any], ...]) -> str:
        return f'{params[0].__name__.title()}Response'


# Every specific model is cached, so there's no overhead

print(Response[int](data=1))
#> data=1 error=None
print(Response[str](data='value'))
#> data='value' error=None
print(Response[str](data='value').dict())
#> {'data': 'value', 'error': None}









# Parse into other types
from pydantic import parse_obj_as


class Item(BaseModel):
    id: int
    name: str


items = parse_obj_as(
    # Any type Pydantic can handle
    List[Item],
    # Input data
    [{'id': 1, 'name': 'My Item'}]
)








# SqlAlchemy interaction
from pydantic import constr

class CompanyModel(BaseModel):
    id: int
    public_key: constr(max_length=20)
    name: constr(max_length=63)
    domains: List[constr(max_length=255)]

    class Config:
        # Enable attribute access from objects
        orm_mode = True

company = {}  # load

# Convert to Pydantic
try:
    CompanyModel.from_orm(company)
except ValidationError:
    pass











# Dynamic models
# When the shape is not known until runtime

from pydantic import BaseModel, create_model

DynamicFoobarModel = create_model(
    # Name
    'DynamicFoobarModel',
    # Tuple(type, default value)
    # ... -> no default value, but can be None
    foo=(str, ...),
    # Default value
    bar=123,
)







# Immutable models
class FooBarModel(BaseModel):
    class Config:
        # Cannot modify once created
        # WARNING: Immutability in python is never strict.
        # If developers are determined/stupid they can always modify a so-called "immutable" object.
        allow_mutation = False






# __root__
# To validate an object without giving it a name

class Container(BaseModel):
    # The argument of parse_obj() is validated against the root type
    __root__: List[str]

print(Container.parse_obj(['a', 'b']).dict())
# -> {'__root__': ['a', 'b']}







# Using with ABCs
import abc

class FooBarModel(BaseModel, abc.ABC):
    a: str
    b: int

    @abc.abstractmethod
    def my_abstract_method(self):
        pass



