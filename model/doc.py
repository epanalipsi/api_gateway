from model import BaseModel, BaseResponse
from typing import List, Optional
from datetime import datetime
import uuid
from pydantic import Field

class Page(BaseModel):
    page_number:int
    page:str
    page_name:str

class Document(BaseModel):
    doc_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_name: str = Field(default_factory=lambda: f"document_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jpg")
    file_path: Optional[str] = None
    total_pages: int = 0
    created_date: datetime = Field(default_factory=datetime.utcnow)
    update_date: datetime = Field(default_factory=datetime.utcnow)
    pages:List[Page] = Field(default_factory=list)
    doc_type:str = ""
    llm_job_id:str = ""
    
class DocResponse(BaseResponse):
    data:Optional[List[Document]] = []
    total_page_response:Optional[int]=0