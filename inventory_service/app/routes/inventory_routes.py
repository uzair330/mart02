# from typing import Annotated
# from fastapi import APIRouter, Depends, HTTPException
# from app.models.product_model import InventoryModel
# from app.database.db import DATABASE_SESSION
# from app.crud.crud import get_product_by_id
    

# from sqlmodel import select

# router = APIRouter()



# @router.get("/get_inventory_by_id",response_model=InventoryModel)
# def getting_product(inventory:Annotated[InventoryModel,Depends(get_product_by_id)]):
#     return inventory


from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException
from app.models.inventory_model import InventoryModel
from app.database.db import DATABASE_SESSION
from app.crud.crud import get_product_by_id
from sqlmodel import select

router = APIRouter()

# @router.get("/get_inventory_by_id/{product_id}", response_model=InventoryModel)
# async def getting_product(product_id: str, session: DATABASE_SESSION = Depends(get_product_by_id)):
#     # Check if the inventory exists for the given product ID
#     inventory = session.exec(select(InventoryModel).where(InventoryModel.product_id == product_id)).first()
#     if not inventory:
#         raise HTTPException(status_code=404, detail="Inventory not found")
#     return inventory

# @router.get("/get_all_inventory", response_model=List[InventoryModel])
# async def get_all_inventory(session: DATABASE_SESSION = Depends(get_product_by_id)):
#     # Retrieve all inventory records
#     inventories = session.exec(select(InventoryModel)).all()
#     return inventories
