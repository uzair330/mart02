# from typing import Annotated,List
# from fastapi import APIRouter, Depends, HTTPException 
# from app.models.user_model import User
# from app.crud.crud import user_login, creating_user, getting_user_by_Id, update_user, delete_user,get_all_users


# router=APIRouter()




# @router.get("/get_all_users", response_model=List[User],tags=[Users])
# def get_users(users: Annotated[list[User], Depends(get_all_users)]):
#     return users


# @router.post("/login",tags=[Signup & Login])
# async def login_user(login:Annotated[dict,Depends(user_login)]):
#     if not login:
#         HTTPException(
#             status_code = 400,
#             detail="Try again, Unable to Login"
#         )
#     return {"access_token":login}


# @router.get("/current_user",tags=[Users])
# def get_current_user(user: Annotated[User,Depends(getting_user_by_Id)]):
#     return user


# @router.post("/create_user",tags=[Signup & Login])
# async def add_user(token: Annotated[dict, Depends(creating_user)]):
#     if not token:
#         HTTPException(
#             status_code=400,
#             detail="Access token generating fails"
#         )    
#     return token    


# @router.put("/update_user",tags=[Update & Delete])
# def update_user(user:Annotated[User,Depends(update_user)]):
#     if not user:
#         HTTPException(
#             status_code=400,
#             detail = "Fail to update user"
#         )
#     return user


# @router.delete("/delete_user",tags=[Update & Delete])
# def update_user(delete_msg:Annotated[User,Depends(delete_user)]):
#     if not delete_msg:
#         HTTPException(
#             status_code=400,
#             detail = "Fail to delete user"
#         )
#     return delete_msg

from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from app.models.user_model import User
from app.crud.crud import user_login, creating_user, getting_user_by_Id, update_user, delete_user, get_all_users


router = APIRouter()


@router.get("/get_all_users", response_model=List[User], tags=["User Management"])
def get_users(users: Annotated[list[User], Depends(get_all_users)]):
    return users


@router.post("/login", tags=["Authentication"])
async def login_user(login: Annotated[dict, Depends(user_login)]):
    if not login:
        raise HTTPException(
            status_code=400,
            detail="Try again, Unable to Login"
        )
    return {"access_token": login}


@router.get("/current_user", tags=["User Management"])
def get_current_user(user: Annotated[User, Depends(getting_user_by_Id)]):
    return user


@router.post("/create_user", tags=["Authentication"])
async def add_user(token: Annotated[dict, Depends(creating_user)]):
    if not token:
        raise HTTPException(
            status_code=400,
            detail="Access token generating fails"
        )
    return token


@router.put("/update_user", tags=["User Updates"])
def update_user(user: Annotated[User, Depends(update_user)]):
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Fail to update user"
        )
    return user


@router.delete("/delete_user", tags=["User Updates"])
def delete_user(delete_msg: Annotated[User, Depends(delete_user)]):
    if not delete_msg:
        raise HTTPException(
            status_code=400,
            detail="Fail to delete user"
        )
    return delete_msg