# main.py
from typing import Optional, List
from enum import Enum
from fastapi import FastAPI, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pymongo import ReturnDocument


# --------------------------
# Helpers for ObjectId typing
# --------------------------
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            try:
                return ObjectId(v)
            except Exception:
                raise ValueError("Invalid objectid")
        raise ValueError("Not a valid ObjectId type")


# --------------------------
# Enums and Pydantic Models
# --------------------------
class TodoStatus(str, Enum):
    todo = "TODO"
    in_progress = "IN_PROGRESS"
    done = "DONE"


class TodoCreate(BaseModel):
    title: str = Field(..., example="Buy groceries")
    description: Optional[str] = Field(None, example="Milk, eggs, bread")
    status: TodoStatus = Field(TodoStatus.todo, example="TODO")


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, example="Buy groceries and fruits")
    description: Optional[str] = Field(None, example="Milk, eggs, apples")
    status: Optional[TodoStatus] = Field(None, example="IN_PROGRESS")


class TodoInDB(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    todo_id: str = Field(..., example="T001")
    title: str
    description: Optional[str] = None
    status: TodoStatus

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "_id": "64f8b9de7f1b4b6b9f1a1a1a",
                "todo_id": "T001",
                "title": "Buy groceries",
                "description": "Milk & eggs",
                "status": "TODO",
            }
        }


class TodoResponse(BaseModel):
    todo_id: str
    title: str
    description: Optional[str]
    status: TodoStatus


# --------------------------
# App and DB setup
# --------------------------
app = FastAPI(
    title="TODO API (FastAPI + MongoDB)",
    version="1.0",
    servers=[
        {"url": "http://localhost:8000", "description": "Local development server"}
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "todo_app_db"
TODOS_COLL = "todos"
COUNTERS_COLL = "counters"


@app.on_event("startup")
async def startup_db_client():
    app.state.mongo_client = AsyncIOMotorClient(MONGO_URI)
    app.state.db = app.state.mongo_client[DB_NAME]
    # Ensure counters doc exists
    await app.state.db[COUNTERS_COLL].update_one(
        {"_id": "todoid"}, {"$setOnInsert": {"seq": 0}}, upsert=True
    )


@app.on_event("shutdown")
async def shutdown_db_client():
    app.state.mongo_client.close()


def format_todo_doc(doc: dict) -> dict:
    """Format Mongo document for responses."""
    return {
        "todo_id": doc["todo_id"],
        "title": doc["title"],
        "description": doc.get("description"),
        "status": doc["status"],
    }


async def generate_todo_id(db) -> str:
    """
    Atomically increment counter and generate ID like T001, T002...
    Uses a counters collection with document _id='todoid' and field seq (int).
    """
    # Using pymongo ReturnDocument requires using the raw PyMongo object.
    # Motor's find_one_and_update accepts return_document from pymongo.
    updated = await db[COUNTERS_COLL].find_one_and_update(
        {"_id": "todoid"},
        {"$inc": {"seq": 1}},
        return_document=ReturnDocument.AFTER,
    )
    seq = updated["seq"]
    return f"T{seq:03d}"


# --------------------------
# API Endpoints
# --------------------------


@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(payload: TodoCreate):
    db = app.state.db
    todo_id = await generate_todo_id(db)
    doc = {
        "todo_id": todo_id,
        "title": payload.title,
        "description": payload.description,
        "status": payload.status.value,
    }
    res = await db[TODOS_COLL].insert_one(doc)
    created = await db[TODOS_COLL].find_one({"_id": res.inserted_id})
    return format_todo_doc(created)


@app.get("/todos", response_model=List[TodoResponse])
async def list_todos(
    skip: int = 0, limit: int = 50, status_filter: Optional[TodoStatus] = None
):
    db = app.state.db
    query = {}
    if status_filter:
        query["status"] = status_filter.value
    cursor = db[TODOS_COLL].find(query).skip(skip).limit(limit).sort("todo_id", 1)
    todos = []
    async for doc in cursor:
        todos.append(format_todo_doc(doc))
    return todos


@app.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: str):
    db = app.state.db
    doc = await db[TODOS_COLL].find_one({"todo_id": todo_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Todo not found")
    return format_todo_doc(doc)


@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: str, payload: TodoUpdate):
    db = app.state.db

    set_fields = {}
    if payload.title is not None:
        set_fields["title"] = payload.title
    if payload.description is not None:
        set_fields["description"] = payload.description
    if payload.status is not None:
        set_fields["status"] = payload.status.value

    if not set_fields:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    updated = await db[TODOS_COLL].find_one_and_update(
        {"todo_id": todo_id}, {"$set": set_fields}, return_document=ReturnDocument.AFTER
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Todo not found")
    return format_todo_doc(updated)
