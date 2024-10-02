from typing import Annotated, List
from app.models.order_model import OrderItemBase,OrderItem,OrderModel,OrderId,OrderUpdate
import logging
from fastapi import Depends, HTTPException
from sqlmodel import select
from app.auth.user_auth import userId_from_token
from app.database.db import DATABASE_SESSION
from uuid import UUID, uuid4


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#-------------------Create Order----------------#
# ----------------------------------------------#
async def create_order(
    order: OrderModel,
    session: DATABASE_SESSION,
    user_id: UUID = Depends(userId_from_token)
) -> OrderModel:
    logger.info("Creating a new order for user: %s", user_id)
    
    # Ensure the order has a unique id
    if not order.id:
        order.id = uuid4()  # Generate a new UUID if not provided
        
    order.user_id = user_id
    
    # Check if the user already has an order
    existing_order = session.query(OrderModel).filter(OrderModel.user_id == user_id).first()
    if existing_order:
        raise HTTPException(status_code=400, detail="User already has an existing order.")
    
    # Add order and its items to the database
    session.add(order)
    session.commit()
    session.refresh(order)
    
    return order

#=====================Read Order========================#

def read_orders(session: DATABASE_SESSION):
    orders = session.exec(select(OrderModel)).all()
    return orders
#-----------------------------------------------------------



async def delete_order(
    order_id: OrderId,
    session: DATABASE_SESSION,
    user_id:UUID=Depends(userId_from_token)
):
    order = session.get(OrderModel, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    session.delete(order)
    session.commit()

    return {"status": "Order deleted", "order_id": order_id}



async def update_order(
    order_id: UUID,
    updated_order: OrderUpdate,
    session: DATABASE_SESSION,
    user_id:UUID=Depends(userId_from_token)
):
    existing_order = session.get(OrderModel, order_id)
    if not existing_order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update order fields
    updated_data = updated_order.dict(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(existing_order, key, value)

    session.commit()
    session.refresh(existing_order)

    return existing_order




# Add multiple OrderItems to an existing Order

async def add_order_items(
    order_id: OrderId,
    # items: List[OrderItem],  # Accept a list of OrderItems to add multiple products
     items: List[OrderItemBase],  # Accept a list of OrderItems to add multiple products
    
    session: DATABASE_SESSION,
    user_id:UUID=Depends(userId_from_token)
) -> OrderModel:
    
    # Get the order by order_id
    order = session.get(OrderModel, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Calculate the total amount for the new items
    total_amount = sum(item.price * item.quantity for item in items)
    
    # Assign the order_id to each item and add them to the session
    for item in items:
        item.order_id = order_id
        session.add(item)
    
    # Update the order total and save
    order.total_amount += total_amount
    session.add(order)
    
    # Commit the transaction and refresh the order
    session.commit()
    session.refresh(order)
    
    return order



async def get_order_items(
    order_id: OrderId,
    session: DATABASE_SESSION,
    user_id:UUID=Depends(userId_from_token)

):
    # Fetch the order to ensure it exists
    order = session.get(OrderModel, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Fetch order items associated with the order
    order_items = session.exec(select(OrderItem).where(OrderItem.order_id == order_id)).all()
    
    return order_items