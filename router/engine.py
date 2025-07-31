from fastapi import APIRouter, Form, Depends, Request, UploadFile, File, HTTPException
from auth.auth_bearer import JWTBearer
from typing import List
import os
from utils.api_utils import poll_jobs, submit_jobs, get_files
from model.engine import LLMResponse
from database.mongo_manager import database

from functools import lru_cache

async def extract_token(request: Request) -> str:
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return auth_header.split(" ", 1)[1]

async def check_and_decrement_user_limit(token: str):
    user = await user_collection.find_one_and_update(
        {"token": token, "upload_limit": {"$gt": 0}},
        {"$inc": {"upload_limit": -1}},
        return_document=True,
        projection={"upload_limit": 1, "_id": 1}
    )
    if not user:
        raise HTTPException(status_code=403, detail="User not found or limit exceeded")
    return user

async def rollback_user_limit(user_id):
    await user_collection.update_one(
        {"_id": user_id},
        {"$inc": {"upload_limit": 1}}
    )

async def process_documents(schema_str: str, documents: List[UploadFile]):
    try:
        return await get_files(schema_str, documents)
    except Exception as e:
        raise RuntimeError(f"File processing failed: {e}")

api_key = os.getenv('API_KEY', '')

endpoint_id = os.getenv('ENDPOINT_ID', "67awaqzdmoq3fn")
url_host = os.getenv("HOST", "https://api.runpod.ai/v2/")
# endpoint_id = os.getenv('ENDPOINT_ID', "")
# url_host = os.getenv("HOST", "http://localhost:8000/")

user_collection = database['users']
document_collection = database['document']

engine_route = APIRouter(prefix="/engine")

# Cache headers to avoid recreating them every time
@lru_cache(maxsize=1)
def get_api_headers():
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

# Cache URL to avoid string concatenation every time
@lru_cache(maxsize=2)
def get_api_url(mode: str = "runsync"):
    return f"{url_host}{endpoint_id}/{mode}"

@engine_route.get('/health', dependencies=[Depends(JWTBearer())], tags=["Engine"])
async def health():
    return {
        'status': 'ok'
    }
    
@engine_route.post('/status', dependencies=[Depends(JWTBearer())], tags=["Engine"])
async def get_status(job_id:str=Form(...)):
    try:
        res = await poll_jobs(
            [job_id], endpoint_id, api_key
        )
        res = res[0]
        return LLMResponse(message='success', job_id=res['id'], data=res['output']['data'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@engine_route.post("/struct_predict", dependencies=[Depends(JWTBearer())], tags=["Engine"])
async def struct_predict(
    request: Request,
    prompt: str = Form(...),
    system_prompt: str = Form(...),
    documents: List[UploadFile] = File(...),
    schema: str = Form(...),
    run_background:bool=Form(False)
):
    if not prompt.strip() or not system_prompt.strip():
        return LLMResponse(message='Prompt and system_prompt cannot be empty')

    if not documents:
        return LLMResponse(message='At least one document is required')

    try:
        token = await extract_token(request)
        user = await check_and_decrement_user_limit(token)
        user_id = user["_id"]

        data = await process_documents(schema, documents)
        # Submit job
        job_input = {
            "input": {
                "images": data['images'],
                "job_type": 'struct_predict',
                "prompt": prompt,
                "system_prompt": system_prompt,
                "schema": data['schema']
            }
        }
    
        url = get_api_url('run' if run_background else 'runsync')
        results = await submit_jobs([job_input], url, get_api_headers(), api_key, background=run_background, is_complete=False)
        
        res = results[0]
        job_input['output'] = res['output']
        job_input['job_id'] = res['id']
        
        await document_collection.insert_one(job_input)
        if 'output' in res:
            data = res['output']['data']
        return LLMResponse(
            message='success', job_id=res['id'], data=data
        )
    except HTTPException as http_err:
        return LLMResponse(message=http_err.detail)

    except RuntimeError as file_err:
        await rollback_user_limit(user_id)
        return LLMResponse(message=str(file_err))

    except Exception as job_err:
        await rollback_user_limit(user_id)
        return LLMResponse(message=f"Job submission failed: {str(job_err)}")
    
@engine_route.post("/chat", dependencies=[Depends(JWTBearer())], tags=["Engine"])
async def chat(
    request: Request,
    prompt: str = Form(...),
    system_prompt: str = Form(...),
    documents: List[UploadFile] = File(...),
    run_background:bool=Form(False)
):
    if not prompt.strip() or not system_prompt.strip():
        return LLMResponse(message='Prompt and system_prompt cannot be empty')

    if not documents:
        return LLMResponse(message='At least one document is required')

    try:
        token = await extract_token(request)
        user = await check_and_decrement_user_limit(token)
        user_id = user["_id"]

        data = await process_documents(None, documents)
        job_input = {
            "input": {
                "images": data['images'],
                "job_type": 'chat',
                "prompt": prompt,
                "system_prompt": system_prompt,
            }
        }
        url = get_api_url('run' if run_background else 'runsync')
        results = await submit_jobs([job_input], url, get_api_headers(), api_key, background=run_background, is_complete=False)
        res = results[0]
        job_input['output'] = res['output']
        job_input['job_id'] = res['id']
        
        await document_collection.insert_one(job_input)
        if 'output' in res:
            data = res['output']['data']
        return LLMResponse(
            message='success', job_id=res['id'], data=data
        )
    except HTTPException as http_err:
        return LLMResponse(message=http_err.detail)

    except RuntimeError as file_err:
        await rollback_user_limit(user_id)
        return LLMResponse(message=str(file_err))

    except Exception as job_err:
        await rollback_user_limit(user_id)
        return LLMResponse(message=f"Job submission failed: {str(job_err)}")