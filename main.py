from typing import Optional
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import db

# Import all routes
from routes import user

tags_metadata = [
    {
        'name': 'users',
        'description': 'Operations with users table.'
    }
]
server = FastAPI(
    title="FRA641Rest",
    description="RESTful API written in FastAPI for used as a backend for community project in FRA641 subject.",
    version="0.0.1-alpha",
    openapi_tags=tags_metadata
)
# server.mount('/images', StaticFiles(directory='static/images'), name='images')

@server.get('/')
def get_root():
    return {"Hello": "HelloWorld"}

@server.on_event('startup')
async def startup():
    await db.connect()

@server.on_event('shutdown')
async def shutdown():
    await db.disconnect()

user.export_routes('/users', server, db)
