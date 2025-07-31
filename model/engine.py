from model import BaseModel, BaseResponse
from typing import Dict, Any, Union
from pydantic import Field

class LLMResponse(BaseResponse):
    job_id: str = Field(default="")
    data: Union[str, Dict[str, Any]] = Field(default_factory=dict)