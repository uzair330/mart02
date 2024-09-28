from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from uuid import uuid4, UUID


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ItemBase(SQLModel):
    product_id: UUID  # Replacing product_variant_id with product_id
    product_name: str
    product_description: str
    quantity: int = Field(gt=0)
    price: float = Field(gt=0.0)


class CartItem(ItemBase, TimestampMixin, SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    # user_id: UUID | None= Field(default_factory=uuid4)
    cart_id: UUID = Field(foreign_key="cart.id")
    cart: "Cart" = Relationship(back_populates="items")



class Cart(TimestampMixin, SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID
    items: Optional[list[CartItem]] = Relationship(back_populates="cart")
    total_amount: float = Field(default=0.0)


class CartBase(SQLModel):
    id: UUID | None = None


class CartCreate(CartBase):
    items: list[ItemBase]


class CartWithItems(CartCreate):
    total_amount: float = Field(default=0.0)


class CartUpdate(CartBase):
    items: Optional[list["CartItemUpdate"]] = None


class CartItemUpdate(SQLModel):
    product_id: Optional[UUID] = None  # Replacing product_variant_id with product_id
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None


class CartRequest(SQLModel):
    cart_id: UUID
