from sqlmodel import SQLModel, Field,Relationship
from uuid import uuid4, UUID
from datetime import datetime, timezone
from typing import List, Optional

class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OrderItemBase(SQLModel):
    product_name: str
    product_description: str
    quantity: int = Field(gt=0)
    price: float = Field(gt=0.0)

class OrderItem(OrderItemBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    order_id: UUID = Field(foreign_key="ordermodel.id")
    order: "OrderModel" = Relationship(back_populates="order_items")

class OrderModel(TimestampMixin, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID
    total_amount: float = Field(default=0.0)
    status: str
    order_items: List[OrderItem] = Relationship(back_populates="order")

class OrderId(SQLModel):
    id:UUID

class OrderUpdate(SQLModel):
    total_amount: float = Field(default=0.0)
    status: str    