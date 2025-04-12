from enum import IntEnum

class Status(IntEnum):
    CREATED = 0
    UPDATED = 1
    DELETED = 2

class ProductStatus(IntEnum):
    INACTIVE = 0
    ACTIVE = 1
