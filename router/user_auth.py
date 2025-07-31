from fastapi import APIRouter, Form
from datetime import timedelta
from typing import Union
from model.user import UserPageResponse, User, TokenRepsonse, BaseResponse, UserResponse, ValidResponse
from utils.token_utils import create_access_token, decode_token
from math import ceil
from database.mongo_manager import database

userauth_route = APIRouter(prefix="/user_auth")
user_collection = database['users']

@userauth_route.get('/health', tags=["User Authentication"])
async def health():
    return {
        'status': 'ok'
    }
    
@userauth_route.post("/login", response_model=TokenRepsonse, tags=["User Authentication"])
async def regen_token(
    email:str=Form(...), 
    password:str=Form(...)
):
    user = await user_collection.find_one({'email': email, 'password': password})
    if user is not None:
        access_token_expires = timedelta(minutes=3000)
        access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
        await user_collection.update_one({'_id': user['_id']}, { "$set": { "token": access_token } })
        user['user_id'] = str(user['_id'])
        del user['_id']
        
        return TokenRepsonse(message="Login Success", token=access_token, data=user)
    else:
        return BaseResponse(status=400, message="No Such User")       

@userauth_route.post("/register", tags=["User Authentication"], response_model=Union[TokenRepsonse, BaseResponse])
async def register_user(
    email:str=Form(...), username:str=Form(...), password:str=Form(...)
):
    user = User(
        email=email, username=username, password=password, token=""
    )
    cursor = user_collection.find({'email': email})
    length = len([document for document in await cursor.to_list(length=100)])
    if length <= 0:
        access_token_expires = timedelta(minutes=3000)
        access_token = create_access_token(data={"sub": user.dict()["username"]}, expires_delta=access_token_expires)
        user.token = access_token
        
        await user_collection.insert_one(user.dict())
        return TokenRepsonse(status=200, message="User Registered", token=access_token, data=user)
    else:
        return BaseResponse(status=400, message="Duplicate User")
    
@userauth_route.post("/token_valid", tags=["User Authentication"], response_model=ValidResponse)
async def validate_token(token:str=Form(...)):
    payload = decode_token(token)
    return ValidResponse(message="You are authorized!", username=payload['sub'])