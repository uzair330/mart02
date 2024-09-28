from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4, UUID
from datetime import datetime, timezone
from typing import Optional, List


# Mixin for timestamps
class TimestampMixin(SQLModel):
    created_at: datetime = Field(default=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Base class for product details (common fields)
class ProductBase(SQLModel):
    product_name: str
    product_description: str
    price: float = Field(gt=0.0)  # Price of the product
    stock: int  # Available stock for the product


# Product model with relation to OrderItems
class ProductModel(ProductBase, TimestampMixin, table=True):
    id: UUID | None = Field(primary_key=True, index=True, default_factory=uuid4)
    user_id: UUID | None = Field(index=True)
    
    # Relationship with OrderItem, linked via product_id
    order_items: List["OrderItem"] = Relationship(back_populates="product")


# Model to represent order items in an order
class OrderItem(TimestampMixin, SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)  # Unique ID for the order item
    product_id: UUID = Field(foreign_key="productmodel.id")  # Foreign key to ProductModel
    product_name: str  # Name of the product at the time of ordering
    product_description: str  # Description of the product
    quantity: int = Field(gt=0)  # Quantity of the product ordered
    price: float = Field(gt=0.0)  # Price of the product at the time of ordering

    # Back reference to the product
    product: ProductModel = Relationship(back_populates="order_items")


# creating/updating products (for input)
class ProductFormModel(ProductBase):
    id: Optional[UUID] = None


# Model for deleting a product by its ID
class DeleteProduct(SQLModel):
    product_id: UUID
