from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4, UUID
from datetime import datetime, timezone
from typing import Optional, List


# Mixin for timestamps
class TimestampMixin(SQLModel):
    created_at: datetime = Field(default=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Inventory model to track stock levels for products
class InventoryModel(TimestampMixin, SQLModel, table=True):
    id: UUID | None = Field(primary_key=True, default_factory=uuid4)  # Unique ID for the inventory record
    product_id: UUID = Field(index=True)  # Product ID
    user_id: UUID  # ID of the user who owns the product
    product_name: str  # Product name for reference
    product_description: str  # Product description for reference
    stock: int = Field(gt=0)  # Available stock for the product