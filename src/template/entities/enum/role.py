from enum import IntEnum, StrEnum


class Role(StrEnum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"
