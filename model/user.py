from model import BaseResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict
from datetime import datetime

class User(BaseModel):
    user_id:str=""
    username:str=""
    email:str=""
    role:str="user"
    password:str=""
    is_admin:bool=False
    upload_limit:int=30
    token:str=""
    update_date:datetime=datetime.now()
    created_date:datetime=datetime.now()
    
class UserPageResponse(BaseResponse):
    data:List[User]=[]
    total_pages:int=0
    
class UserResponse(BaseResponse):
    data:Union[Dict, User]={}
        
class TokenRepsonse(BaseResponse):
    token:str=""
    token_upload_limit:int
    token_expiry_date:str
    data:Optional[User]=None

class ValidResponse(BaseResponse):
    username:str=""