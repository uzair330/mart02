from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import uuid4, UUID
from datetime import datetime, timezone
from enum import Enum

# Mixin for timestamps
class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Base class for cart item details
class CartItemBase(SQLModel):
    product_id: UUID
    quantity: int
    price: float
    product_name:str
    product_description:str

class CartItem(CartItemBase, TimestampMixin, table=True):
    id: UUID | None = Field(primary_key=True, default_factory=uuid4)
    cart_id: UUID | None = Field(foreign_key="cart.id")
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    cart: Optional["Cart"] = Relationship(back_populates="items")

class Cart(TimestampMixin, SQLModel, table=True):
    id: UUID | None = Field(primary_key=True, default_factory=uuid4)
    user_id: UUID
    total_amount: float = 0
    items: List[CartItem] = Relationship(back_populates="cart")

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SEND_FOR_PAIMENT = "SEND_FOR_PAIMENT"

class OrderItem(TimestampMixin, SQLModel, table=True):
    id: UUID | None = Field(primary_key=True, default_factory=uuid4)
    order_id: UUID | None = Field(foreign_key="ordermodel.id")
    product_id: UUID
    quantity: int
    price: float
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    order: Optional["OrderModel"] = Relationship(back_populates="items")

class OrderModel(TimestampMixin, SQLModel, table=True):
    __tablename__ = "ordermodel"
    id: UUID | None = Field(primary_key=True, default_factory=uuid4)
    user_id: UUID
    total_amount: float = 0
    order_status: OrderStatus = Field(default=OrderStatus.PENDING)
    items: List[OrderItem] = Relationship(back_populates="order")

class ProductItemUpdate(SQLModel):
    order_id : UUID
    product_id: UUID
    quantity:int
    price:float
    product_name:str
    product_description:str
