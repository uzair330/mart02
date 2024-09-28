from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from app.models.product_model import ProductModel,ProductFormModel
from app.database.db import DATABASE_SESSION
from app.crud.crud import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product
)
from sqlmodel import select

router = APIRouter()



@router.get("/products", response_model=list[ProductFormModel])
async def get_all_products(session: DATABASE_SESSION):
    products = session.exec(select(ProductModel)).all()
    if not products:
        raise HTTPException(status_code=404, detail="No Products found")
    
    return products

@router.get("/get_product_by_id",response_model=ProductFormModel)
def getting_product(product:Annotated[ProductModel,Depends(get_product_by_id)]):
    return product

@router.post("/create_product",response_model=ProductFormModel)
async def adding_product(product:Annotated[ProductModel,Depends(create_product)]):
    return product

@router.put("/update_product")
def update_product(
    updated_product: Annotated[ProductModel, Depends(update_product)],
):
    return updated_product


@router.delete("/delete_product")
def delete_product(delete_product:Annotated[str,Depends(delete_product)]):
    return delete_product