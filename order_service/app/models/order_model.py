# from enum import Enum
# from typing import Any, Optional
# from sqlmodel import SQLModel, Field, Relationship
# from datetime import datetime, timezone
# from uuid import uuid4, UUID


# class TimestampMixin(SQLModel):
#     created_at: datetime = Field(default=datetime.now(timezone.utc))
#     updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# class ItemBase(SQLModel):
#     product_name: str
#     product_description: str
#     quantity: int = Field(gt=0)
#     price: float = Field(gt=0.0)


# class OrderItem(ItemBase, TimestampMixin, table=True):
#     id: UUID | None = Field(default_factory=uuid4, primary_key=True)
#     order_id: UUID = Field(foreign_key="order.id")
#     order: "Order" = Relationship(back_populates="items")


# class OrderStatus(str, Enum):
#     UNPAID = "UNPAID"
#     PENDING = "PENDING"
#     PAID = "PAID"


# class Order(TimestampMixin, table=True):
#     id: UUID | None = Field(default_factory=uuid4, primary_key=True)
#     cart_id: UUID | None = Field(foreign_key="cart.id")
#     user_id: UUID
#     items: list[OrderItem] = Relationship(back_populates="order", cascade_delete=True)
#     total_amount: float = Field(default=0.0)
#     order_status: OrderStatus = Field(default=OrderStatus.UNPAID)


# class OrderBase(SQLModel):
#     user_id: UUID


# class OrderCreate(OrderBase):
#     items: list[ItemBase]


# class OrderUpdate(OrderBase):
#     items: Optional[list[ItemBase]] = None


# class CartRequest(SQLModel):
#     cart_id: UUID


# class OrderRequest(SQLModel):
#     order_id: UUID


# class OrderItemData(SQLModel):
#     id: UUID | None
#     order_id: UUID
#     product_name: str
#     product_description: str
#     quantity: int = Field(gt=0)
#     price: float = Field(gt=0.0)


# class OrderData(SQLModel):
#     id: UUID
#     cart_id: UUID | None
#     user_id: UUID
#     items: list[dict[str, Any]]
#     total_amount: float
#     order_status: OrderStatus

from enum import Enum
from typing import Any, Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from uuid import uuid4, UUID

class TimestampMixin(SQLModel):
    created_at: datetime = Field(default=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ItemBase(SQLModel):
    product_name: str
    product_description: str
    quantity: int = Field(gt=0)
    price: float = Field(gt=0.0)

class OrderStatus(str, Enum):
    UNPAID = "UNPAID"
    PENDING = "PENDING"
    PAID = "PAID"

class OrderItem(ItemBase, TimestampMixin, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    order_id: UUID = Field(foreign_key="order.id")
    order: "Order" = Relationship(back_populates="items")

class Order(TimestampMixin, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    cart_id: UUID | None = Field(foreign_key="cart.id")
    user_id: UUID
    items: List[OrderItem] = Relationship(back_populates="order")
    total_amount: float = Field(default=0.0)
    order_status: OrderStatus = Field(default=OrderStatus.UNPAID)

class OrderBase(SQLModel):
    user_id: UUID

class OrderCreate(OrderBase):
    items: List[ItemBase]

class OrderUpdate(OrderBase):
    items: Optional[List[ItemBase]] = None

class CartRequest(SQLModel):
    cart_id: UUID

class OrderRequest(SQLModel):
    order_id: UUID

class OrderItemData(SQLModel):
    id: UUID | None
    order_id: UUID
    product_name: str
    product_description: str
    quantity: int = Field(gt=0)
    price: float = Field(gt=0.0)

class OrderData(SQLModel):
    id: UUID
    cart_id: UUID | None
    user_id: UUID
    items: List[dict[str, Any]]
    total_amount: float
    order_status: OrderStatus
