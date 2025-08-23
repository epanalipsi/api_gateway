from fastapi import APIRouter, File, UploadFile, Depends, Form
from auth.auth_bearer import JWTBearer
from database.mongo_manager import database
from model.doc import DocResponse, Document
from typing import List

doc_route = APIRouter(prefix="/doc")
doc_collection = database['document']

@doc_route.get('/health', tags=["Documents"])
async def health():
    return {
        'status': 'ok'
    }
    
@doc_route.post('/insert', dependencies=[Depends(JWTBearer())], tags=['Documents'])
async def insert_doc(
    documents: List[UploadFile] = File(...),
):
    insert_docs = []
    for doc in documents:
        await doc.read()
        document = Document(
            file_name=doc.filename
        )
        insert_docs.append(document)
        print(document)
    