from fastapi import Depends, HTTPException
from sqlmodel import select
from app.models.product_model import (
ProductBase,
ProductModel,
OrderItem,
ProductFormModel,
DeleteProduct,

) 
from typing import Annotated
from app.database.db import DATABASE_SESSION
from uuid import UUID, uuid4
from app.auth.user_auth import userId_from_token
from app.kafka.kafka import kafka_producer

product_topic = "product_topic"
async def get_all_products(session:DATABASE_SESSION):
    products = session.exec(select(ProductModel)).all
    if not products:
        raise HTTPException(
            status_code=404,
            detail="No Product found"
        )

def get_product_by_id(product_id:UUID, session:DATABASE_SESSION):
    product = session.get(ProductModel,product_id)
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

# async def create_product(product:ProductFormModel, session: DATABASE_SESSION, user_id:Annotated[UUID, Depends(userId_from_token),Depends(kafka_producer)] ):
#     product_id=uuid4()
#     product_db = ProductModel(
#         id=product_id,
#         user_id=user_id,
#         product_name=product.product_name,
#         product_description=product.product_description,
#         price=product.price,
#         stock=product.stock
#     )

#     session.add(product_db)
#     try:
#         session.commit()
#         session.refresh(product_db)
#         #TODO Kafka message here for product create
#     except Exception as error:
#         session.rollback()
#         raise HTTPException(
#             status_code=400,
#             detail=f"Error while creating product: {error}"
#         )    
#     session.refresh(product_db)
#     product_create_topic="create_product_topic"
#     kafka_producer(product_create_topic,product_db)
#     return product_db    

async def create_product(
    product: ProductFormModel, 
    session: DATABASE_SESSION,  # Use FastAPI's dependency injection for session
    user_id: Annotated[UUID, Depends(userId_from_token)]  # Extract user ID from token
):
    # Generate a new product UUID
    product_id = uuid4()

    # Create a new product instance
    product_db = ProductModel(
        id=product_id,
        user_id=user_id,
        product_name=product.product_name,
        product_description=product.product_description,
        price=product.price,
        stock=product.stock
    )

    # Add the product to the database session
    session.add(product_db)

    try:
        # Commit the transaction
        session.commit()
        session.refresh(product_db)

        

        # Send the product creation message to Kafka
        # message = {
        #     "action": "create",  # Specify action type
        #     "product": {
        #         "id": str(product_db.id),
        #         "user_id": str(product_db.user_id),
        #         "product_name": product_db.product_name,
        #         "product_description": product_db.product_description,
        #         "price": product_db.price,
        #         "stock": product_db.stock
        #     }
        # }
        message = {
        "action": "create",  # Specify action type
        "id": str(product_db.id),  # The product ID
        "user_id": str(product_db.user_id),  # The user who owns the product
        "product_name": product_db.product_name,  # Product name
        "product_description": product_db.product_description,  # Product description
        "price": product_db.price,  # Product price
        "stock": product_db.stock  # Product stock
    }


        # Call kafka_producer and await the result
        await kafka_producer(product_topic, message)

    except Exception as error:
        # Rollback the session in case of any error
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error while creating product: {error}"
        )
    
    # Return the created product
    return product_db



# def update_product(
#     product_id: UUID,
#     updated_product: ProductBase,
#     session: DATABASE_SESSION,
#     user_id: UUID = Depends(userId_from_token)
# ):
#     product_db = session.exec(
#         select(ProductModel).where(
#             ProductModel.id == product_id,
#             ProductModel.user_id == user_id
#         )
#     ).first()

#     # Product not found or not added by the user
#     if not product_db:
#         raise HTTPException(
#             status_code=404,
#             detail="Product not found or not added by the user"
#         )

#     # Perform the update
#     new_product_data = updated_product.model_dump(exclude_unset=True).items()
#     for key, value in new_product_data:
#         setattr(product_db, key, value)

#     session.add(product_db)
#     session.commit()
#     session.refresh(product_db)

#     return product_db


async def update_product(
    product_id: UUID,
    updated_product: ProductBase,  # Assuming ProductBase is the model for update
    session: DATABASE_SESSION,              # Session is injected via FastAPI dependency
    user_id: UUID = Depends(userId_from_token)  # Get the user_id from the token
):
    # Fetch the product from the database
    product_db = session.exec(
        select(ProductModel).where(
            ProductModel.id == product_id,
            ProductModel.user_id == user_id
        )
    ).first()

    # If product is not found or doesn't belong to the user, raise 404
    if not product_db:
        raise HTTPException(
            status_code=404,
            detail="Product not found or not added by the user"
        )

    # Perform the update by setting the new values on the product object
    new_product_data = updated_product.model_dump(exclude_unset=True).items()
    for key, value in new_product_data:
        setattr(product_db, key, value)

    # Save the updated product to the session and commit
    session.add(product_db)
    session.commit()
    session.refresh(product_db)

   

    # Prepare message for Kafka
    message = {
    "action": "update",  # Specify the action type
    "product_id": str(product_db.id),  # The product ID
    "user_id": str(product_db.user_id),  # The user who owns the product
    "updated_fields": {key: value for key, value in new_product_data}  # Only send the updated fields
    }

    # Send Kafka message (async call)
    try:
        await kafka_producer(product_topic, message)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send Kafka update message: {str(e)}"
        )

    # Return the updated product
    return product_db




def delete_product(
    delete_product:DeleteProduct,
    session:DATABASE_SESSION,
    user_id:UUID=Depends(userId_from_token)
):
    product = session.exec(
        select(ProductModel).where(
            ProductModel.id == delete_product.product_id,
            user_id == user_id
        )
    ).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Error no product found"
        ) 
    session.delete(product)
    session.commit() 
    return {"message":f"Product deleted having id  {delete_product.product_id} successfuly."}      
# Adding kafka



