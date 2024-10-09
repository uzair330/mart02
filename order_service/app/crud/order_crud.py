from fastapi import HTTPException
from sqlmodel import select
from typing import List, Optional
from uuid import UUID
from app.models.order_model import (
    Cart,
    CartItem,
    CartItemBase,
    OrderModel,
    OrderItem,
    OrderStatus,
)
from app.database.db import DATABASE_SESSION  # Use the same session dependency
from app.kafka.kafka import kafka_producer  # If needed
from app.auth.user_auth import userId_from_token
import logging
from typing import Annotated
from fastapi import Depends

logger = logging.getLogger(__name__)

# Simulated function to fetch product details
def get_product_details(product_id: UUID):
    # In a real app, you'd fetch this from a products service or database
    return {
        "product_name": "Sample Product",
        "product_description": "This is a description of the product"
    }

# ------------------ CART OPERATIONS -------------------

# 01 ==============Create Cart==========================#
async def create_cart(session: Depends(DATABASE_SESSION), user_id: UUID = Depends(userId_from_token)) -> Cart:
    existing_cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    
    if existing_cart:
        return existing_cart
    
    new_cart = Cart(user_id=user_id, total_amount=0)
    session.add(new_cart)
    session.commit()
    session.refresh(new_cart)
    
    return new_cart




async def add_items_to_cart(
    cart_id: UUID, items: List[CartItemBase], session: DATABASE_SESSION
) -> Cart:
    cart = session.get(Cart, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    for item in items:
        product_details = get_product_details(item.product_id)
        cart_item = CartItem(**item.dict(), cart_id=cart.id, **product_details)
        existing_item = session.exec(
            select(CartItem).where(
                CartItem.cart_id == cart.id, CartItem.product_id == cart_item.product_id
            )
        ).first()
        if existing_item:
            existing_item.quantity += cart_item.quantity
            session.add(existing_item)
        else:
            cart.items.append(cart_item)
            session.add(cart_item)
        cart.total_amount += cart_item.price * cart_item.quantity
    session.commit()
    session.refresh(cart)
    return cart

async def checkout_cart(cart_id: UUID, session: DATABASE_SESSION) -> OrderModel:
    cart = session.get(Cart, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    new_order = OrderModel(user_id=cart.user_id, total_amount=cart.total_amount)
    for cart_item in cart.items:
        order_item = OrderItem(
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.price,
            product_name=cart_item.product_name,
            product_description=cart_item.product_description,
            order=new_order
        )
        new_order.items.append(order_item)
    session.add(new_order)
    session.delete(cart)
    session.commit()
    session.refresh(new_order)
    return new_order

# ------------------ ORDER OPERATIONS -------------------

async def get_all_orders(session: DATABASE_SESSION) -> List[OrderModel]:
    orders = session.exec(select(OrderModel)).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    return orders

async def get_order_by_id(order_id: UUID, session: DATABASE_SESSION) -> OrderModel:
    order = session.get(OrderModel, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

async def finalize_order(order_id: UUID, session: DATABASE_SESSION) -> OrderModel:
    order = session.get(OrderModel, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.order_status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only PENDING orders can be finalized.")
    order.order_status = OrderStatus.PAID
    session.commit()
    session.refresh(order)
    return order

async def delete_order(order_id: UUID, session: DATABASE_SESSION):
    order = session.get(OrderModel, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    session.delete(order)
    session.commit()
    return {"status": "Order deleted", "order_id": order_id}

async def add_items_to_order(
    order_id: UUID, items: List[CartItemBase], session: DATABASE_SESSION
) -> OrderModel:
    order = session.get(OrderModel, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.order_status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Cannot modify a finalized order.")
    existing_product_ids = {item.product_id for item in order.items}
    for item in items:
        if item.product_id in existing_product_ids:
            raise HTTPException(status_code=400, detail=f"Product ID {item.product_id} is already in the order.")
        product_details = get_product_details(item.product_id)
        order_item = OrderItem(
            **item.dict(),
            order_id=order.id,
            **product_details
        )
        order.items.append(order_item)
        order.total_amount += order_item.price * order_item.quantity
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

async def delete_order_item_by_product_id(
    order_id: UUID,
    product_id: UUID,
    session: DATABASE_SESSION
) -> OrderModel:
    order = session.get(OrderModel, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.order_status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Cannot modify a finalized order.")
    order_item = next((item for item in order.items if item.product_id == product_id), None)
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item for the given product not found.")
    order.total_amount -= order_item.price * order_item.quantity
    order.items.remove(order_item)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

async def update_order_item_by_product_id(
    order_id: UUID,
    product_id: UUID,
    quantity: Optional[int],
    price: Optional[float],
    product_name: Optional[str],
    product_description: Optional[str],
    session: DATABASE_SESSION
) -> OrderItem:
    order = session.get(OrderModel, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.order_status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Cannot modify a finalized order.")
    order_item = next((item for item in order.items if item.product_id == product_id), None)
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item for the given product not found.")
    if quantity is not None:
        order_item.quantity = quantity
    if price is not None:
        order_item.price = price
    if product_name is not None:
        order_item.product_name = product_name
    if product_description is not None:
        order_item.product_description = product_description
    session.add(order_item)
    session.commit()
    session.refresh(order_item)
    return order_item

async def get_order_items(order_id: UUID, session: DATABASE_SESSION) -> List[OrderItem]:
    order = session.get(OrderModel, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order.items
