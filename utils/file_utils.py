from PIL import Image
import asyncio
from pdf2image import convert_from_bytes
from fastapi import UploadFile, File
from typing import List
from model.doc import Page, Document
from pdf2image import convert_from_bytes
import io
import mimetypes
import base64
import json
import os

def encode_image(image: Image.Image, quality: int = 80, format: str = "WEBP") -> str:
    buf = io.BytesIO()
    if format == "JPEG" and image.mode in ("RGBA", "LA", "P"):
        image = image.convert("RGB")
    image.save(buf, format=format, quality=quality, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

async def handle_document(files:List[UploadFile]):
    documents = []
    image_pages = []
    
    for file in files:
        content = await file.read()
        file_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
    
        try:
            if "pdf" in file_type:
                images = await asyncio.to_thread(convert_from_bytes, content, dpi=150, thread_count=2, use_pdftocairo=True)

                tasks = [
                    asyncio.to_thread(lambda i=i, img=img: Page(
                        page_number=i+1, page=encode_image(img, format='JPEG'), 
                        page_name=os.path.basename(img.filename)
                    ))
                    for i, img in enumerate(images)
                ]
                pages = await asyncio.gather(*tasks)
                documents.append(Document(
                    file_name=file.filename,
                    pages=pages,
                    total_pages=len(pages), doc_type='pdf'
                ))
            else:
                image_pages.append(Page(
                    page_number=len(image_pages) + 1, page=base64.b64encode(content),
                    page_name=file.filename
                ))
        except Exception as e:
            raise ValueError(f"Failed to parse file {file.filename}: {e}")
    
    if image_pages:
        documents.append(Document(
            file_name=file.filename,
            pages=image_pages,
            total_pages=len(image_pages), 
            doc_type='img'
        ))
    return documents

async def process_documents(documents: List[UploadFile], schema_str: str=None):
    # Parse the schema JSON string
    try:
        documents = await handle_document(documents)
        images = []
        for doc in documents:
            for page in doc.pages:
                images.append(page.page)
        
        if schema_str:
            schema = json.loads(schema_str)
            return documents, images, schema
        else:
            return documents, images, None
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in schema_path: {e}")
        # return await get_files(schema_str, documents)
    except Exception as e:
        raise RuntimeError(f"File processing failed: {e}")
    
    