import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"


class Permission(str, enum.Enum):
    SELECT_ONLY = "SELECT_ONLY"
    READ_WRITE = "READ_WRITE"
    ADMIN_ACCESS = "ADMIN_ACCESS"


class DataBaseType(str, enum.Enum):
    postgres = "postgres"
    mysql = "mysql"
    sqlite = "sqlite"
    oracle = "oracle"
    sql_server = "sql_server"


class ChatRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"


class LlmMode(str, enum.Enum):
    local = "local"
    online = "online"