from fastapi import Depends, HTTPException
from sqlmodel import select
from app.models.inventory_model import InventoryModel 
from typing import Annotated
from app.database.db import DATABASE_SESSION
from uuid import UUID, uuid4
from app.auth.user_auth import userId_from_token




def get_product_by_id(product_id:UUID, session:DATABASE_SESSION):
    product = session.get(InventoryModel,product_id)
    if not product:
        raise HTTPException(
        status_code=404,
        detail="Product Not Found"
    )  
    product_dict = {
        "id": product.id,
        "product_name": product.product_name,
        "product_description": product.product_description,
        "price":product.price,
        "stock":product.stock
        }      
    return product_dict    
