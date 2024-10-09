from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from uuid import UUID
from app.kafka.kafka import kafka_producer
from app.models.order_model import (
    Cart,
    CartItemBase,
    OrderModel,
    OrderItem,
    OrderStatus,
    CartItem,
    ProductItemUpdate
)
from app.crud.order_crud import (
    create_cart,
    add_items_to_cart,
    checkout_cart,
    get_all_orders,
    get_order_by_id,
    finalize_order,
    delete_order,
    add_items_to_order,
    delete_order_item_by_product_id,
    update_order_item_by_product_id,
    get_order_items,
)
from app.database.db import get_session  # Use the same session dependency
from app.auth.user_auth import userId_from_token
from typing import Annotated
from fastapi import Depends

from app.database.db import DATABASE_SESSION
from sqlmodel import select

router = APIRouter()

order_topic="order_topic"

# ------------------ CART OPERATIONS -------------------

# 1. Create Cart for a User
@router.post("/carts/", response_model=Cart, tags=["Cart"])
async def create_cart(session: DATABASE_SESSION,user_id: UUID=Depends(userId_from_token)) -> Cart:
    existing_cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    
    if existing_cart:
        return existing_cart
    
    new_cart = Cart(user_id=user_id, total_amount=0)
    session.add(new_cart)
    try:
        session.commit()
        session.refresh(new_cart)
    
        # Prepare Kafka message
        message = {
            "action": "cart_created",
            "id": str(new_cart.id),
            "user_id": str(new_cart.user_id),
            "total_amount": new_cart.total_amount,
        }

        # Send Kafka message
        await kafka_producer(order_topic, message)

    except Exception as error:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error while creating cart: {error}"
        )
    


    return new_cart


# 2. Add Items to Cart

@router.post("/carts/{cart_id}/items/", response_model=Cart, tags=["Cart"])
async def add_items_to_cart(
    cart_id: UUID, items: List[CartItemBase], session: DATABASE_SESSION
) -> Cart:
    cart = session.get(Cart, cart_id)
    
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    for item in items:
        # Create CartItem using only item.dict() without additional product details
        cart_item = CartItem(
            **item.dict(),  # This includes product_id, quantity, name, description, price
            cart_id=cart.id  # Add cart_id separately
        )
        
        # Check if the item already exists in the cart
        existing_item = session.exec(
            select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == cart_item.product_id)
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



# 3. Checkout (Convert Cart to Order)
@router.post("/carts/{cart_id}/checkout/", response_model=OrderModel, tags=["Order"])
async def checkout_cart(cart_id: UUID, session: DATABASE_SESSION) -> OrderModel:
    cart = session.get(Cart, cart_id)
    
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    new_order = OrderModel(user_id=cart.user_id, total_amount=cart.total_amount)
    
    # Transfer items from cart to order
    for cart_item in cart.items:
        order_item = OrderItem(
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.price,
            product_name=cart_item.product_name,  # Transfer product name
            product_description=cart_item.product_description,  # Transfer description
            order=new_order
        )
        new_order.items.append(order_item)
    
    
    try:
        session.add(new_order)
        session.delete(cart)  # Remove cart after checkout
        session.commit()
        session.refresh(new_order)
    
        # Prepare Kafka message
        message = {
            "action": "order_created",
            "order_id": str(new_order.id),
            }
        # Send Kafka message
        await kafka_producer(order_topic, message)

    except Exception as error:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error while order: {error}"
        )



    return new_order

# ------------------ ORDER OPERATIONS -------------------


@router.post("/orders/{order_id}/items/", response_model=OrderModel, tags=["Order"])
async def add_items_to_order(
    order_id: UUID, items: List[CartItemBase], session: DATABASE_SESSION
) -> OrderModel:
    order = session.get(OrderModel, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.order_status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Cannot modify a finalized order.")

    # Create a set to track existing product IDs in the order
    existing_product_ids = {item.product_id for item in order.items}
    
    for item in items:
        # Check if the product ID already exists in the order
        if item.product_id in existing_product_ids:
            raise HTTPException(status_code=400, detail=f"Product ID {item.product_id} is already in the order.")
        
        # Create an OrderItem using the input values directly
        order_item = OrderItem(
            **item.dict(),  # This includes product_id, quantity, name, description, price
            order_id=order.id  # Add order_id separately
        )
        
        order.items.append(order_item)
        order.total_amount += order_item.price * order_item.quantity
    
    session.add(order)
    session.commit()
    session.refresh(order)
    
    return order

@router.get("/orders/user/{user_id}", response_model=List[OrderModel], tags=["Order"])
async def get_orders_by_user(
    user_id: UUID, 
    session: DATABASE_SESSION
) -> List[OrderModel]:
    # Query the database to get orders by the given user_id
    orders = session.exec(
        select(OrderModel).where(OrderModel.user_id == user_id)
    ).all()

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for the given user_id")

    return orders

@router.delete("/orders/{order_id}/items/{product_id}", response_model=OrderModel, tags=["Order"])
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

    # Find the order item based on product_id
    order_item = next((item for item in order.items if item.product_id == product_id), None)

    if not order_item:
        raise HTTPException(status_code=404, detail="Order item for the given product not found.")

    # Update the total_amount before removing the order item
    order.total_amount -= order_item.price * order_item.quantity
    
    # Remove the order item from the order
    order.items.remove(order_item)
    
    session.add(order)

    try:
        session.commit()
        session.refresh(order)
        # Prepare Kafka message
        message = {
            "action": "delete_order_item",
            "order_id": str(order.order_id),
            "product_id" : str(order.product_id)
            
        }
        # Send Kafka message
        await kafka_producer(order_topic, message)

    except Exception as error:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error while deleting : {error}"
        )

    return order






