from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

ACCOUNT_ALREADY_EXISTS: ServerOperation
ACCOUNT_DOES_NOT_EXIST: ServerOperation
DESCRIPTOR: _descriptor.FileDescriptor
FAILURE: ServerOperation
LIST_OF_ACCOUNTS: ServerOperation
LIST_OF_MESSAGES: ServerOperation
MESSAGES_EXIST: ServerOperation
NO_MESSAGES: ServerOperation
SUCCESS: ServerOperation

class ClientMessage(_message.Message):
    __slots__ = ["info"]
    INFO_FIELD_NUMBER: _ClassVar[int]
    info: str
    def __init__(self, info: _Optional[str] = ...) -> None: ...

class ServerMessage(_message.Message):
    __slots__ = ["info", "operation"]
    INFO_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    info: str
    operation: ServerOperation
    def __init__(self, operation: _Optional[_Union[ServerOperation, str]] = ..., info: _Optional[str] = ...) -> None: ...

class ServerOperation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
