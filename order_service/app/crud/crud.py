from typing import Annotated, List
from app.models.cart_model import Cart, CartCreate,CartWithItems, CartItem, CartUpdate, CartRequest,ItemBase,CartUpdate
from fastapi import Depends, HTTPException
from sqlmodel import select
from app.auth.user_auth import userId_from_token
from app.database.db import DATABASE_SESSION
from uuid import UUID, uuid4
from sqlalchemy import and_ 


#-----------Card Crud Functions---------------


async def get_carts(session: DATABASE_SESSION, user_id: UUID = Depends(userId_from_token)):
    select_cart = select(Cart).where(Cart.user_id == user_id)
    carts = session.exec(select_cart).all()
    if not carts:
        raise HTTPException(
            status_code=404,
            detail="No carts found for this user"
        )
    for cart in carts:
        if cart.items:
            total_amount = 0.0
            for item in cart.items:
                total_amount += item.price * item.quantity
            cart.total_amount = round(total_amount, 2)
    # print(carts[0])
    return cart


# async def get_cartitems(session: DATABASE_SESSION, user_id: UUID = Depends(userId_from_token)):
#     select_cart = select(CartItem).where(Cart.user_id == user_id)
#     carts = session.exec(select_cart).all()
#     if not carts:
#         raise HTTPException(
#             status_code=404,
#             detail="No carts found for this user"
#         )
#     return carts



async def get_cartitems(session: DATABASE_SESSION, cart_id: CartRequest,user_id:UUID=Depends(userId_from_token)):
    select_cart = select(CartItem).where(CartItem.cart_id == cart_id and CartItem.user_id == user_id)
    cart_items = session.exec(select_cart).all()
    
    if not cart_items:
        raise HTTPException(
            status_code=404,
            detail="No cart items found for this cart"
        )
    
    return cart_items

async def create_cart(
    session: DATABASE_SESSION,
    create_cart: CartCreate,
    user_id: UUID = Depends(userId_from_token)
) -> Cart:
    # Check if a cart already exists for the user
    cart_check = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if cart_check:
        print("Cart already exists", cart_check.items)

    # Use existing cart if found, otherwise create a new one
    if cart_check and cart_check.id:
        cart_in_db = cart_check
        cart_id = cart_check.id
    else:
        cart_id = uuid4()
        cart_in_db = Cart(id=cart_id, user_id=user_id)
        session.add(cart_in_db)

    total_amount = 0.0
    # Add items to cart
    for item in create_cart.items:
        db_item = CartItem(
            cart_id=cart_id,
            # user_id=user_id,
            product_id=item.product_id,
            product_name=item.product_name,
            product_description=item.product_description,
            quantity=item.quantity,
            price=item.price,
        )
        total_amount += item.price * item.quantity
        session.add(db_item)

    cart_in_db.total_amount = round(total_amount, 2)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating Cart: {e}")

    # Refresh cart after commit to get updated values
    session.refresh(cart_in_db)
    return cart_in_db



async def update_cart(
    session: DATABASE_SESSION, 
    cart_request: CartRequest, 
    cart_update: CartUpdate
) -> Cart:
    # Fetch the existing cart based on the provided cart_id
    db_cart = session.exec(select(Cart).where(Cart.id == cart_request.cart_id)).first()
    if not db_cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    if cart_update.items and db_cart.items:
        # Extract current items by product_id
        existing_items = {item.product_id: item for item in db_cart.items}
        total_amount = 0.0
        
        for item in cart_update.items:
            # Check if the item already exists
            if item.product_id in existing_items:
                # Update existing item
                db_item = existing_items.pop(item.product_id)
                for key, value in item.model_dump(exclude_unset=True).items():
                    setattr(db_item, key, value)
                session.add(db_item)
                total_amount += db_item.price * db_item.quantity

    # Update the total amount of the cart
    db_cart.total_amount = round(total_amount, 2)
    
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating Cart: {e}")

    session.refresh(db_cart)
    return db_cart    