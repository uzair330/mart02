from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from app.models.order_model import OrderItemBase,OrderItem,OrderModel,OrderId
from uuid import UUID, uuid4
from typing import List
from app.database.db import DATABASE_SESSION
from app.models.cart_model import CartWithItems,Cart,CartUpdate
from app.crud.order_crud import (
    create_order,
    read_orders,
    update_order,
    delete_order,
    add_order_items,
    get_order_items
)

from app.crud.cart_crud import (
    get_carts,
    create_cart
    ,update_cart,
    get_cartitems,
    
)


from sqlmodel import select

router = APIRouter()


@router.get("/get_cart", response_model=Cart,tags=["Cart-Operations"])
def get_cart(cart: Annotated[Cart, Depends(get_carts)]):
    return cart


@router.get("/get_cart_items/",tags=["Cart-Operations"])
async def get_cart_items(cart_id: str, session: DATABASE_SESSION):
    cart_id_uuid = UUID(cart_id)  # Convert the string to UUID
    return await get_cartitems(session, cart_id_uuid)


@router.post("/create_cart", response_model=Cart,tags=["Cart-Operations"])
async def create_cart(cart_items: Annotated[Cart, Depends(create_cart)]):
    return cart_items


@router.put("/update_cart", response_model=CartWithItems,tags=["Cart-Operations"])
def update_cart(
    updated_cart: Annotated[CartUpdate, Depends(update_cart)],
):
    return updated_cart

# Create a new order
@router.post("/orders/", response_model=OrderModel, tags=["Create Order"])
async def create_order(order: Annotated[OrderModel, Depends(create_order)]):
    return order


@router.get("/orders/", response_model=List[OrderModel], tags=["Get Orders"])
async def read_orders(order: Annotated[OrderModel, Depends(read_orders)]):
    return order



# Update an existing order
@router.put("/update_order",tags=["Update & Delete Order"])
async def update_order(
    updated_order: Annotated[OrderModel, Depends(update_order)],
):
    return updated_order


# Delete an order
@router.delete("/delete_order",tags=["Update & Delete Order"])
def delete_order(delete_order: Annotated[str, Depends(delete_order)]):
    return delete_order



# Add multiple OrderItems to an existing Order

@router.post("/orders/items/", tags=["Add Order Items"])
async def order_items(order_items:Annotated[OrderItemBase, Depends(add_order_items)]):
    return order_items


@router.get("/orders/items", response_model=List[OrderItem], tags=["Get Order Items"])
async def order_items(order_items:Annotated[OrderItem, Depends(get_order_items)]):
    return order_items