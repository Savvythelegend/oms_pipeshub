from dataclasses import dataclass
from enum import Enum

class OrderType(Enum):
    NEW = "New"
    MODIFY = "Modify"
    CANCEL = "Cancel"

class ResponseType(Enum):
    ACCEPT = "Accept"
    REJECT = "Reject"

@dataclass
class OrderRequest:
    order_id: str
    order_type: OrderType
    price: float
    quantity: int
    timestamp: float

@dataclass
class OrderResponse:
    order_id: str
    response_type: ResponseType
    timestamp: float

@dataclass
class QueuedOrder:
    order_id: str
    price: float
    quantity: int
    timestamp: float 