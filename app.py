from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values

from router.engine import engine_route
from router.user_auth import userauth_route

config = dotenv_values("deployment/deploy.env")
origins = [
    "http://localhost",
    "http://localhost:5000",
    "http://localhost:6000",
    "http://192.168.68.120:1000",
    "*"
]
tags_metadata = [
    {"name": "Engine", "description": "Calling the LLM Engine"},
    {"name": "User Authentication", "description": "User Credential and Authentication"},
    {"name": "Health Check", "description": "Health Check API"}
]

app = FastAPI(openapi_tags=tags_metadata)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(engine_route)
app.include_router(userauth_route)

@app.get('/health', tags=['Health Check'])
async def health():
    return {
        'status': 'ok'
    }
