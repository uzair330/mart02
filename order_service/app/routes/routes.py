from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
# from app.models.product_model import ProductModel,ProductFormModel
from uuid import uuid4, UUID

from app.database.db import DATABASE_SESSION
from app.crud.crud import (
    get_carts,
    create_cart
    ,update_cart,
    get_cartitems
)
from sqlmodel import select

from app.models.cart_model import CartWithItems,Cart,CartUpdate

router = APIRouter()

@router.get("/get_cart", response_model=Cart)
def get_cart(cart: Annotated[Cart, Depends(get_carts)]):
    return cart


@router.get("/get_cart_items/")
async def get_cart_items(cart_id: str, session: DATABASE_SESSION):
    cart_id_uuid = UUID(cart_id)  # Convert the string to UUID
    return await get_cartitems(session, cart_id_uuid)


@router.post("/create_cart", response_model=Cart)
async def create_cart(cart_items: Annotated[Cart, Depends(create_cart)]):
    return cart_items


@router.put("/update_cart", response_model=CartWithItems)
def update_cart(
    updated_cart: Annotated[CartUpdate, Depends(update_cart)],
):
    return updated_cart
