from model import BaseModel, BaseResponse
from typing import List, Optional
from model.engine import LLMResponse
from datetime import datetime
import uuid
from pydantic import Field

class Page(BaseModel):
    page_number:int

class Document(BaseModel):
    doc_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_name: str
    file_path: Optional[str] = None
    total_pages: int = 0
    created_date: datetime = Field(default_factory=datetime.utcnow)
    update_date: datetime = Field(default_factory=datetime.utcnow)
    pages:List[Page] = Field(default_factory=list)
    doc_type:str = None

class DocResponse(BaseResponse):
#     docs_inserted:Optional[int]=0
#     data:Optional[List[Document]]=[]
    total_page_response:int=0