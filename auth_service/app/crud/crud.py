from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from app.models.user_model import User, UserBase,UpdatingUser
from app.database.db import DATABASE_SESSION
from app.auth.user_auth import create_token,userId_from_token,password_verification,hashed_password

from app.settings import SECRET_KEY, TOKEN_EXPIRE_MINUTES

from uuid import UUID


def user_login(user_info:UserBase, session:DATABASE_SESSION):
    user = select(User).where(User.email==user_info.email)
    check_user=session.exec(user).one_or_none()
    if check_user is None:
        raise HTTPException(
            status_code=404,
            detail="Invalid Credentails"
        )

    pass_verify = password_verification(user_info.password,check_user.password)

    if not pass_verify:
        raise HTTPException(
            status_code=404,
            detail="Invalid Credentails"
        ) 
    token = create_token(check_user,TOKEN_EXPIRE_MINUTES)      
    return {"access_token":token} 


def get_all_users (session: DATABASE_SESSION):
    user = session.exec(
        select(User)).all()
    if not user:
        HTTPException(status_code=400,detail="No User in database")
    return user

def getting_user_by_Id(session:DATABASE_SESSION,   user_id:UUID = Depends(userId_from_token)):
    user = session.get(User,user_id)
    if user is None:
        HTTPException(status_code=400, detail="User not found")
    return user



async def add_user_in_database(user_form: User, session: Session):
    try:
        user = User.model_validate(
            user_form, update={"password": hashed_password(user_form.password)}
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return user

async def creating_user(user:UserBase, session:DATABASE_SESSION):
    check_user = select(User).where(User.email == user.email)
    user_exists = session.exec(check_user).one_or_none()
    if user_exists is not None:
        raise HTTPException (
            status_code = 404,
            detail = "Email Already exists try with another email or login"
        )    

    user_data = await add_user_in_database(user,session)    

    user_details = {
        "email":user_data.email,
        "username":user_data.username,
        "password":user.password
    }

    # login new register user
    token = user_login(user_info=UserBase(**user_details),session=session) 
    return token
    

def update_user(
    user_details:UpdatingUser,
    session:DATABASE_SESSION,
    user_id: UUID = Depends(userId_from_token)):

    check_userId = select(User).where(User.id == user_id)

    user = session.exec(check_userId).one_or_none()
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect User ID"
        )

    updating_user = user_details.model_dump(exclude_unset=True)
    for key, value in updating_user.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message":"user updated successfully"} 

def delete_user(session:DATABASE_SESSION, user_id:UUID = Depends(userId_from_token)):
    user = session.get(User,user_id)
    if user is None:
        raise HTTPException(
            status_code=400,
            detail="User not found"
            )

    session.delete(user)
    session.commit()
    message=f"User deleted successfully: Id= {user_id}"
    return message                   
