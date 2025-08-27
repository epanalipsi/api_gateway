from fastapi import APIRouter, File, UploadFile, Depends, Form, Body
from auth.auth_bearer import JWTBearer
from database.mongo_manager import database
from model.doc import DocResponse, BaseResponse, Document
from typing import List
from utils.file_utils import handle_document
from math import ceil

doc_route = APIRouter(prefix="/doc")
doc_collection = database['document']

@doc_route.get('/health', tags=["Documents"])
async def health():
    return {
        'status': 'ok'
    }
    
@doc_route.post('/insert', dependencies=[Depends(JWTBearer())], tags=['Documents'])
async def insert_doc(
    files: List[UploadFile] = File(...),
):
    documents = await handle_document(files)
    documents = [doc.model_dump() for doc in documents]
    result = await doc_collection.insert_many(documents)
    
    return {
        "status": 200, 'message': 'ok', 
        'docs_inserted': len(result.inserted_ids)
    }
    
@doc_route.post('/list', dependencies=[Depends(JWTBearer())], tags=['Documents'])
async def list_doc(page:int=Form(...), page_size:int=Form(...)):
    skip = (page - 1) * page_size

    # Faster count (approximate, but very fast)
    total_items = await doc_collection.estimated_document_count()
    total_pages = int(ceil(float(total_items) / float(page_size)))

    cursor = doc_collection.find({}).sort(
        [("updated_date", -1), ("created_date", -1)]
    ).skip(skip).limit(page_size)
    results = await cursor.to_list(length=None)
    
    return DocResponse(message="success", total_page_response=total_pages, data=results)

@doc_route.post("/update", dependencies=[Depends(JWTBearer())], tags=['Documents'])
async def update_doc(doc_req:Document):
    result = await doc_collection.update_one(
        {"doc_id": doc_req.doc_id},  # or {"doc_id": req.doc_id} if using string IDs
        {"$set": doc_req.model_dump()}
    )
    
    # Fetch the updated document
    updated_doc = await doc_collection.find_one({"doc_id": doc_req.doc_id})
    return DocResponse(message="success", data=[updated_doc]).model_dump(exclude={"total_page_response"})
    
@doc_route.post("/delete", dependencies=[Depends(JWTBearer())], tags=['Documents'])
async def delete_doc(doc_id:str=Form(...)):
    result = await doc_collection.delete_one({"doc_id": doc_id})
    if result.deleted_count > 0:
        message = "Doc Deleted"
    else:
        message = "No Doc Found"
    return BaseResponse(message=message)
