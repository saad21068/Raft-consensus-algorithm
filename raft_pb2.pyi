from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServeClientArgs(_message.Message):
    __slots__ = ("input",)
    INPUT_FIELD_NUMBER: _ClassVar[int]
    input: str
    def __init__(self, input: _Optional[str] = ...) -> None: ...

class ServeClientReply(_message.Message):
    __slots__ = ("data", "leader_id", "success", "message")
    DATA_FIELD_NUMBER: _ClassVar[int]
    LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    data: str
    leader_id: int
    success: bool
    message: str
    def __init__(self, data: _Optional[str] = ..., leader_id: _Optional[int] = ..., success: bool = ..., message: _Optional[str] = ...) -> None: ...

class EmptyMessage(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class LeaderMessage(_message.Message):
    __slots__ = ("leader", "address")
    LEADER_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    leader: int
    address: str
    def __init__(self, leader: _Optional[int] = ..., address: _Optional[str] = ...) -> None: ...

class GetValResponse(_message.Message):
    __slots__ = ("success", "value", "leader_id", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    value: str
    leader_id: int
    message: str
    def __init__(self, success: bool = ..., value: _Optional[str] = ..., leader_id: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class Get_Key(_message.Message):
    __slots__ = ("key", "leader_id_start")
    KEY_FIELD_NUMBER: _ClassVar[int]
    LEADER_ID_START_FIELD_NUMBER: _ClassVar[int]
    key: str
    leader_id_start: int
    def __init__(self, key: _Optional[str] = ..., leader_id_start: _Optional[int] = ...) -> None: ...

class Set_Key_Val(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class Success(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class VoteRequest(_message.Message):
    __slots__ = ("term", "id", "last_log_index", "last_log_term", "old_lease_time")
    TERM_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LAST_LOG_INDEX_FIELD_NUMBER: _ClassVar[int]
    LAST_LOG_TERM_FIELD_NUMBER: _ClassVar[int]
    OLD_LEASE_TIME_FIELD_NUMBER: _ClassVar[int]
    term: int
    id: int
    last_log_index: int
    last_log_term: int
    old_lease_time: float
    def __init__(self, term: _Optional[int] = ..., id: _Optional[int] = ..., last_log_index: _Optional[int] = ..., last_log_term: _Optional[int] = ..., old_lease_time: _Optional[float] = ...) -> None: ...

class VoteRequestResponse(_message.Message):
    __slots__ = ("term", "result", "old_lease_time", "max_old_lease")
    TERM_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    OLD_LEASE_TIME_FIELD_NUMBER: _ClassVar[int]
    MAX_OLD_LEASE_FIELD_NUMBER: _ClassVar[int]
    term: int
    result: bool
    old_lease_time: float
    max_old_lease: float
    def __init__(self, term: _Optional[int] = ..., result: bool = ..., old_lease_time: _Optional[float] = ..., max_old_lease: _Optional[float] = ...) -> None: ...

class AppendEntriesMessage(_message.Message):
    __slots__ = ("term", "id", "prev_log_index", "prev_log_term", "entries", "leader_commit", "lease_interval", "heartbeat_count")
    TERM_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PREV_LOG_INDEX_FIELD_NUMBER: _ClassVar[int]
    PREV_LOG_TERM_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    LEADER_COMMIT_FIELD_NUMBER: _ClassVar[int]
    LEASE_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_COUNT_FIELD_NUMBER: _ClassVar[int]
    term: int
    id: int
    prev_log_index: int
    prev_log_term: int
    entries: _containers.RepeatedCompositeFieldContainer[Entry]
    leader_commit: int
    lease_interval: float
    heartbeat_count: int
    def __init__(self, term: _Optional[int] = ..., id: _Optional[int] = ..., prev_log_index: _Optional[int] = ..., prev_log_term: _Optional[int] = ..., entries: _Optional[_Iterable[_Union[Entry, _Mapping]]] = ..., leader_commit: _Optional[int] = ..., lease_interval: _Optional[float] = ..., heartbeat_count: _Optional[int] = ...) -> None: ...

class Entry(_message.Message):
    __slots__ = ("term", "update")
    TERM_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    term: int
    update: Update
    def __init__(self, term: _Optional[int] = ..., update: _Optional[_Union[Update, _Mapping]] = ...) -> None: ...

class Update(_message.Message):
    __slots__ = ("command", "key", "value")
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    command: str
    key: str
    value: str
    def __init__(self, command: _Optional[str] = ..., key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class AppendEntryReply(_message.Message):
    __slots__ = ("term", "result", "storing_leasder_lease_time", "heartbeat_count")
    TERM_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    STORING_LEASDER_LEASE_TIME_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_COUNT_FIELD_NUMBER: _ClassVar[int]
    term: int
    result: bool
    storing_leasder_lease_time: float
    heartbeat_count: int
    def __init__(self, term: _Optional[int] = ..., result: bool = ..., storing_leasder_lease_time: _Optional[float] = ..., heartbeat_count: _Optional[int] = ...) -> None: ...
