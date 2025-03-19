from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncpg
import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
django.setup()

from django.contrib.auth.models import User

app = FastAPI()

# PostgreSQL connection settings
DATABASE_URL = "postgresql://user:password@localhost:5432/yourdbname"

# Create a connection pool
async def connect_db():
    return await asyncpg.create_pool(DATABASE_URL)

db_pool = None

@app.on_event("startup")
async def startup():
    global db_pool
    db_pool = await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await db_pool.close()

# Request model
class UserCheckRequest(BaseModel):
    username: str
    email: str

@app.post("/check-user/")
async def check_user(request: UserCheckRequest):
    async with db_pool.acquire() as conn:
        username_exists = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM auth_user WHERE username=$1)", 
            request.username
        )
        email_exists = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM auth_user WHERE email=$1)", 
            request.email
        )

    return {"username_exists": username_exists, "email_exists": email_exists}