# 7. Get Order by ID
@router.get("/orders/{order_id}", response_model=OrderModel, tags=["Order"])
async def get_order(order_id: UUID, session: DATABASE_SESSION) -> OrderModel:
    order = session.get(OrderModel, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order

@router.delete("/orders/{order_id}", tags=["Order"])
async def delete_order(order_id: UUID, session: DATABASE_SESSION):
    order = session.get(OrderModel, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    
    try:
        session.commit()
        session.refresh(order)
        # Prepare Kafka message
        message = {
            "action": "delete_order",
            "order_id": str(order_id),
                        
        }
        # Send Kafka message
        await kafka_producer(order_topic, message)

    except Exception as error:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error while deleting order. {order_id}: {error}"
        )
    return {"status": "Order deleted", "order_id": order_id}

# 10. Get Items of a Specific Order
@router.get("/orders/{order_id}/items", response_model=List[OrderItem], tags=["Order"])
async def get_order_items(order_id: UUID, session: DATABASE_SESSION) -> List[OrderItem]:
    order = session.get(OrderModel, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order.items


@router.put("/orders/{order_id}/items/", response_model=OrderModel, tags=["Order"])
async def update_order_item(
    order_id: UUID,
    updated_item: CartItemBase,  # This contains product_id, name, description, quantity, price
    session: DATABASE_SESSION
) -> OrderModel:
    # Retrieve the order
    order = session.get(OrderModel, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.order_status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Cannot modify a finalized order.")

    # Use product_id from updated_item to find the specific item in the order
    order_item = session.exec(
        select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.product_id == updated_item.product_id)
    ).first()

    if not order_item:
        raise HTTPException(status_code=404, detail=f"Product ID {updated_item.product_id} not found in the order.")
    
    # Update the order item fields
    order_item.product_name = updated_item.product_name
    order_item.product_description = updated_item.product_description
    order_item.quantity = updated_item.quantity
    order_item.price = updated_item.price
    
    # Recalculate the total amount for the order
    order.total_amount = sum(
        item.price * item.quantity for item in order.items
    )
    
    # Commit the changes and refresh the order
    session.add(order)
    
    try:
        session.commit()
        session.refresh(order)
        # Prepare Kafka message
        message = {
            "action": "update_order",
            "product_id": order.product_id,
            "quantity": order.quantity,
            "price": order.price,
            "product_name": order.product_name,
            "product_description": order.product_description
                        
        }
        
        # Send Kafka message
        await kafka_producer(order_topic, message)

    except Exception as error:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error while creating product: {error}"
        )

    return order




# 5. Finalize Order (Prepare for payment)
@router.post("/orders/{order_id}/finalize", response_model=OrderModel, tags=["Finalize Order"])
async def finalize_order(order_id: UUID, session: DATABASE_SESSION) -> OrderModel:
    order = session.get(OrderModel, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.order_status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only PENDING ORDERS can be finalized.")
    
    # Perform any necessary finalization steps (e.g., lock items, confirm stock)
    order.order_status = OrderStatus.SEND_FOR_PAIMENT  # Change order status to 'SEND_FOR_PAIMENT'
    
    
    try:
        session.commit()
        session.refresh(order)
        # Prepare Kafka message
        message = {
            "action": "finalizing_order",
            "id":user_id,
            "user_id": order.id,
            "Total Amount":order.total_amount,
            "order_status":"PENDING"
                       
        }

        {
  
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "total_amount": 0,
  "order_status": "PENDING"
}
        
        # Send Kafka message
        await kafka_producer(order_topic, message)

    except Exception as error:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error while creating product: {error}"
        )

    return order
